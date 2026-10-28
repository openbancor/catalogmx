"""Tests for the reproducible Banxico SPEI participant (5-digit) updater."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "update_banxico_spei.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banxico_spei_updater", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PAYLOAD = {
    "instituciones": [["40002", "BANAMEX"], ["2001", "BANXICO"], ["90721", "albo"]],
    "institucionesMISPEI": [],
    "overrideCaptcha": True,
}


class FakeResponse:
    def __init__(self, body: bytes, charset: str | None = "utf-8"):
        self._body = body
        self.headers = self
        self._charset = charset

    def get_content_charset(self):
        return self._charset

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_build_url_requires_explicit_valid_date():
    module = load_module()
    assert module.build_url("2026-10-27").endswith("instituciones.do?fecha=27-10-2026")
    for bad in ("27-10-2026", "2026-13-01", "", "hoy"):
        with pytest.raises(ValueError, match="fecha"):
            module.build_url(bad)


def test_parse_payload_returns_pairs_and_fails_closed():
    module = load_module()
    module._base.MIN_EXPECTED_INSTITUTIONS = 2
    assert module.parse_payload(json.dumps(PAYLOAD)) == [
        ("40002", "BANAMEX"),
        ("2001", "BANXICO"),
        ("90721", "albo"),
    ]
    for bad in (
        "not json",
        "[]",
        '{"instituciones": "x"}',
        '{"instituciones": [["1"]]}',
    ):
        with pytest.raises(RuntimeError):
            module.parse_payload(bad)


def test_fetch_uses_no_credentials(monkeypatch):
    module = load_module()
    module._base.MIN_EXPECTED_INSTITUTIONS = 2
    seen = {}

    def fake_urlopen(request, timeout):
        seen["headers"] = dict(request.header_items())
        seen["url"] = request.full_url
        return FakeResponse(json.dumps(PAYLOAD).encode())

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    assert len(module.fetch_institutions("2026-10-27")) == 3
    assert seen["url"].endswith("fecha=27-10-2026")
    assert not {"Authorization", "Cookie"} & set(seen["headers"])


def test_apply_marks_owner_disaffiliations_and_provenance():
    module = load_module()
    module._base.MIN_EXPECTED_INSTITUTIONS = 2
    existing = [
        {"code": "002", "name": "X", "full_name": "F", "rfc": None, "spei": True},
        {
            "code": "143",
            "name": "CIBanco",
            "full_name": "CIBanco, S.A.",
            "rfc": None,
            "spei": False,
        },
        {
            "code": "630",
            "name": "CB INTERCAM",
            "full_name": "I",
            "rfc": None,
            "spei": True,
        },
        {"code": "777", "name": "OTHER", "full_name": "O", "rfc": None, "spei": True},
    ]
    merged, summary = module.build_catalog(
        existing, [("40002", "BANAMEX"), ("90721", "albo")], "2026-10-27"
    )
    by_code = {b["code"]: b for b in merged}
    for code in ("143", "630"):
        row = by_code[code]
        assert row["status"] == "historical"
        assert row["spei_code"] is None
        assert row["spei"] is False
        assert row["spei_disaffiliated"] is True
        assert row["spei_disaffiliation_date"] is None
        assert "dueño" in row["status_source"]
    # absent from the list but not covered by the owner decision: not marked disaffiliated
    assert by_code["777"]["status"] == "historical"
    assert "spei_disaffiliated" not in by_code["777"]
    assert by_code["002"]["spei_verified_at"] == "2026-10-27"
    assert by_code["002"]["spei_source"] == module.SOURCE_LABEL
    assert summary.current == 2


def test_check_consistency_detects_bad_suffix_and_collision():
    module = load_module()
    module.check_consistency(
        [{"code": "012", "spei_code": "40012", "status": "active"}]
    )
    module.check_consistency(
        [{"code": "143", "spei_code": None, "status": "historical"}]
    )
    with pytest.raises(RuntimeError, match="suffix"):
        module.check_consistency(
            [{"code": "012", "spei_code": "40014", "status": "active"}]
        )
    with pytest.raises(RuntimeError, match="duplicate"):
        module.check_consistency(
            [
                {"code": "012", "spei_code": "40012", "status": "active"},
                {"code": "012", "spei_code": None, "status": "historical"},
            ]
        )


def test_main_writes_files_and_reports_errors(tmp_path, monkeypatch, capsys):
    module = load_module()
    module._base.MIN_EXPECTED_INSTITUTIONS = 2
    banks = tmp_path / "banks.json"
    snap = tmp_path / "spei_institutions.json"
    banks.write_text(
        json.dumps(
            [{"code": "002", "name": "X", "full_name": "F", "rfc": None, "spei": True}]
        )
    )
    monkeypatch.setattr(
        module, "urlopen", lambda r, timeout: FakeResponse(json.dumps(PAYLOAD).encode())
    )
    args = [
        "--fecha",
        "2026-10-27",
        "--banks-path",
        str(banks),
        "--snapshot-path",
        str(snap),
    ]
    assert module.main(args) == 0
    data = json.loads(banks.read_text())
    assert {b["code"] for b in data} == {"001", "002", "721"}
    assert json.loads(snap.read_text())[0]["banxico_key"] == "2001"
    assert "synchronized" in capsys.readouterr().out

    before = banks.read_bytes()
    assert (
        module.main(
            [
                "--fecha",
                "mañana",
                "--banks-path",
                str(banks),
                "--snapshot-path",
                str(snap),
            ]
        )
        == 1
    )
    assert banks.read_bytes() == before

    def boom(request, timeout):
        raise OSError("network down")

    monkeypatch.setattr(module, "urlopen", boom)
    assert module.main(args) == 1
    assert banks.read_bytes() == before


def test_script_entrypoint_exits_with_main_status(monkeypatch):
    import runpy

    monkeypatch.setattr(sys, "argv", ["update_banxico_spei.py", "--fecha", "invalid"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(SCRIPT_PATH), run_name="__main__")
    assert excinfo.value.code == 1
