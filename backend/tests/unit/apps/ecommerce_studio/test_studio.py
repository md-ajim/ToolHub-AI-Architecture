import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
import datetime
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.subscriptions.models import Plan, PlanPrice, Subscription, SubscriptionStatus, BillingInterval, CreditType
from apps.subscriptions.services import CreditService
from apps.ai_tools.registry import is_known_operation, OPERATION_REGISTRY
from apps.ai_tools.models import AIProcessingJob
from apps.ecommerce_studio.models import MarketplacePreset, StudioSession

User = get_user_model()


def _png(content_color=(120, 160, 200, 255), size=(300, 300)):
    from PIL import Image as PILImage
    buf = io.BytesIO()
    PILImage.new("RGBA", size, content_color).save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile("product.png", buf.read(), content_type="image/png")


def _pro_features():
    # Feature keys in plans use underscores (e.g. ``ai_generative_fill``) while
    # OPERATION_REGISTRY keys use dashes; mirror the registry so paid plans match
    # enqueue_ai_job's feature gate exactly.
    feats = {
        OPERATION_REGISTRY[op].get("feature", f"ai_{op}"): True
        for op in OPERATION_REGISTRY
    }
    feats.update({
        "ai_access": True, "bulk_processing": True, "high_resolution_export": True,
        "cloud_history": True, "basic_tools": True, "brand_kit": True,
        "team_features": True, "api_access": True,
    })
    return feats


class EcommerceStudioBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="seller@example.com", password="pw")
        self.plan = Plan.objects.create(
            code="testpro", name="Test Pro", storage_limit=500 * 1024 * 1024,
            daily_limit=-1, batch_limit=20, api_limit=500, features=_pro_features(),
        )
        PlanPrice.objects.create(plan=self.plan, billing_interval=BillingInterval.MONTHLY, amount=999)
        Subscription.objects.create(
            user=self.user, plan=self.plan, status=SubscriptionStatus.ACTIVE,
            provider="stripe", expires_at=timezone.now() + datetime.timedelta(days=30),
        )
        CreditService.add_allocation(self.user, 5000, "seed", CreditType.AI)
        call_command("seed_marketplace_presets")

    def _auth(self):
        self.client.force_authenticate(self.user)


class AuthAndGatingTests(EcommerceStudioBase):
    def test_unauthenticated_preset_list_blocked(self):
        resp = self.client.get("/api/v1/studio/presets/")
        self.assertIn(resp.status_code, (401, 403))

    def test_authenticated_preset_list_returns_system_presets(self):
        self._auth()
        resp = self.client.get("/api/v1/studio/presets/")
        self.assertEqual(resp.status_code, 200)
        codes = [p["code"] for p in resp.json()["data"]]
        self.assertIn("amazon-main", codes)
        self.assertIn("instagram-post", codes)

    def test_unknown_operation_rejected(self):
        self._auth()
        resp = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "not-real"}, format="multipart")
        self.assertEqual(resp.status_code, 422)

    def test_known_operation_registry(self):
        self.assertTrue(is_known_operation("shadow"))
        self.assertFalse(is_known_operation("nope"))


class JobLifecycleTests(EcommerceStudioBase):
    def test_operation_runs_and_completes(self):
        self._auth()
        resp = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "shadow"}, format="multipart")
        self.assertEqual(resp.status_code, 202, resp.json())
        job_id = resp.json()["data"]["job_id"]
        job = AIProcessingJob.objects.get(id=job_id)
        # CELERY_TASK_ALWAYS_EAGER runs the task synchronously.
        self.assertEqual(job.status, AIProcessingJob.Status.COMPLETED)
        self.assertIsNotNone(job.output_file)
        self.assertGreater(job.consumed_credits, 0)

    def test_idempotency_key_reuses_job(self):
        self._auth()
        key = "idem-123"
        r1 = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "enhance", "idempotency_key": key}, format="multipart")
        r2 = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "enhance", "idempotency_key": key}, format="multipart")
        self.assertEqual(r1.json()["data"]["job_id"], r2.json()["data"]["job_id"])

    def test_parameters_passed_to_job(self):
        self._auth()
        resp = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "recolor", "parameters": '{"color": "#00ff00", "strength": 0.7}'}, format="multipart")
        job = AIProcessingJob.objects.get(id=resp.json()["data"]["job_id"])
        self.assertEqual(job.parameters.get("color"), "#00ff00")

    def test_batch_creates_child_jobs(self):
        self._auth()
        resp = self.client.post("/api/v1/ai/batch/", {"tool_name": "background-remove", "images": [_png(), _png(), _png()]}, format="multipart")
        self.assertEqual(resp.status_code, 202)
        batch_id = resp.json()["data"]["id"]
        batch = AIProcessingJob.objects.filter(batch__id=batch_id).count()
        self.assertEqual(batch, 3)


class CreditAndOwnershipTests(EcommerceStudioBase):
    def test_insufficient_credits_returns_402(self):
        self._auth()
        wallet = CreditService.get_wallet(self.user)
        wallet.ai_credits = 0
        wallet.save()
        resp = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "shadow"}, format="multipart")
        self.assertEqual(resp.status_code, 402)

    def test_cannot_access_other_users_session(self):
        self._auth()
        other = User.objects.create_user(email="other@example.com", password="pw")
        s = StudioSession.objects.create(user=other, source_image=_png(), status="draft")
        resp = self.client.get(f"/api/v1/studio/sessions/{s.id}/")
        self.assertIn(resp.status_code, (403, 404))


class PresetAndPreviewTests(EcommerceStudioBase):
    def test_custom_preset_create(self):
        self._auth()
        resp = self.client.post("/api/v1/studio/presets/", {
            "code": "custom-pro", "platform": "custom", "name": "My Custom", "width": 1200,
            "height": 1200, "aspect_ratio": "1:1", "format": "png", "quality": 95,
            "fit": "contain", "padding_px": 40, "background": "transparent",
            "export_naming_template": "{product}.png",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(MarketplacePreset.objects.filter(code="custom-pro", user=self.user).exists())

    def test_preset_preview_returns_image(self):
        self._auth()
        resp = self.client.post("/api/v1/studio/presets/amazon-main/preview/", {"image": _png()}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(resp["Content-Type"], ("image/jpg", "image/jpeg", "image/png", "image/webp"))


class SavedWorkflowTests(EcommerceStudioBase):
    def test_create_and_run_workflow(self):
        self._auth()
        steps = [{"step_key": "bg", "operation": "background-remove", "params": {}},
                 {"step_key": "enh", "operation": "enhance", "params": {}}]
        resp = self.client.post("/api/v1/studio/workflows/", {"name": "Amazon White", "steps": steps, "visibility": "private"}, format="json")
        self.assertEqual(resp.status_code, 201)
        wf_id = resp.json()["data"]["id"]
        run = self.client.post(f"/api/v1/studio/workflows/{wf_id}/run/", {"image": _png(), "name": "run1"}, format="multipart")
        self.assertEqual(run.status_code, 202)
        session_id = run.json()["data"]["id"]
        session = StudioSession.objects.get(id=session_id)
        self.assertEqual(session.step_records.count(), 2)
        # advance both steps
        for _ in range(3):
            session.refresh_from_db()
            if session.status == "completed":
                break
            self.client.post(f"/api/v1/studio/sessions/{session.id}/continue/")
        session.refresh_from_db()
        self.assertEqual(session.status, "completed")
        self.assertIsNotNone(session.current_image)


class BrandKitTests(EcommerceStudioBase):
    def test_brand_kit_requires_business_feature(self):
        # Current plan has brand_kit feature -> allowed
        self._auth()
        resp = self.client.post("/api/v1/studio/brand-kits/", {"name": "Kit"})
        self.assertEqual(resp.status_code, 201)


class StudioSessionTests(EcommerceStudioBase):
    def test_create_session_runs_pipeline_to_completion(self):
        self._auth()
        resp = self.client.post("/api/v1/studio/sessions/create/", {"source_image": _png(), "name": "Studio"}, format="multipart")
        self.assertEqual(resp.status_code, 202)
        session_id = resp.json()["data"]["id"]
        for _ in range(15):
            session = StudioSession.objects.get(id=session_id)
            if session.status in ("completed", "failed"):
                break
            self.client.post(f"/api/v1/studio/sessions/{session.id}/continue/")
        session.refresh_from_db()
        self.assertEqual(session.status, "completed", session.error_message)
        self.assertIsNotNone(session.current_image)
        completed = session.step_records.filter(status="completed").count()
        self.assertGreater(completed, 0)

    def test_studio_export_creates_record(self):
        self._auth()
        resp = self.client.post("/api/v1/studio/sessions/create/", {"source_image": _png(), "name": "Studio"}, format="multipart")
        session_id = resp.json()["data"]["id"]
        for _ in range(15):
            session = StudioSession.objects.get(id=session_id)
            if session.status == "completed":
                break
            self.client.post(f"/api/v1/studio/sessions/{session.id}/continue/")
        session.refresh_from_db()
        export = self.client.post(f"/api/v1/studio/sessions/{session_id}/export/", {"format": "png", "quality": 92, "name": "final"}, format="json")
        self.assertEqual(export.status_code, 201)
        self.assertIn("file_url", export.json()["data"])


class ExportTests(EcommerceStudioBase):
    def test_single_export_from_job(self):
        self._auth()
        op = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "background-remove"}, format="multipart")
        job_id = op.json()["data"]["job_id"]
        resp = self.client.post("/api/v1/studio/export/", {"job_id": job_id, "format": "png", "quality": 90, "name": "exp"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIsNotNone(resp.json()["data"]["file_url"])

    def test_batch_zip_export(self):
        self._auth()
        ids = []
        for _ in range(3):
            op = self.client.post("/api/v1/ai/operation/", {"image": _png(), "tool_name": "enhance"}, format="multipart")
            ids.append(op.json()["data"]["job_id"])
        resp = self.client.post("/api/v1/studio/export/batch/", {"job_ids": ids, "name": "batch"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()["data"]["is_zip"])
