"""Unit tests for the editor snapshot validator.

Pins the contract the Layers panel relies on: group hierarchy (parentId),
color-grade presets (filter), tone adjustments, mirroring flags, plus the
size caps that protect the versions endpoint.
"""

from apps.workspace.validators import (
    validate_editor_snapshot,
    validate_layer,
    MAX_SNAPSHOT_LAYERS,
)


def make_layer(**overrides):
    layer = {
        "id": "layer-1",
        "name": "Image",
        "type": "image",
        "visible": True,
        "locked": False,
        "opacity": 100,
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 100,
        "rotation": 0,
        "zIndex": 1,
        "parentId": None,
        "filter": "none",
        "adjustments": {"brightness": 100, "contrast": 100, "saturate": 100},
        "flipH": False,
        "flipV": False,
    }
    layer.update(overrides)
    return layer


def make_snapshot(*layers):
    return {
        "imageUrl": "blob:x",
        "document": {"id": "doc-1", "layers": list(layers)},
        "timestamp": 1,
    }


def test_empty_and_imageless_snapshots_are_valid():
    assert validate_editor_snapshot(None) == []
    assert validate_editor_snapshot({}) == []
    assert validate_editor_snapshot({"imageUrl": "blob:x"}) == []


def test_full_style_and_group_fields_are_valid():
    snapshot = make_snapshot(
        make_layer(
            id="group-1",
            name="Elements",
            type="group",
            filter="warm",
            adjustments={"brightness": 120, "contrast": 90, "saturate": 110},
            flipH=True,
        ),
        make_layer(id="layer-2", name="Plant", parentId="group-1", filter="bw", flipV=True),
    )
    assert validate_editor_snapshot(snapshot) == []


def test_missing_id_and_name_are_rejected():
    assert validate_layer({}, 0) != []
    assert validate_layer({"id": "a"}, 0) != []
    assert validate_layer({"name": "b"}, 0) != []


def test_unknown_filter_and_bad_adjustments_are_rejected():
    assert validate_layer(make_layer(filter="nope"), 0) != []
    assert validate_layer(make_layer(adjustments={"brightness": 500}), 0) != []
    assert validate_layer(make_layer(adjustments="warm"), 0) != []
    assert validate_layer(make_layer(flipH="yes"), 0) != []
    assert validate_layer(make_layer(parentId=12), 0) != []
    assert validate_layer(make_layer(opacity=150), 0) != []


def test_layer_cap_is_enforced():
    layers = [make_layer(id=f"l-{i}", name=f"L{i}") for i in range(MAX_SNAPSHOT_LAYERS + 1)]
    errors = validate_editor_snapshot(make_snapshot(*layers))
    assert any("maximum" in e for e in errors)


def test_non_list_layers_are_rejected():
    assert validate_editor_snapshot({"document": {"layers": {}}}) != []
    assert validate_editor_snapshot({"document": "nope"}) != []
    assert validate_editor_snapshot("nope") != []
