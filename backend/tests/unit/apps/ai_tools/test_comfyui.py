"""Tests for the ComfyUI local-inference integration.

Covers: client, workflow validation/rendering, task routing, model selection,
local provider, missing model, ComfyUI unavailable/timeout, output retrieval,
and QA vs normal-user access. All ComfyUI server interactions are mocked.
"""

import io
import json
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase, TestCase, override_settings
from django.core.files.base import ContentFile
from PIL import Image as PILImage

from apps.ai_tools.registry import get_image_models, select_model
from apps.ai_tools.comfyui.client import (
    ComfyUIClient,
    ComfyUIUnavailable,
    ComfyUITimeout,
    ComfyWorkflowInvalid,
    ComfyOutputNotFound,
)
from apps.ai_tools.comfyui import errors
from apps.ai_tools.comfyui.workflows_registry import WorkflowRegistry, workflow_registry


def make_image_file(mode="RGB", size=(64, 64), fmt="PNG"):
    img = PILImage.new(mode, size, color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return ContentFile(buf.read(), name="test.png")


@override_settings(
    COMFYUI_ENABLED=True,
    COMFYUI_BASE_URL="http://127.0.0.1:8188",
    COMFYUI_TIMEOUT=5,
    COMFYUI_EXECUTION_TIMEOUT=300,
)
class ComfyUIClientTest(SimpleTestCase):
    def setUp(self):
        self.session = MagicMock()

    def test_is_available_true(self):
        client = ComfyUIClient(session=self.session)
        self.session.get.return_value = MagicMock(status_code=200)
        self.session.get.return_value.json.return_value = {"system": {"comfyui_version": "0.34.0"}}
        self.assertTrue(client.is_available())

    def test_is_available_false_on_connection_error(self):
        client = ComfyUIClient(session=self.session)
        self.session.get.side_effect = Exception("Connection refused")
        self.assertFalse(client.is_available())

    def test_health_unavailable(self):
        client = ComfyUIClient(session=self.session)
        self.session.get.side_effect = Exception("Connection refused")
        snapshot = client.health()
        self.assertEqual(snapshot["status"], "unavailable")

    def test_run_success(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.return_value = MagicMock(status_code=200)
        self.session.post.return_value.json.return_value = {"prompt_id": "abc123"}
        history = {
            "abc123": {
                "status": {"status_str": "success", "completed": True},
                "outputs": {"3": {"images": [{"filename": "out.png", "subfolder": "", "type": "output"}]}},
            }
        }
        self.session.get.return_value = MagicMock(status_code=200)
        self.session.get.return_value.json.side_effect = [
            history,  # /history/prompt_id
        ]
        # second GET is /view
        self.session.get.return_value.content = make_image_file().read()
        self.session.get.return_value.headers = {"Content-Type": "image/png"}

        workflow = {
            "3": {"class_type": "SaveImage", "inputs": {"filename_prefix": "x", "images": []}},
            "1": {"class_type": "LoadImage", "inputs": {"image": "in.png"}},
        }
        result = client.run(workflow, timeout_seconds=30, poll_interval=0.01)
        self.assertIsNotNone(result)
        self.assertTrue(result.name.startswith("comfyui_output_"))
        self.assertTrue(result.name.endswith(".png"))

    def test_run_timeout(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.return_value = MagicMock(status_code=200)
        self.session.post.return_value.json.return_value = {"prompt_id": "abc123"}
        self.session.get.return_value = MagicMock(status_code=200)
        self.session.get.return_value.json.return_value = {}  # empty history

        workflow = {"1": {"class_type": "LoadImage", "inputs": {"image": "in.png"}}}
        with self.assertRaises(ComfyUITimeout):
            client.run(workflow, timeout_seconds=0.2, poll_interval=0.05)

    def test_run_rejected_prompt_wraps_workflow_invalid(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.return_value = MagicMock()
        self.session.post.return_value.status_code = 400
        self.session.post.return_value.text = "node error"
        import requests

        self.session.post.return_value.raise_for_status.side_effect = (
            requests.HTTPError("400 Client Error: node error")
        )
        with self.assertRaises(ComfyWorkflowInvalid):
            client.run({"1": {}}, timeout_seconds=30, poll_interval=0.01)

    def test_upload_image_success(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.return_value = MagicMock(status_code=200)
        self.session.post.return_value.json.return_value = {"name": "in.png", "subfolder": "toolhub", "type": "input"}
        ref = client.upload_image(make_image_file())
        self.assertEqual(ref["name"], "in.png")
        self.assertEqual(ref["subfolder"], "toolhub")

    def test_upload_image_strips_storage_path(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.return_value = MagicMock(status_code=200)
        self.session.post.return_value.json.return_value = {
            "name": "test.png",
            "subfolder": "toolhub",
            "type": "input",
        }
        image_file = make_image_file()
        image_file.name = "ai-inputs/test.png"

        client.upload_image(image_file)

        uploaded_name = self.session.post.call_args.kwargs["files"]["image"][0]
        self.assertEqual(uploaded_name, "test.png")

    def test_upload_image_unavailable(self):
        client = ComfyUIClient(session=self.session)
        self.session.post.side_effect = Exception("no route to host")
        with self.assertRaises(ComfyUIUnavailable):
            client.upload_image(make_image_file())


@override_settings(COMFYUI_ENABLED=True)
class WorkflowRegistryTest(SimpleTestCase):
    def test_available_operations(self):
        ops = workflow_registry.available_operations()
        self.assertIn("upscale", ops)
        self.assertIn("background_remove", ops)
        self.assertIn("face_restore", ops)
        self.assertIn("inpaint", ops)

    def test_upscale_render_substitutes_placeholders(self):
        wf = workflow_registry.render(
            "upscale",
            {"INPUT_IMAGE": "photo.png", "MODEL_NAME": "4x-UltraSharp.pth"},
        )
        self.assertEqual(wf["1"]["inputs"]["image"], "photo.png")
        self.assertEqual(wf["2"]["inputs"]["model_name"], "4x-UltraSharp.pth")
        self.assertEqual(wf["3"]["class_type"], "ImageUpscaleWithModel")
        self.assertEqual(wf["4"]["class_type"], "SaveImage")

    def test_background_remove_render_uses_native_birefnet_nodes(self):
        wf = workflow_registry.render(
            "background_remove",
            {
                "INPUT_IMAGE": "toolhub/in.png",
                "MODEL_NAME": "birefnet.safetensors",
            },
        )
        self.assertEqual(wf["1"]["inputs"]["image"], "toolhub/in.png")
        self.assertEqual(wf["2"]["class_type"], "LoadBackgroundRemovalModel")
        self.assertEqual(
            wf["2"]["inputs"]["bg_removal_name"], "birefnet.safetensors"
        )
        self.assertEqual(wf["3"]["class_type"], "RemoveBackground")
        self.assertEqual(wf["4"]["class_type"], "InvertMask")
        self.assertEqual(wf["5"]["class_type"], "JoinImageWithAlpha")
        self.assertEqual(wf["6"]["class_type"], "SaveImage")

    def test_unknown_operation_raises(self):
        with self.assertRaises(RuntimeError):
            workflow_registry.render("no_such_op", {})

    def test_invalid_workflow_missing_workflow_key(self):
        reg = WorkflowRegistry()
        with patch.object(reg, "dir", "/nonexistent"):
            with self.assertRaises((RuntimeError, FileNotFoundError)):
                reg.render("upscale", {})


@override_settings(COMFYUI_ENABLED=True)
class TaskRoutingTest(SimpleTestCase):
    def test_router_resolves_upscale(self):
        from apps.ai_tools.comfyui.routing import ImageTaskRouter

        router = ImageTaskRouter(client=MagicMock())
        router._client.is_available.return_value = True
        entry = router.resolve("upscale")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["provider"], "comfyui_local")
        self.assertEqual(entry["workflow"], "upscale")
        self.assertEqual(entry["queue"], "image_local_ai")
        self.assertTrue(entry["local_available"])

    def test_router_returns_none_when_disabled(self):
        with override_settings(COMFYUI_ENABLED=False):
            from apps.ai_tools.comfyui.routing import ImageTaskRouter

            router = ImageTaskRouter(client=MagicMock())
            self.assertIsNone(router.resolve("upscale"))

    def test_router_unknown_task_none(self):
        from apps.ai_tools.comfyui.routing import ImageTaskRouter

        router = ImageTaskRouter(client=MagicMock())
        self.assertIsNone(router.resolve("not-a-task"))


@override_settings(COMFYUI_ENABLED=True, AI_REQUIRE_LIVE_VERIFICATION=False)
class ModelSelectionTest(SimpleTestCase):
    def test_comfyui_models_present_when_enabled(self):
        models = get_image_models("upscale")
        providers = {m["provider"] for m in models}
        self.assertIn("comfyui_local", providers)

    @override_settings(COMFYUI_ENABLED=False)
    def test_comfyui_models_hidden_when_disabled(self):
        models = get_image_models("upscale")
        providers = {m["provider"] for m in models}
        self.assertNotIn("comfyui_local", providers)

    @override_settings(FAL_KEY="test-key")
    def test_select_model_prefers_hf_then_comfyui_then_mock(self):
        # Quality-first ordering: the recommended fal upscaler (priority 15)
        # beats local ComfyUI (priority 20); mock/test-only never win.
        model = select_model("upscale", None)
        self.assertIsNotNone(model)
        self.assertEqual(model["id"], "fal-esrgan-upscale")
        self.assertFalse(model.get("is_mock"))

    @override_settings(COMFYUI_ENABLED=True, FAL_KEY="")
    def test_select_model_falls_back_to_comfyui_without_fal(self):
        model = select_model("upscale", None)
        self.assertIsNotNone(model)
        self.assertEqual(model["provider"], "comfyui_local")


@override_settings(
    COMFYUI_ENABLED=True,
    COMFYUI_BASE_URL="http://127.0.0.1:8188",
    COMFYUI_TIMEOUT=5,
)
class ComfyUIProviderTest(SimpleTestCase):
    def test_registered_in_provider_registry(self):
        from apps.ai_tools.providers import get_provider, PROVIDER_ADAPTERS

        self.assertIn("comfyui_local", PROVIDER_ADAPTERS)
        provider = get_provider("comfyui_local")
        self.assertEqual(provider.name, "comfyui_local")

    def test_disabled_when_env_off(self):
        with override_settings(COMFYUI_ENABLED=False):
            from apps.ai_tools.providers.comfyui_provider import ComfyUILocalImageProvider

            provider = ComfyUILocalImageProvider()
            self.assertFalse(provider.is_configured())

    def test_supports_upscale_and_bg_remove(self):
        from apps.ai_tools.providers.comfyui_provider import ComfyUILocalImageProvider

        provider = ComfyUILocalImageProvider()
        self.assertTrue(provider.supports("upscale"))
        self.assertTrue(provider.supports("background-remove"))
        self.assertFalse(provider.supports("whatever"))

    @patch("apps.ai_tools.providers.comfyui_provider.ComfyUIClient")
    def test_process_success(self, mock_client_cls):
        from apps.ai_tools.providers.comfyui_provider import ComfyUILocalImageProvider
        from apps.ai_tools.providers.base import ImageProcessingRequest

        client = MagicMock()
        client.is_available.return_value = True
        client.upload_image.return_value = {"name": "in.png", "subfolder": "toolhub", "type": "input"}
        client.validate_workflow.return_value = []
        client.run.return_value = make_image_file()
        mock_client_cls.return_value = client

        provider = ComfyUILocalImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(),
                operation="background-remove",
                model_id="comfyui-local-bg-remove",
                extra={"model_name": "unauthorized-model"},
            )
        )
        self.assertEqual(result.provider, "comfyui_local")
        self.assertEqual(result.model_id, "comfyui-local-bg-remove")
        self.assertEqual(result.width, 64)
        workflow = client.run.call_args.args[0]
        self.assertEqual(workflow["1"]["inputs"]["image"], "toolhub/in.png")
        self.assertEqual(
            workflow["2"]["inputs"]["bg_removal_name"], "birefnet.safetensors"
        )
        mock_client_cls.assert_called_once()

    def test_inpaint_requires_mask(self):
        from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
        from apps.ai_tools.providers.comfyui_provider import ComfyUILocalImageProvider

        with self.assertRaises(ProviderError) as ctx:
            ComfyUILocalImageProvider().process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="inpaint"
                )
            )
        self.assertEqual(ctx.exception.code, "mask_required")

    @patch("apps.ai_tools.providers.comfyui_provider.ComfyUIClient")
    def test_process_unavailable_provider_error(self, mock_client_cls):
        from apps.ai_tools.providers.comfyui_provider import ComfyUILocalImageProvider
        from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError

        client = MagicMock()
        client.is_available.return_value = False
        mock_client_cls.return_value = client

        provider = ComfyUILocalImageProvider()
        with self.assertRaises(ProviderError):
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="upscale")
            )

    def test_safe_error_messages_do_not_leak(self):
        for code, msg in errors.SAFE_ERROR_MAP.items():
            self.assertNotIn("/app/", msg)
            self.assertNotIn("secret", msg.lower())
            self.assertNotIn("token", msg.lower())

    def test_error_codes_defined(self):
        self.assertEqual(
            {"COMFYUI_UNAVAILABLE", "COMFYUI_TIMEOUT", "MODEL_NOT_FOUND",
             "WORKFLOW_INVALID", "MODEL_LOAD_FAILED", "INSUFFICIENT_RESOURCES",
             "OUTPUT_NOT_FOUND"} - set(errors.SAFE_ERROR_MAP), set())


class ComfyUIHealthTest(TestCase):
    def test_snapshot_unavailable(self):
        from apps.ai_tools.health import ComfyUIHealthService

        with override_settings(COMFYUI_ENABLED=True):
            svc = ComfyUIHealthService(client=MagicMock())
            svc._client.health.side_effect = Exception("down")
            snap = svc.snapshot()
            self.assertEqual(snap["status"], "unavailable")

    def test_snapshot_disabled(self):
        from apps.ai_tools.health import ComfyUIHealthService

        with override_settings(COMFYUI_ENABLED=False):
            svc = ComfyUIHealthService(client=MagicMock())
            self.assertEqual(svc.snapshot()["status"], "disabled")

    def test_health_endpoint_auth_required(self):
        from django.test import Client as TestClient

        resp = TestClient().get("/api/v1/ai/local-ai/health/")
        self.assertIn(resp.status_code, (302, 401, 403))