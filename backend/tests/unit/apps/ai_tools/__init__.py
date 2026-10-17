import io
from unittest.mock import patch, MagicMock
from PIL import Image
from django.test import SimpleTestCase, override_settings
from apps.ai_tools.providers import get_provider, get_available_providers, MockImageProvider, HuggingFaceImageProvider
from apps.ai_tools.validators import validate_image_file, validate_mask_file
from apps.ai_tools.registry import select_model, get_image_models, AI_TOOL_CREDIT_COSTS


class ImageProviderTest(SimpleTestCase):
    def test_mock_provider_is_configured(self):
        provider = MockImageProvider()
        self.assertTrue(provider.is_configured())

    def test_mock_provider_name(self):
        provider = MockImageProvider()
        self.assertEqual(provider.name, "mock")

    @override_settings(HF_API_TOKEN="", HUGGINGFACE_API_KEY="")
    def test_huggingface_provider_not_configured_without_key(self):
        provider = HuggingFaceImageProvider()
        self.assertFalse(provider.is_configured())

    @override_settings(HUGGINGFACE_API_KEY="test-key", HF_API_TOKEN="")
    def test_huggingface_provider_configured_with_key(self):
        provider = HuggingFaceImageProvider()
        self.assertTrue(provider.is_configured())
        self.assertEqual(provider._api_key, "test-key")

    @override_settings(HF_API_TOKEN="test-hf-token", HUGGINGFACE_API_KEY="")
    def test_huggingface_provider_configured_with_hf_api_token(self):
        provider = HuggingFaceImageProvider()
        self.assertTrue(provider.is_configured())
        self.assertEqual(provider._api_key, "test-hf-token")

    def test_get_available_providers_includes_mock(self):
        providers = get_available_providers()
        self.assertIn("mock", providers)


class ImageValidatorTest(SimpleTestCase):
    def _make_image(self, mode="RGB", size=(200, 200), fmt="PNG"):
        img = Image.new(mode, size, color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        buf.seek(0)
        return buf

    def _make_file(self, buf, name="test.png", content_type="image/png"):
        from django.core.files.uploadedfile import InMemoryUploadedFile
        return InMemoryUploadedFile(buf, "ImageField", name, content_type, buf.tell(), None)

    def test_valid_image_passes(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = validate_image_file(f)
        self.assertEqual(result["width"], 200)
        self.assertEqual(result["height"], 200)

    def test_oversized_image_rejected(self):
        buf = self._make_image(size=(50000, 50000))
        f = self._make_file(buf)
        with self.assertRaises(Exception):
            validate_image_file(f)

    def test_valid_mask_passes(self):
        buf = self._make_image(mode="L", size=(100, 100))
        f = self._make_file(buf, "mask.png")
        result = validate_mask_file(f)
        self.assertTrue(result)

    def test_rgba_mask_rejected(self):
        buf = self._make_image(mode="RGBA", size=(100, 100))
        f = self._make_file(buf, "mask.png")
        with self.assertRaises(Exception):
            validate_mask_file(f)


class ImageRegistryTest(SimpleTestCase):
    def test_credit_costs_defined(self):
        self.assertIn("background-remove", AI_TOOL_CREDIT_COSTS)
        self.assertIn("upscale", AI_TOOL_CREDIT_COSTS)
        self.assertIn("enhance", AI_TOOL_CREDIT_COSTS)
        self.assertIn("object-remove", AI_TOOL_CREDIT_COSTS)

    def test_get_image_models_returns_list(self):
        models = get_image_models("background-remove")
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)

    def test_select_model_returns_model(self):
        model = select_model("background-remove", None)
        self.assertIsNotNone(model)
        self.assertIn("id", model)

    def test_select_model_unknown_returns_none(self):
        model = select_model("unknown-tool", None)
        self.assertIsNone(model)
