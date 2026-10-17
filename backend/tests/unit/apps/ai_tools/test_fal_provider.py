"""Tests for the fal.ai image provider (all HTTP mocked — no spend).

Covers: FAL_KEY gating, per-operation endpoint routing, input building
(data-URI, try-on references, kontext prompts), result parsing for both
fal response shapes ({image:{url}} and {images:[{url}]}), auth/validation
error mapping, NSFW filtering, and registry visibility.
"""

import base64
import io

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings
from PIL import Image as PILImage
from unittest.mock import patch, MagicMock

from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
from apps.ai_tools.providers.fal import FalImageProvider
from apps.ai_tools.registry import get_image_models


def make_image_file(size=(64, 64)):
    img = PILImage.new("RGB", size, color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.getvalue(), name="test.png")


def make_result_png(size=(128, 128)):
    buf = io.BytesIO()
    PILImage.new("RGB", size, color=(20, 90, 160)).save(buf, format="PNG")
    return buf.getvalue()


def fal_post_response(payload, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    resp.text = str(payload)[:300]
    return resp


@override_settings(FAL_KEY="test-fal-key")
class FalProviderTest(SimpleTestCase):
    def test_not_configured_without_key(self):
        with override_settings(FAL_KEY=""):
            provider = FalImageProvider()
            self.assertFalse(provider.is_configured())
            with self.assertRaises(ProviderError) as ctx:
                provider.process(
                    ImageProcessingRequest(image_file=make_image_file(), operation="upscale")
                )
            self.assertEqual(ctx.exception.code, "not_configured")

    def test_supports_only_mapped_operations(self):
        provider = FalImageProvider()
        for op in (
            "upscale", "fashion-model", "background-generate", "product-edit",
            "mockup-generate", "product-photography", "product-staging",
            "text-to-image", "relight", "object-remove", "inpaint",
            "generative-fill", "expand", "expand-image", "recolor", "enhance",
        ):
            self.assertTrue(provider.supports(op), op)
        self.assertFalse(provider.supports("background-remove"))
        self.assertFalse(provider.supports("shadow"))

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_upscale_builds_esrgan_input(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"image": {"url": "https://cdn.example/u.png", "width": 128, "height": 128}}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="upscale",
                model_id="fal-esrgan-upscale",
            )
        )
        self.assertEqual(result.width, 128)
        self.assertEqual(result.model_id, "fal-esrgan-upscale")
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/esrgan", args[0])
        self.assertEqual(kwargs["headers"]["Authorization"], "Key test-fal-key")
        sent = kwargs["json"]
        self.assertTrue(sent["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(sent["model"], "RealESRGAN_x4plus")

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_tryon_requires_garment_reference(self, mock_get, mock_post):
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="fashion-model",
                    model_id="fal-fashn-tryon",
                )
            )
        self.assertEqual(ctx.exception.code, "reference_required")
        mock_post.assert_not_called()

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_tryon_sends_model_and_garment(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"images": [{"url": "https://cdn.fashn.ai/x/output_0.png"}]}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="fashion-model",
                model_id="fal-fashn-tryon",
                reference_files=[make_image_file()],
            )
        )
        self.assertEqual(result.width, 128)
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/fashn/tryon/v1.6", args[0])
        sent = kwargs["json"]
        self.assertTrue(sent["model_image"].startswith("data:"))
        self.assertTrue(sent["garment_image"].startswith("data:"))
        self.assertEqual(sent["mode"], "balanced")

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_kontext_edit_uses_prompt(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"images": [{"url": "https://cdn.example/e.png", "width": 128, "height": 128}]}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="background-generate",
                model_id="fal-flux-kontext-edit", prompt="studio backdrop",
            )
        )
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/flux-kontext", args[0])
        self.assertEqual(kwargs["json"]["prompt"], "studio backdrop")

    @patch("apps.ai_tools.providers.fal.requests.post")
    def test_auth_failure_maps_to_not_configured(self, mock_post):
        mock_post.return_value = fal_post_response({"detail": "Unauthorized"}, status=401)
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="upscale")
            )
        self.assertEqual(ctx.exception.code, "not_configured")

    @patch("apps.ai_tools.providers.fal.requests.post")
    def test_validation_error_mapped(self, mock_post):
        mock_post.return_value = fal_post_response({"detail": "bad input"}, status=422)
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="upscale")
            )
        self.assertEqual(ctx.exception.code, "invalid_input")

    @patch("apps.ai_tools.providers.fal.requests.post")
    def test_nsfw_result_rejected(self, mock_post):
        mock_post.return_value = fal_post_response(
            {"images": [{"url": "https://cdn.example/x.png"}], "has_nsfw_concepts": [True]}
        )
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="text-to-image",
                    model_id="fal-flux-schnell-t2i", prompt="x",
                )
            )
        self.assertEqual(ctx.exception.code, "content_filtered")

    def test_non_fal_model_id_rejected(self):
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="upscale",
                    model_id="cf-flux-klein-4b",
                )
            )
        self.assertEqual(ctx.exception.code, "unsupported_operation")

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_inpaint_requires_mask(self, mock_get, mock_post):
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="object-remove",
                    model_id="fal-qwen-inpaint", prompt="remove it",
                )
            )
        self.assertEqual(ctx.exception.code, "mask_required")
        mock_post.assert_not_called()

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_inpaint_sends_mask_and_prompt(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"images": [{"url": "https://cdn.example/i.png"}]}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="object-remove",
                model_id="fal-qwen-inpaint", prompt="remove the sign",
                mask_file=make_image_file(),
            )
        )
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/qwen-image-edit/inpaint", args[0])
        sent = kwargs["json"]
        self.assertTrue(sent["mask_url"].startswith("data:"))
        self.assertEqual(sent["prompt"], "remove the sign")

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_outpaint_maps_directions_and_clamps(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"images": [{"url": "https://cdn.example/o.png"}]}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="expand",
                model_id="fal-outpaint",
                extra={"directions": ["left", "right"], "expand": 5000},
            )
        )
        _, kwargs = mock_post.call_args
        sent = kwargs["json"]
        self.assertIn("/fal-ai/image-apps-v2/outpaint", mock_post.call_args.args[0])
        self.assertEqual(sent["expand_left"], 700)
        self.assertEqual(sent["expand_right"], 700)
        self.assertEqual(sent["expand_top"], 0)

    @patch("apps.ai_tools.providers.fal.requests.post")
    def test_outpaint_rejects_empty_directions(self, mock_post):
        provider = FalImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="expand",
                    model_id="fal-outpaint", extra={"directions": ["sideways"]},
                )
            )
        self.assertEqual(ctx.exception.code, "invalid_input")
        mock_post.assert_not_called()

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_clarity_enhance_keeps_dimensions(self, mock_get, mock_post):
        mock_post.return_value = fal_post_response(
            {"image": {"url": "https://cdn.example/c.png"}}
        )
        mock_get.return_value = MagicMock(content=make_result_png())
        mock_get.return_value.raise_for_status.return_value = None
        provider = FalImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="enhance",
                model_id="fal-clarity-enhance",
            )
        )
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/clarity-upscaler", args[0])
        sent = kwargs["json"]
        self.assertEqual(sent["upscale_factor"], 1)
        self.assertIn("prompt", sent)


@override_settings(FAL_KEY="test-fal-key", AI_REQUIRE_LIVE_VERIFICATION=False)
class FalRegistryTest(SimpleTestCase):
    def test_registry_shows_fal_when_configured(self):
        providers = {m["provider"] for m in get_image_models()}
        self.assertIn("fal", providers)
        upscale = [m for m in get_image_models("upscale") if m["provider"] == "fal"]
        self.assertTrue(upscale)

    def test_registry_hides_fal_without_key(self):
        with override_settings(FAL_KEY=""):
            providers = {m["provider"] for m in get_image_models()}
            self.assertNotIn("fal", providers)

    def test_fal_upscale_is_production_eligible_shape(self):
        models = [m for m in get_image_models("upscale") if m["id"] == "fal-esrgan-upscale"]
        self.assertTrue(models)
        self.assertFalse(models[0].get("is_mock"))
