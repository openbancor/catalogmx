"""Tests for deterministic reviewed CONAPO/IFT reference bundles."""

from __future__ import annotations

import importlib.util
import json
import sys
import tarfile
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "build_reviewed_reference.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("reviewed_reference_builder", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ift_bundle_is_deterministic_and_canonicalizes_json(tmp_path: Path):
    module = load_module()
    source = tmp_path / "ift"
    source.mkdir()
    (source / "codigos_lada.json").write_text('{"b":2,"a":1}\n', encoding="utf-8")
    (source / "operadores_moviles.json").write_text(
        '[{"z":2,"a":1}]\n', encoding="utf-8"
    )
    (source / "operadores_pnn.json").write_text('{"x":true}\n', encoding="utf-8")

    first = tmp_path / "first"
    second = tmp_path / "second"
    artifact1, manifest1_path, manifest1 = module.build_dataset(
        "ift.numbering", first, source
    )

    # Formatting and key order must not change semantic/binary identity.
    (source / "codigos_lada.json").write_text(
        '{\n  "a": 1,\n  "b": 2\n}\n', encoding="utf-8"
    )
    artifact2, manifest2_path, manifest2 = module.build_dataset(
        "ift.numbering", second, source
    )

    assert artifact1.read_bytes() == artifact2.read_bytes()
    assert (
        manifest1["dataset"]["content_sha256"]
        == manifest2["dataset"]["content_sha256"]
    )
    assert json.loads(manifest1_path.read_text(encoding="utf-8")) == manifest1
    assert json.loads(manifest2_path.read_text(encoding="utf-8")) == manifest2
    assert manifest1["dataset_id"] == "ift.numbering"
    assert manifest1["dataset_version"] == "1"
    assert manifest1["dataset"]["format"] == "tar.gz"
    assert manifest1["dataset"]["mount_path"] == "ift"

    with tarfile.open(artifact1, "r:gz") as archive:
        assert sorted(archive.getnames()) == [
            "ift/codigos_lada.json",
            "ift/operadores_moviles.json",
            "ift/operadores_pnn.json",
        ]
        member = archive.extractfile("ift/codigos_lada.json")
        assert member is not None
        assert member.read() == b'{"a":1,"b":2}\n'


def test_conapo_bundle_normalizes_text_line_endings(tmp_path: Path):
    module = load_module()
    source = tmp_path / "conapo"
    source.mkdir()
    (source / "municipios_tipologia.csv").write_bytes(b"a,b\r\n1,2\r\n")
    (source / "sun_2020.csv").write_bytes(b"x,y\r3,4")

    artifact, _, manifest = module.build_dataset(
        "conapo.territorial", tmp_path / "out", source
    )

    assert manifest["dataset_version"] == "2020"
    assert manifest["dataset"]["mount_path"] == "conapo"
    with tarfile.open(artifact, "r:gz") as archive:
        first = archive.extractfile("conapo/municipios_tipologia.csv")
        second = archive.extractfile("conapo/sun_2020.csv")
        assert first is not None and first.read() == b"a,b\n1,2\n"
        assert second is not None and second.read() == b"x,y\n3,4\n"


def test_reviewed_bundle_fails_closed_when_namespace_changes(tmp_path: Path):
    module = load_module()
    source = tmp_path / "ift"
    source.mkdir()
    for name in (
        "codigos_lada.json",
        "operadores_moviles.json",
        "operadores_pnn.json",
    ):
        (source / name).write_text("{}\n", encoding="utf-8")
    (source / "future.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="namespace changed"):
        module.build_dataset("ift.numbering", tmp_path / "out", source)

    (source / "future.json").unlink()
    (source / "operadores_pnn.json").unlink()
    with pytest.raises(RuntimeError, match="missing=operadores_pnn.json"):
        module.build_dataset("ift.numbering", tmp_path / "out2", source)
