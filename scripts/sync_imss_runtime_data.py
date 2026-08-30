#!/usr/bin/env python3
"""Synchronize package-local runtime data from canonical shared-data."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_DATA = REPO_ROOT / "packages" / "shared-data"
PYTHON_DATA = REPO_ROOT / "packages" / "python" / "catalogmx" / "data"
DART_DATA = REPO_ROOT / "packages" / "dart" / "lib" / "src" / "data"

RUNTIME_FILES = ("imss-tables.json", "imss-catalogs.json")
PYTHON_ONLY_FILES = {
    "cfdi-estado.json": SHARED_DATA / "sat" / "cfdi_4.0" / "estado.json",
}


def _dart_source(sources: dict[str, bytes]) -> bytes:
    decoded = {name: content.decode("utf-8") for name, content in sources.items()}
    for name, content in decoded.items():
        if "'''" in content:
            raise ValueError(f"{name} cannot be embedded in a raw Dart string")

    return (
        "// GENERATED FILE. DO NOT EDIT.\n"
        "// Run: python scripts/sync_imss_runtime_data.py\n\n"
        "const String imssTablesJson = r'''\n"
        f"{decoded['imss-tables.json'].rstrip()}\n"
        "''';\n\n"
        "const String imssCatalogsJson = r'''\n"
        f"{decoded['imss-catalogs.json'].rstrip()}\n"
        "''';\n"
    ).encode()


def expected_outputs() -> dict[Path, bytes]:
    """Return every generated artifact and its deterministic content."""
    sources = {name: (SHARED_DATA / name).read_bytes() for name in RUNTIME_FILES}
    return {
        **{PYTHON_DATA / name: content for name, content in sources.items()},
        **{
            PYTHON_DATA / name: source.read_bytes()
            for name, source in PYTHON_ONLY_FILES.items()
        },
        DART_DATA / "imss_runtime_data.generated.dart": _dart_source(sources),
    }


def synchronize(*, check: bool) -> None:
    """Write generated outputs, or fail if checked outputs are stale."""
    stale: list[str] = []
    for target, content in expected_outputs().items():
        if target.exists() and target.read_bytes() == content:
            continue
        if check:
            stale.append(str(target.relative_to(REPO_ROOT)))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    if stale:
        raise SystemExit(
            "package runtime data is stale; run scripts/sync_imss_runtime_data.py: "
            + ", ".join(stale)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail instead of updating stale files"
    )
    args = parser.parse_args()
    synchronize(check=args.check)


if __name__ == "__main__":
    main()
