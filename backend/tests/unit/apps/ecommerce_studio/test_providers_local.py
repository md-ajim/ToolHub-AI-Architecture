"""Tests for the local deterministic provider covering all e-commerce operations."""

from unittest.mock import patch
from django.test import SimpleTestCase
from apps.ai_tools.providers.local_provider import LocalImageProvider
from apps.ai_tools.providers.base import ImageProcessingRequest
from django.core.files.base import ContentFile
from PIL import Image as PILImage
import io


class LocalProviderOperationTest(SimpleTestCase):
    def _img(self, mode="RGBA", size=(300, 300), color=(120, 160, 200, 255)):
        img = PILImage.new(mode, size, color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return ContentFile(buf.read(), name="t.png")

    def _run(self, operation, params=None):
        provider = LocalImageProvider()
        req = ImageProcessingRequest(image_file=self._img(), operation=operation, extra=params or {})
        return provider.process(req)

    def test_is_configured(self):
        self.assertTrue(LocalImageProvider().is_configured())

    def test_background_remove(self):
        r = self._run("background-remove")
        self.assertEqual(r.provider, "local")

    def test_shadow(self):
        r = self._run("shadow", {"strength": 0.5, "mode": "natural", "direction": "bottom"})
        self.assertEqual(r.format, "PNG")

    def test_background_generate(self):
        r = self._run("background-generate", {"mode": "studio"})
        self.assertIsNotNone(r.width)

    def test_expand(self):
        r = self._run("expand", {"directions": ["all"], "expand": 50})
        self.assertGreater(r.width, 300)

    def test_relight(self):
        r = self._run("relight", {"brightness": 1.1, "mode": "studio"})
        self.assertIsNotNone(r.height)

    def test_recolor(self):
        r = self._run("recolor", {"color": "#ff0000", "strength": 0.8})
        self.assertEqual(r.provider, "local")

    def test_retouch(self):
        r = self._run("retouch", {"level": "standard"})
        self.assertIsNotNone(r.width)

    def test_marketplace_resize(self):
        r = self._run("marketplace-resize", {"width": 1000, "height": 1000, "fit": "contain", "background": "white", "padding": 40})
        self.assertEqual((r.width, r.height), (1000, 1000))

    def test_product_staging(self):
        r = self._run("product-staging", {"scene": "studio"})
        self.assertIsNotNone(r.width)

    def test_product_photography(self):
        r = self._run("product-photography", {"scene": "luxury", "lighting": "dramatic"})
        self.assertIsNotNone(r.width)

    def test_fashion_model(self):
        r = self._run("fashion-model", {"background": "studio"})
        self.assertEqual(r.metadata.get("method"), "deterministic")

    def test_ghost_mannequin(self):
        r = self._run("ghost-mannequin", {})
        self.assertIsNotNone(r.width)

    def test_flat_lay(self):
        r = self._run("flat-lay", {"background": "#f4f1ec"})
        self.assertIsNotNone(r.width)

    def test_infographic(self):
        r = self._run("infographic", {"title": "X", "features": ["a", "b"]})
        self.assertIsNotNone(r.width)

    def test_size_chart(self):
        r = self._run("size-chart", {"sizes": ["S", "M", "L"], "rows": [{"label": "Chest", "values": ["36", "38", "40"]}]})
        self.assertIsNotNone(r.width)

    def test_carousel(self):
        r = self._run("carousel", {"slides": ["Main", "Feature"]})
        self.assertGreater(r.width, 600)

    def test_social_creative(self):
        r = self._run("social-creative", {"format": "instagram_post", "headline": "Hi"})
        self.assertEqual((r.width, r.height), (1080, 1080))

    def test_ad_creative(self):
        r = self._run("ad-creative", {"headline": "Shop", "cta": "Buy"})
        self.assertEqual((r.width, r.height), (1200, 628))

    def test_unknown_operation_raises(self):
        provider = LocalImageProvider()
        req = ImageProcessingRequest(image_file=self._img(), operation="nope")
        from apps.ai_tools.providers.base import ProviderError
        with self.assertRaises(ProviderError):
            provider.process(req)
