"""Deterministic creative compositor tests (no network, no AI).

The five creative tools are honest Pillow layout pipelines (not AI): each
test proves the operation honors its panel parameters, produces the
documented dimensions, and actually transforms the input.
"""

import io

import pytest
from PIL import Image

from apps.ai_tools.providers import pil_ops


def make_product(size=(400, 300), color=(200, 40, 40)):
    img = Image.new("RGB", size, (30, 60, 200))
    from PIL import ImageDraw

    ImageDraw.Draw(img).rectangle([50, 50, 150, 150], fill=color)
    return img


def as_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestInfographic:
    def test_dimensions_and_bullets(self):
        base = make_product()
        out = pil_ops.run_operation(
            "infographic",
            base,
            {"title": "T", "features": ["a", "b", "c", "d", "e", "f", "g"], "accent": "#ff0000"},
        )
        assert out.size[0] >= 900
        assert out.size[1] == base.size[1] + 420
        assert as_bytes(out) != as_bytes(base)

    def test_string_features_accepted(self):
        out = pil_ops.run_operation("infographic", make_product(), {"features": "x\ny"})
        assert out.size[1] == make_product().size[1] + 420


class TestSizeChart:
    def test_table_layout(self):
        out = pil_ops.run_operation(
            "size-chart",
            make_product(),
            {"sizes": ["S", "M"], "rows": [{"label": "Chest", "values": ["36", "38"]}]},
        )
        assert out.size == (1000, 760)
        assert as_bytes(out) != as_bytes(make_product())


class TestCarousel:
    def test_one_card_per_slide(self):
        out = pil_ops.run_operation(
            "carousel", make_product(), {"slides": ["A", "B", "C"]}
        )
        assert out.size == (1800, 600)

    def test_slide_cap(self):
        out = pil_ops.run_operation(
            "carousel", make_product(), {"slides": [f"S{i}" for i in range(10)]}
        )
        assert out.size[0] == 600 * 6


class TestSocialCreative:
    @pytest.mark.parametrize(
        "fmt,dims",
        [("instagram_post", (1080, 1080)), ("tiktok", (1080, 1920)), ("banner", (1500, 500))],
    )
    def test_format_dimensions(self, fmt, dims):
        out = pil_ops.run_operation(
            "social-creative",
            make_product(),
            {"format": fmt, "headline": "Hi", "cta": "Go", "accent": "#00ff00"},
        )
        assert out.size == dims

    def test_unknown_format_falls_back(self):
        out = pil_ops.run_operation("social-creative", make_product(), {"format": "nope"})
        assert out.size == (1080, 1080)


class TestAdCreative:
    def test_fixed_canvas_and_offer(self):
        out = pil_ops.run_operation(
            "ad-creative",
            make_product(),
            {"headline": "H", "offer": "50% OFF", "cta": "Buy", "brand": "B", "accent": "#e63946"},
        )
        assert out.size == (1200, 628)
        assert as_bytes(out) != as_bytes(make_product())


class TestCreativeUtilityWiring:
    def test_local_creative_compose_is_test_only_but_allowlisted(self):
        from apps.ai_tools.capabilities import (
            NON_AI_MODEL_OPERATION_ALLOWLIST,
            TEST_ONLY_MODEL_IDS,
            model_supports_operation,
        )

        assert "local-creative-compose" in TEST_ONLY_MODEL_IDS
        for op in ("infographic", "size-chart", "carousel", "social-creative", "ad-creative"):
            assert op in NON_AI_MODEL_OPERATION_ALLOWLIST["local-creative-compose"]
            assert model_supports_operation("local-creative-compose", op) is True
        assert model_supports_operation("local-creative-compose", "upscale") is False

    def test_creative_ops_resolve_utility_without_mock(self, settings):
        settings.AI_REQUIRE_LIVE_VERIFICATION = False
        from apps.ai_tools.registry import get_image_models

        for op in ("infographic", "size-chart", "carousel", "social-creative", "ad-creative"):
            models = get_image_models(op, None)
            ids = {m["id"] for m in models}
            assert "local-creative-compose" in ids, op
            assert not (ids & {"mock-bg-remove", "local-deterministic"}), op
