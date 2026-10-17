"""Batch model selection tests: model_id passthrough + strict per-item validation."""

import io
import types

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def make_png(name="test.png") -> SimpleUploadedFile:
    img = Image.new("RGB", (64, 64), (100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@pytest.fixture
def qa_user(db):
    return get_user_model().objects.create_user(
        email="qa-batch@toolhub.local", password="password", is_qa_user=True
    )


@pytest.fixture
def ai_task_stub(monkeypatch):
    stub = types.SimpleNamespace(delay=lambda job_id: None, run=lambda job_id: None)
    monkeypatch.setattr("apps.ai_tools.tasks.process_ai_job", stub)
    monkeypatch.setattr("apps.ai_tools.tasks.process_comfyui_job", stub)
    return stub


@pytest.fixture
def relaxed_gate(settings):
    settings.AI_REQUIRE_LIVE_VERIFICATION = False


def post_batch(client, files, **data):
    payload = {"tool_name": "background-remove", **data}
    for f in files:
        payload.setdefault("images", []).append(f)
    # Build multipart manually: APIClient handles list values for files.
    return client.post("/api/v1/ai/batch/", payload, format="multipart")


class TestBatchModelSelection:
    def test_explicit_model_reaches_child_jobs(self, qa_user, ai_task_stub, relaxed_gate):
        client = APIClient()
        client.force_authenticate(qa_user)
        response = post_batch(client, [make_png()], model_id="local-rmbg-u2net")
        assert response.status_code == 202, response.data
        data = response.data["data"]
        assert len(data["job_ids"]) == 1
        assert data["failed_items"] == []

        from apps.ai_tools.models import AIProcessingJob

        job = AIProcessingJob.objects.get(id=data["job_ids"][0])
        assert job.model_id == "local-rmbg-u2net"
        assert job.provider == "local_rmbg"

    def test_mock_model_rejected_per_item(self, qa_user, ai_task_stub, relaxed_gate):
        client = APIClient()
        client.force_authenticate(qa_user)
        response = post_batch(client, [make_png()], model_id="mock-bg-remove")
        assert response.status_code == 202, response.data
        data = response.data["data"]
        assert data["job_ids"] == []
        assert len(data["failed_items"]) == 1
        assert "MISMATCH" in data["failed_items"][0]["error"]

    def test_auto_model_without_selection(self, qa_user, ai_task_stub, relaxed_gate):
        client = APIClient()
        client.force_authenticate(qa_user)
        response = post_batch(client, [make_png()])
        assert response.status_code == 202, response.data
        assert len(response.data["data"]["job_ids"]) == 1


@pytest.mark.django_db
class TestBatchAggregateHonesty:
    """Stored batch counters are write-once; the serializer must derive
    live values from child jobs so status/counts never contradict them."""

    def _batch(self, user):
        from apps.ai_tools.models import AIBatchJob

        return AIBatchJob.objects.create(
            user=user, tool_name="bg-remove", status="processing",
            total_count=2, completed_count=0, failed_count=0,
        )

    def _job(self, user, batch, status):
        import uuid

        from apps.ai_tools.models import AIProcessingJob

        return AIProcessingJob.objects.create(
            user=user, batch=batch, tool_name="bg-remove", status=status,
            idempotency_key=f"qa-agg-{uuid.uuid4().hex}",
        )

    def test_counts_and_status_derive_from_children(self, qa_user):
        from apps.ai_tools.serializers import AIBatchJobSerializer

        batch = self._batch(qa_user)
        self._job(qa_user, batch, "completed")
        self._job(qa_user, batch, "failed")
        data = AIBatchJobSerializer(batch).data
        assert data["completed_count"] == 1
        assert data["failed_count"] == 1
        assert data["status"] == "completed"

    def test_processing_while_active(self, qa_user):
        from apps.ai_tools.serializers import AIBatchJobSerializer

        batch = self._batch(qa_user)
        self._job(qa_user, batch, "completed")
        self._job(qa_user, batch, "processing")
        data = AIBatchJobSerializer(batch).data
        assert data["status"] == "processing"
        assert data["completed_count"] == 1

    def test_all_failed_reports_failed(self, qa_user):
        from apps.ai_tools.serializers import AIBatchJobSerializer

        batch = self._batch(qa_user)
        self._job(qa_user, batch, "failed")
        data = AIBatchJobSerializer(batch).data
        assert data["status"] == "failed"
        assert data["failed_count"] == 1

    def test_empty_batch_keeps_stored_status(self, qa_user):
        from apps.ai_tools.serializers import AIBatchJobSerializer

        batch = self._batch(qa_user)
        data = AIBatchJobSerializer(batch).data
        assert data["status"] == "processing"
        assert data["completed_count"] == 0


@pytest.mark.django_db
class TestWorkspaceHistoryRecording:
    def test_completed_job_writes_history(self, qa_user):
        from apps.ai_tools.models import AIProcessingJob
        from apps.ai_tools.tasks import _finalize_job_success
        from apps.workspace.models import History

        job = AIProcessingJob.objects.create(
            user=qa_user, tool_name="bg-remove", status="processing",
            idempotency_key="qa-hist-1",
        )
        assert _finalize_job_success(job.id) is True
        row = History.objects.get(user=qa_user)
        assert row.tool == "bg-remove"

    def test_terminal_job_writes_no_duplicate_history(self, qa_user):
        from apps.ai_tools.models import AIProcessingJob
        from apps.ai_tools.tasks import _finalize_job_success
        from apps.workspace.models import History

        job = AIProcessingJob.objects.create(
            user=qa_user, tool_name="bg-remove", status="completed",
            idempotency_key="qa-hist-2",
        )
        assert _finalize_job_success(job.id) is False
        assert History.objects.filter(user=qa_user).count() == 0
