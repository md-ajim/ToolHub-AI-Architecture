from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from apps.ai_tools.providers.mock import MockImageProvider
from apps.ai_tools.providers.huggingface import HuggingFaceImageProvider
from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
from django.core.files.base import ContentFile
from PIL import Image as PILImage
import io

try:
    import huggingface_hub  # noqa: F401
    _HF_HUB_AVAILABLE = True
except ImportError:
    _HF_HUB_AVAILABLE = False


class MockProviderProcessingTest(SimpleTestCase):
    def _make_image_file(self, mode="RGB", size=(200, 200), fmt="PNG"):
        img = PILImage.new(mode, size, color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        buf.seek(0)
        return ContentFile(buf.read(), name="test.png")

    def test_mock_background_remove(self):
        provider = MockImageProvider()
        img_file = self._make_image_file()
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="background-remove",
        )
        result = provider.process(request)
        self.assertEqual(result.provider, "mock")
        self.assertEqual(result.format, "PNG")

    def test_mock_upscale(self):
        provider = MockImageProvider()
        img_file = self._make_image_file(size=(100, 100))
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="upscale",
        )
        result = provider.process(request)
        self.assertEqual(result.width, 200)
        self.assertEqual(result.height, 200)

    def test_mock_enhance(self):
        provider = MockImageProvider()
        img_file = self._make_image_file()
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="enhance",
        )
        result = provider.process(request)
        self.assertEqual(result.provider, "mock")

    def test_mock_object_remove(self):
        provider = MockImageProvider()
        img_file = self._make_image_file()
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="object-remove",
        )
        result = provider.process(request)
        self.assertEqual(result.provider, "mock")

    def test_mock_passport(self):
        provider = MockImageProvider()
        img_file = self._make_image_file()
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="passport-photo",
        )
        result = provider.process(request)
        self.assertEqual(result.provider, "mock")

    def test_mock_passport_honors_country_parameter(self):
        provider = MockImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=self._make_image_file(size=(100, 100)),
                operation="passport-photo",
                extra={"country": "uk"},
            )
        )
        self.assertEqual((result.width, result.height), (350, 450))

    def test_mock_unsupported_operation(self):
        provider = MockImageProvider()
        img_file = self._make_image_file()
        request = ImageProcessingRequest(
            image_file=img_file,
            operation="unknown",
        )
        with self.assertRaises(Exception):
            provider.process(request)


@override_settings(HF_API_TOKEN="test-token", HUGGINGFACE_API_KEY="")
class HuggingFaceImageProviderTest(SimpleTestCase):
    """HF provider uses the InferenceClient task methods on the auto-router."""

    def _make_image_file(self, mode="RGB", size=(64, 64), fmt="PNG"):
        img = PILImage.new(mode, size, color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        buf.seek(0)
        return ContentFile(buf.read(), name="test.png")

    def _make_seg_element(self, mode="RGBA"):
        mask = PILImage.new(mode, (64, 64), (255, 0, 0, 255))
        el = MagicMock()
        el.label = "mask"
        el.mask = mask
        return el

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_background_remove_uses_rmbg_segmentation(self, mock_client_factory):
        client = MagicMock()
        client.image_segmentation.return_value = [self._make_seg_element()]
        mock_client_factory.return_value = client

        provider = HuggingFaceImageProvider()
        result = provider.process(
            ImageProcessingRequest(image_file=self._make_image_file(), operation="background-remove")
        )
        self.assertEqual(result.provider, "huggingface")
        self.assertEqual(result.model_id, "briaai/RMBG-2.0")
        self.assertEqual(result.format, "PNG")
        client.image_segmentation.assert_called_once()
        _, kwargs = client.image_segmentation.call_args
        self.assertEqual(kwargs["model"], "briaai/RMBG-2.0")

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_generative_fill_uses_image_to_image(self, mock_client_factory):
        client = MagicMock()
        client.image_to_image.return_value = PILImage.new("RGB", (64, 64), (10, 20, 30))
        mock_client_factory.return_value = client

        provider = HuggingFaceImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=self._make_image_file(),
                operation="generative-fill",
                prompt="replace the sky",
            )
        )
        self.assertEqual(result.model_id, "Qwen/Qwen-Image-Edit-2511")
        self.assertEqual(result.format, "PNG")
        _, kwargs = client.image_to_image.call_args
        self.assertEqual(kwargs["model"], "Qwen/Qwen-Image-Edit-2511")
        self.assertEqual(kwargs["prompt"], "replace the sky")

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_edit_uses_default_prompt_when_missing(self, mock_client_factory):
        client = MagicMock()
        client.image_to_image.return_value = PILImage.new("RGB", (64, 64), (10, 20, 30))
        mock_client_factory.return_value = client

        provider = HuggingFaceImageProvider()
        provider.process(
            ImageProcessingRequest(image_file=self._make_image_file(), operation="product-edit")
        )
        _, kwargs = client.image_to_image.call_args
        self.assertEqual(kwargs["model"], "Qwen/Qwen-Image-Edit-2511")

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_registry_model_id_resolved_to_hf_model(self, mock_client_factory):
        client = MagicMock()
        client.image_to_image.return_value = PILImage.new("RGB", (64, 64), (10, 20, 30))
        mock_client_factory.return_value = client

        provider = HuggingFaceImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=self._make_image_file(),
                operation="product-edit",
                model_id="hf-qwen-image-edit",
            )
        )
        _, kwargs = client.image_to_image.call_args
        self.assertEqual(kwargs["model"], "Qwen/Qwen-Image-Edit-2511")

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_local_process_overwrites_invalid_operation_ok(self, mock_client_factory):
        client = MagicMock()
        mock_client_factory.return_value = client
        provider = HuggingFaceImageProvider()
        with self.assertRaises(ProviderError):
            provider.process(
                ImageProcessingRequest(image_file=self._make_image_file(), operation="upscale")
            )

    @patch("apps.ai_tools.providers.huggingface.HuggingFaceImageProvider._client")
    def test_provider_error_wrapped_on_client_failure(self, mock_client_factory):
        client = MagicMock()
        client.image_segmentation.side_effect = Exception("boom")
        mock_client_factory.return_value = client

        provider = HuggingFaceImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=self._make_image_file(), operation="background-remove")
            )
        self.assertEqual(ctx.exception.code, "provider_error")


class LocalRMBGImageProviderTest(SimpleTestCase):
    def _make_image_file(self, mode="RGB", size=(64, 64), fmt="PNG"):
        img = PILImage.new(mode, size, color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        buf.seek(0)
        return ContentFile(buf.read(), name="test.png")

    @patch("rembg.new_session")
    @patch("rembg.remove")
    def test_background_remove_returns_rgba_png(self, mock_remove, mock_new_session):
        from apps.ai_tools.providers.rembg_provider import LocalRMBGImageProvider

        provider = LocalRMBGImageProvider()
        mock_remove.return_value = PILImage.new("RGBA", (64, 64), (0, 0, 0, 0))
        result = provider.process(
            ImageProcessingRequest(image_file=self._make_image_file(), operation="background-remove")
        )
        self.assertEqual(result.provider, "local_rmbg")
        self.assertEqual(result.model_id, "local-rmbg-u2net")
        self.assertEqual(result.format, "PNG")
        mock_remove.assert_called_once()

    @patch("rembg.new_session")
    @patch("rembg.remove")
    def test_unsupported_operation_raises(self, mock_remove, mock_new_session):
        from apps.ai_tools.providers.rembg_provider import LocalRMBGImageProvider

        provider = LocalRMBGImageProvider()
        with self.assertRaises(ProviderError):
            provider.process(
                ImageProcessingRequest(image_file=self._make_image_file(), operation="upscale")
            )
        mock_remove.assert_not_called()

    def test_supports_only_background_remove(self):
        from apps.ai_tools.providers.rembg_provider import LocalRMBGImageProvider

        provider = LocalRMBGImageProvider()
        self.assertTrue(provider.supports("background-remove"))
        self.assertFalse(provider.supports("upscale"))
