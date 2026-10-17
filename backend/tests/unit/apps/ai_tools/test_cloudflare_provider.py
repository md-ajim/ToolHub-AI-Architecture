"""Tests for the Cloudflare Workers AI image provider.

Covers: provider registration/gating, capability mapping, text-to-image,
img2img (editing), mask-based inpainting, FLUX multipart editing, error
handling, and registry visibility (models hidden until credentials exist).
All Cloudflare API interactions are mocked.
"""

import base64
import io

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings
from PIL import Image as PILImage
from unittest.mock import patch, MagicMock

from apps.ai_tools.providers import get_provider, PROVIDER_ADAPTERS
from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
from apps.ai_tools.providers.cloudflare import CloudflareImageProvider
from apps.ai_tools.registry import get_image_models


def make_image_file(mode="RGB", size=(64, 64), fmt="PNG"):
    img = PILImage.new(mode, size, color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return ContentFile(buf.read(), name="test.png")


def png_response_b64():
    buf = io.BytesIO()
    PILImage.new("RGB", (64, 64), color=(20, 90, 160)).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def make_response(payload=None, binary=None, status=200, headers=None):
    resp = MagicMock()
    resp.status_code = status
    resp.headers = {"content-type": headers or "application/json"}
    resp.text = payload if isinstance(payload, str) else None
    if binary is not None:
        resp.content = binary
        resp.text = ""
    else:
        resp.content = b""
        resp.json.return_value = payload
    return resp


@override_settings(
    CLOUDFLARE_ACCOUNT_ID="acct123",
    CLOUDFLARE_API_TOKEN="tok",
    CLDFLARE_ACCOUNT_ID="acct123",
    CLDFLARE_API_TOKEN="tok",
    CF_ACCOUNT_ID="acct123",
    CF_API_TOKEN="tok",
    CLDFLARE_BASE_URL="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/",
    CLDFLARE_TIMEOUT=30,
)
class CloudflareProviderTest(SimpleTestCase):
    def test_registered_in_provider_registry(self):
        self.assertIn("cloudflare", PROVIDER_ADAPTERS)
        provider = get_provider("cloudflare")
        self.assertEqual(provider.name, "cloudflare")

    def test_unconfigured_without_creds(self):
        with override_settings(
            CLOUDFLARE_ACCOUNT_ID="",
            CLOUDFLARE_API_TOKEN="",
            CLDFLARE_ACCOUNT_ID="",
            CLDFLARE_API_TOKEN="",
            CF_ACCOUNT_ID="",
            CF_API_TOKEN="",
        ):
            self.assertFalse(CloudflareImageProvider().is_configured())

    def test_configured_requires_account_and_token(self):
        provider = CloudflareImageProvider()
        self.assertTrue(provider._account_id and provider._api_token)
        self.assertTrue(provider.is_configured())
        with override_settings(
            CLOUDFLARE_ACCOUNT_ID="",
            CLDFLARE_ACCOUNT_ID="",
            CF_ACCOUNT_ID="",
        ):
            self.assertFalse(CloudflareImageProvider().is_configured())
        with override_settings(
            CLOUDFLARE_API_TOKEN="",
            CLDFLARE_API_TOKEN="",
            CF_API_TOKEN="",
        ):
            self.assertFalse(CloudflareImageProvider().is_configured())

    def test_supports_known_operations(self):
        provider = CloudflareImageProvider()
        self.assertTrue(provider.supports("text-to-image"))
        self.assertTrue(provider.supports("generative-fill"))
        self.assertTrue(provider.supports("object-remove"))
        self.assertFalse(provider.supports("nothing-here"))

    def test_process_not_configured(self):
        with override_settings(
            CLOUDFLARE_ACCOUNT_ID="",
            CLOUDFLARE_API_TOKEN="",
            CLDFLARE_ACCOUNT_ID="",
            CLDFLARE_API_TOKEN="",
            CF_ACCOUNT_ID="",
            CF_API_TOKEN="",
        ):
            provider = CloudflareImageProvider()
            with self.assertRaises(ProviderError) as ctx:
                provider.process(ImageProcessingRequest(image_file=make_image_file(), operation="text-to-image", prompt="x"))
            self.assertEqual(ctx.exception.code, "not_configured")

    def test_sdxl_lightning_uses_bytedance_model(self):
        provider = CloudflareImageProvider()
        request = ImageProcessingRequest(
            image_file=make_image_file(),
            operation="text-to-image",
            model_id="cf-sdxl-lightning",
        )
        self.assertEqual(
            provider._resolve_model(request),
            "@cf/bytedance/stable-diffusion-xl-lightning",
        )

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_text_to_image_success(self, mock_post):
        mock_post.return_value = make_response(
            payload={"success": True, "result": {"response": png_response_b64()}}
        )
        provider = CloudflareImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(),
                operation="text-to-image",
                prompt="a red car",
                width=768,
                height=512,
            )
        )
        self.assertEqual(result.provider, "cloudflare")
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)
        self.assertEqual(result.format, "PNG")
        call_kwargs = mock_post.call_args.kwargs
        self.assertIn("/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0", mock_post.call_args.args[0])
        self.assertEqual(call_kwargs["json"]["prompt"], "a red car")
        self.assertEqual(call_kwargs["json"]["width"], 768)
        self.assertEqual(call_kwargs["json"]["height"], 512)
        self.assertEqual(result.model_id, "cf-sdxl-base")

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_img2img_uses_image_b64_and_strength(self, mock_post):
        mock_post.return_value = make_response(payload={"success": True, "result": {"response": png_response_b64()}})
        provider = CloudflareImageProvider()
        request = ImageProcessingRequest(
            image_file=make_image_file(),
            operation="product-edit",
            model_id="cf-sd15-img2img",
            prompt="change to blue",
            extra={"strength": 0.6},
        )
        result = provider.process(request)
        self.assertEqual(result.width, 64)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["prompt"], "change to blue")
        self.assertEqual(payload["strength"], 0.6)
        self.assertIn("image_b64", payload)
        # Base64 decodes back to a valid PNG.
        PILImage.open(io.BytesIO(base64.b64decode(payload["image_b64"]))).verify()

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_inpaint_requires_mask(self, mock_post):
        provider = CloudflareImageProvider()
        request = ImageProcessingRequest(
            image_file=make_image_file(size=(64, 64)),
            operation="inpaint",
            prompt="remove the object",
        )
        with self.assertRaises(Exception) as ctx:
            provider.process(request)
        self.assertIn("mask", str(ctx.exception).lower())
        mock_post.assert_not_called()

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_inpaint_passes_mask_bytes(self, mock_post):
        mock_post.return_value = make_response(payload={"success": True, "result": {"response": png_response_b64()}})
        provider = CloudflareImageProvider()
        mask = PILImage.new("L", (64, 64), color=255)
        mbuf = io.BytesIO()
        mask.save(mbuf, format="PNG")
        request = ImageProcessingRequest(
            image_file=make_image_file(size=(64, 64)),
            mask_file=ContentFile(mbuf.getvalue(), name="mask.png"),
            operation="object-remove",
            prompt="remove the object",
        )
        result = provider.process(request)
        self.assertEqual(result.width, 64)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(len(payload["mask"]), 64 * 64)
        self.assertIn("/stable-diffusion-v1-5-inpainting", mock_post.call_args.args[0])
        self.assertIn("image_b64", payload)

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_flux_multipart_editing(self, mock_post):
        mock_post.return_value = make_response(
            binary=base64.b64decode(png_response_b64()), headers="image/png"
        )
        provider = CloudflareImageProvider()
        request = ImageProcessingRequest(
            image_file=make_image_file(),
            operation="product-edit",
            model_id="cf-flux-klein-4b",
            prompt="style it like a sunset",
        )
        result = provider.process(request)
        self.assertEqual(result.width, 64)
        call_kwargs = mock_post.call_args.kwargs
        self.assertIn("/flux-2-klein-4b", mock_post.call_args.args[0])
        self.assertEqual(call_kwargs["data"]["prompt"], "style it like a sunset")
        self.assertIn("input_image_0", call_kwargs["files"])
        self.assertEqual(result.model_id, "cf-flux-klein-4b")

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_api_error_raises(self, mock_post):
        mock_post.return_value = make_response(
            status=400,
            payload={"success": False, "errors": [{"message": "Model input is not valid"}]},
        )
        provider = CloudflareImageProvider()
        with self.assertRaises(Exception) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="text-to-image", prompt="x")
            )
        self.assertIn("Model input is not valid", str(ctx.exception))

    @patch("apps.ai_tools.providers.cloudflare.requests.post")
    def test_blocked_sd_falls_back_to_flux(self, mock_post):
        not_allowed = make_response(
            status=400,
            payload={"success": False, "errors": [{"message": "AiError: This account is not allowed to access @cf/runwayml/stable-diffusion-v1-5-img2img."}]},
        )
        ok = make_response(binary=base64.b64decode(png_response_b64()), headers="image/png")
        mock_post.side_effect = [not_allowed, ok]
        provider = CloudflareImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(),
                operation="product-edit",
                model_id="cf-sd15-img2img",
                prompt="blue",
            )
        )
        self.assertEqual(result.width, 64)
        self.assertEqual(mock_post.call_count, 2)
        kwargs = mock_post.call_args.kwargs
        self.assertIn("files", kwargs)
        self.assertIn("/flux-2-klein-4b", mock_post.call_args.args[0])
        self.assertEqual(result.model_id, "cf-flux-klein-4b")

    def test_registry_hides_cloudflare_when_not_configured(self):
        with override_settings(
            CLOUDFLARE_ACCOUNT_ID="",
            CLOUDFLARE_API_TOKEN="",
            CLDFLARE_ACCOUNT_ID="",
            CLDFLARE_API_TOKEN="",
            CF_ACCOUNT_ID="",
            CF_API_TOKEN="",
        ):
            providers = {m["provider"] for m in get_image_models()}
            self.assertNotIn("cloudflare", providers)

    def test_registry_shows_cloudflare_when_configured(self):
        # Registry-visibility logic (live quality is gated separately and
        # covered by verify_models + test_capability_eligibility).
        with override_settings(AI_REQUIRE_LIVE_VERIFICATION=False):
            providers = {m["provider"] for m in get_image_models()}
            self.assertIn("cloudflare", providers)
            t2i = [m for m in get_image_models("text-to-image") if m["provider"] == "cloudflare"]
            self.assertTrue(t2i)