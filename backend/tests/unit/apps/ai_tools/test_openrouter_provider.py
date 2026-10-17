"""Tests for the OpenRouter Image API provider (HTTP mocked — no spend).

Covers: OPENROUTER_API_KEY gating, T2I + img2img routing, reference
payload shape (OpenAPI-verified), b64 response parsing, auth/quota error
mapping, wrong-model rejection, and registry visibility.
"""

import base64
import io

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings
from PIL import Image as PILImage
from unittest.mock import patch, MagicMock

from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
from apps.ai_tools.providers.openrouter import OpenRouterImageProvider
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


def images_response(b64=None, cost=0.02, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {
        "data": [{"b64_json": b64 or base64.b64encode(make_result_png()).decode(), "media_type": "image/png"}],
        "usage": {"cost": cost},
    }
    resp.text = ""
    return resp


@override_settings(OPENROUTER_API_KEY="test-or-key")
class OpenRouterProviderTest(SimpleTestCase):
    def test_not_configured_without_key(self):
        with override_settings(OPENROUTER_API_KEY=""):
            provider = OpenRouterImageProvider()
            self.assertFalse(provider.is_configured())
            with self.assertRaises(ProviderError) as ctx:
                provider.process(
                    ImageProcessingRequest(image_file=make_image_file(), operation="text-to-image", prompt="x")
                )
            self.assertEqual(ctx.exception.code, "not_configured")

    def test_supports_only_mapped_operations(self):
        provider = OpenRouterImageProvider()
        for op in (
            "text-to-image", "background-generate", "product-edit",
            "mockup-generate", "enhance", "retouch", "recolor",
        ):
            self.assertTrue(provider.supports(op), op)
        self.assertFalse(provider.supports("background-remove"))
        self.assertFalse(provider.supports("upscale"))
        self.assertFalse(provider.supports("generative-fill"))

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_t2i_posts_prompt_only(self, mock_post):
        mock_post.return_value = images_response()
        provider = OpenRouterImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="text-to-image",
                model_id="or-gemini-flash-image", prompt="a studio photo",
            )
        )
        self.assertEqual(result.width, 128)
        self.assertEqual(result.model_id, "or-gemini-flash-image")
        args, kwargs = mock_post.call_args
        self.assertIn("/api/v1/images", args[0])
        self.assertTrue(kwargs["headers"]["Authorization"].startswith("Bearer "))
        sent = kwargs["json"]
        self.assertEqual(sent["model"], "google/gemini-2.5-flash-image")
        self.assertEqual(sent["prompt"], "a studio photo")
        self.assertNotIn("input_references", sent)
        self.assertEqual(result.metadata["reported_cost_usd"], 0.02)

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_edit_sends_input_reference(self, mock_post):
        mock_post.return_value = images_response()
        provider = OpenRouterImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="background-generate",
                model_id="or-gemini-flash-image", prompt="studio backdrop",
            )
        )
        _, kwargs = mock_post.call_args
        refs = kwargs["json"]["input_references"]
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["type"], "image_url")
        self.assertTrue(refs[0]["image_url"]["url"].startswith("data:image/png;base64,"))

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_quota_exhausted_mapped(self, mock_post):
        resp = MagicMock()
        resp.status_code = 402
        mock_post.return_value = resp
        provider = OpenRouterImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="text-to-image", prompt="x")
            )
        self.assertEqual(ctx.exception.code, "quota_exceeded")

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_empty_data_rejected(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"data": [], "usage": {}}
        mock_post.return_value = resp
        provider = OpenRouterImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="text-to-image", prompt="x")
            )
        self.assertEqual(ctx.exception.code, "provider_error")

    def test_non_openrouter_model_id_rejected(self):
        provider = OpenRouterImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="text-to-image",
                    model_id="cf-flux-klein-4b", prompt="x",
                )
            )
        self.assertEqual(ctx.exception.code, "unsupported_operation")

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_instruction_edits_use_default_prompts(self, mock_post):
        mock_post.return_value = images_response()
        provider = OpenRouterImageProvider()
        for op in ("enhance", "retouch", "recolor"):
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation=op,
                    model_id="or-gemini-flash-image",
                )
            )
            _, kwargs = mock_post.call_args
            sent = kwargs["json"]
            self.assertTrue(sent["prompt"], op)
            self.assertEqual(len(sent["input_references"]), 1, op)

    @patch("apps.ai_tools.providers.openrouter.requests.post")
    def test_cheap_alternates_route_to_own_slugs(self, mock_post):
        provider = OpenRouterImageProvider()
        for model_id, slug in (
            ("or-gpt-image-mini", "openai/gpt-5-image-mini"),
            ("or-gemini-lite-image", "google/gemini-3.1-flash-lite-image"),
        ):
            mock_post.return_value = images_response()
            provider = OpenRouterImageProvider()
            result = provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="text-to-image",
                    model_id=model_id, prompt="x",
                )
            )
            self.assertEqual(result.model_id, model_id)
            _, kwargs = mock_post.call_args
            self.assertEqual(kwargs["json"]["model"], slug)


@override_settings(OPENROUTER_API_KEY="test-or-key", AI_REQUIRE_LIVE_VERIFICATION=False)
class OpenRouterRegistryTest(SimpleTestCase):
    def test_registry_shows_openrouter_when_configured(self):
        providers = {m["provider"] for m in get_image_models()}
        self.assertIn("openrouter", providers)
        ids = {m["id"] for m in get_image_models("text-to-image") if m["provider"] == "openrouter"}
        self.assertEqual(
            ids, {"or-gemini-flash-image", "or-gpt-image-mini", "or-gemini-lite-image"}
        )

    def test_registry_hides_openrouter_without_key(self):
        with override_settings(OPENROUTER_API_KEY=""):
            providers = {m["provider"] for m in get_image_models()}
            self.assertNotIn("openrouter", providers)
