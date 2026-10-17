"""K-Means posterize tests (classical ML, deterministic — no network, no AI).

Proves the posterize operation honors its parameters, learns a genuine
palette from image data (not hardcoded), preserves transparency, stays
deterministic, and is wired honestly through the local provider + registry
(TEST-ONLY utility model, never an AI fallback).
"""

import io

import pytest
from PIL import Image

from apps.ai_tools.providers import pil_ops


def make_colorful(size=(320, 200)):
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(size[1]):
        for x in range(size[0]):
            px[x, y] = (x % 256, y % 256, (x * y) % 256)
    return img


def make_half_transparent():
    img = Image.new("RGBA", (200, 100), (0, 0, 255, 0))  # transparent blue
    px = img.load()
    for y in range(100):
        for x in range(100):
            px[x, y] = (255, 0, 0, 255)  # opaque red
    return img


def test_unique_colors_equal_k():
    out = pil_ops.run_operation("posterize", make_colorful(), {"colors": 6})
    assert len(set(out.convert("RGB").getdata())) == 6
    assert out.info["kmeans_k"] == 6
    assert len(out.info["kmeans_palette"]) == 6


def test_deterministic_same_palette_twice():
    img = make_colorful()
    a = pil_ops.run_operation("posterize", img, {"colors": 6}).info["kmeans_palette"]
    b = pil_ops.run_operation("posterize", img, {"colors": 6}).info["kmeans_palette"]
    assert a == b


def test_cluster_count_boundaries():
    img = make_colorful()
    assert pil_ops.run_operation("posterize", img, {"colors": 1}).info["kmeans_k"] == 2
    assert pil_ops.run_operation("posterize", img, {"colors": 99}).info["kmeans_k"] == 32
    assert pil_ops.run_operation("posterize", img, {"colors": "abc"}).info["kmeans_k"] == 6
    assert pil_ops.run_operation("posterize", img, {}).info["kmeans_k"] == 6
    for k in (4, 8, 16, 32):
        out = pil_ops.run_operation("posterize", img, {"colors": k})
        assert out.info["kmeans_k"] == k


def test_proportions_sum_to_one_and_dominant_first():
    out = pil_ops.run_operation("posterize", make_colorful(), {"colors": 8})
    props = out.info["kmeans_proportions"]
    assert len(props) == 8
    # Proportions are rounded to 4 decimals for JSON metadata — allow that.
    assert abs(sum(props) - 1.0) < 1e-3
    assert props[0] == max(props)  # dominant cluster first


def test_transparent_pixels_excluded_from_palette():
    out = pil_ops.run_operation("posterize", make_half_transparent(), {"colors": 4})
    palette = out.info["kmeans_palette"]
    assert "#0000ff" not in palette  # transparent blue must not contaminate
    assert out.info["kmeans_opaque_fraction"] == pytest.approx(0.5)


def test_alpha_channel_preserved():
    out = pil_ops.run_operation("posterize", make_half_transparent(), {"colors": 4})
    assert out.mode == "RGBA"
    alpha = out.split()[-1]
    assert alpha.getpixel((50, 50)) == 255   # was opaque
    assert alpha.getpixel((150, 50)) == 0    # was transparent


def test_grayscale_and_solid_inputs():
    gray = Image.new("L", (64, 64), 128)
    out = pil_ops.run_operation("posterize", gray, {"colors": 3})
    assert out.size == (64, 64)
    solid = Image.new("RGB", (100, 100), (10, 200, 30))
    out = pil_ops.run_operation("posterize", solid, {"colors": 8})
    assert out.info["kmeans_proportions"][0] == pytest.approx(1.0)


def test_palette_mode_returns_swatch_strip():
    out = pil_ops.run_operation(
        "posterize", make_colorful(), {"colors": 5, "mode": "palette"}
    )
    assert out.size == (640, 96)
    assert out.info["kmeans_mode"] == "palette"
    assert len(out.info["kmeans_palette"]) == 5
    assert out.info["kmeans_method"].startswith("k-means++")


def test_dithering_runs():
    out = pil_ops.run_operation("posterize", make_colorful(), {"colors": 4, "dithering": True})
    assert out.size == (320, 200)
    assert len(out.info["kmeans_palette"]) == 4


def test_unknown_operation_still_rejected():
    with pytest.raises(ValueError):
        pil_ops.run_operation("not-a-real-op", make_colorful(), {})


def test_provider_passes_palette_metadata_through():
    from django.core.files.base import ContentFile

    from apps.ai_tools.providers.base import ImageProcessingRequest
    from apps.ai_tools.providers.local_provider import LocalImageProvider

    buf = io.BytesIO()
    make_colorful().save(buf, format="PNG")
    buf.seek(0)
    req = ImageProcessingRequest(
        image_file=ContentFile(buf.read(), name="t.png"),
        operation="posterize",
        extra={"colors": 5},
    )
    res = LocalImageProvider().process(req)
    assert res.provider == "local"
    assert res.metadata["operation"] == "posterize"
    assert len(res.metadata["kmeans_palette"]) == 5
    assert abs(sum(res.metadata["kmeans_proportions"]) - 1.0) < 1e-3


def test_provider_rejects_garbage_bytes():
    from django.core.files.base import ContentFile

    from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
    from apps.ai_tools.providers.local_provider import LocalImageProvider

    req = ImageProcessingRequest(
        image_file=ContentFile(b"this is not an image", name="t.png"),
        operation="posterize",
        extra={"colors": 4},
    )
    with pytest.raises(ProviderError):
        LocalImageProvider().process(req)


def test_registry_wiring_is_honest():
    from apps.ai_tools import registry
    from apps.ai_tools.capabilities import (
        NON_AI_MODEL_OPERATION_ALLOWLIST,
        TEST_ONLY_MODEL_IDS,
        model_supports_operation,
    )

    assert registry.is_known_operation("posterize")
    assert registry.get_credit_cost("posterize") == 1
    assert "posterize" in registry.ALL_CAPABILITIES
    assert registry.get_operation("posterize")["feature"] == "ai_posterize"
    # Local K-Means serves ONLY posterize and stays out of AI fallbacks.
    assert NON_AI_MODEL_OPERATION_ALLOWLIST["local-kmeans"] == ["posterize"]
    assert "local-kmeans" in TEST_ONLY_MODEL_IDS
    assert model_supports_operation("local-kmeans", "posterize") is True
    assert model_supports_operation("local-kmeans", "recolor") is False
