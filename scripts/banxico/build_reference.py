#!/usr/bin/env python3
"""Build a deterministic Banco de México reference-data bundle.

The tracked JSON files under ``packages/shared-data/banxico`` are the reviewed
compatibility/reference views. This builder packages their JSON semantics into
one language-independent release artifact with a manifest and per-file SHA-256
checksums. It does not contact Banco de México or mutate source data; source
refresh and publication review remain separate steps.

Release members are canonical JSON rather than copies of repository formatting.
Therefore formatting-only or object-key-order changes preserve both semantic and
binary artifact identity, which makes the content-addressed release tag truly
reusable for semantically identical reviewed data.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "packages" / "shared-data" / "banxico"
DATASET_ID = "banxico.reference"
DATASET_VERSION = "1"
OUTPUT_NAME = "banxico_reference.tar.gz"
MANIFEST_NAME = "banxico_reference.manifest.json"
MOUNT_PATH = "banxico"
EXPECTED_FILES = (
    "banks.json",
    "codigos_plaza.json",
    "instituciones_financieras.json",
    "monedas_divisas.json",
    "spei_institutions.json",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(parsed: Any) -> bytes:
    """Render stable release bytes for one parsed JSON value."""
    return (
        json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def load_source_files(source_dir: Path) -> list[tuple[str, bytes, Any]]:
    """Load and validate the exact reviewed Banxico JSON namespace."""
    observed = sorted(path.name for path in source_dir.glob("*.json"))
    expected = sorted(EXPECTED_FILES)
    if observed != expected:
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        details = []
        if missing:
            details.append(f"missing={','.join(missing)}")
        if extra:
            details.append(f"unexpected={','.join(extra)}")
        raise RuntimeError(
            "Banxico reference namespace changed; review required: " + "; ".join(details)
        )

    result: list[tuple[str, bytes, Any]] = []
    for name in EXPECTED_FILES:
        path = source_dir / name
        source_payload = path.read_bytes()
        try:
            parsed = json.loads(source_payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid Banxico JSON file: {name}") from exc
        if not isinstance(parsed, (list, dict)):
            raise RuntimeError(f"Banxico JSON root must be object/array: {name}")
        result.append((name, canonical_json_bytes(parsed), parsed))
    return result


def semantic_hash(files: Sequence[tuple[str, bytes, Any]]) -> str:
    """Hash JSON semantics independently from repository formatting."""
    digest = hashlib.sha256()
    for name, canonical_payload, _ in sorted(files, key=lambda item: item[0]):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(canonical_payload)
    return digest.hexdigest()


def write_deterministic_archive(
    files: Sequence[tuple[str, bytes, Any]], output_path: Path
) -> None:
    """Write a byte-reproducible ``tar.gz`` with normalized metadata."""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, payload, _ in sorted(files, key=lambda item: item[0]):
            info = tarfile.TarInfo(name=f"{MOUNT_PATH}/{name}")
            info.size = len(payload)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(payload))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            compressed.write(tar_buffer.getvalue())


def build_manifest(
    files: Sequence[tuple[str, bytes, Any]], output_path: Path
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "authority": {
            "name": "BANXICO",
            "reviewed_compatibility_views": True,
        },
        "ingestion": {
            "release": "repository-reviewed",
            "source": "packages/shared-data/banxico",
            "release_member_encoding": "canonical-json-v1",
        },
        "dataset": {
            "file": output_path.name,
            "file_sha256": sha256_file(output_path),
            "content_sha256": semantic_hash(files),
            "format": "tar.gz",
            "mount_path": MOUNT_PATH,
            "files": [
                {
                    "path": f"{MOUNT_PATH}/{name}",
                    "bytes": len(payload),
                    "sha256": sha256_bytes(payload),
                }
                for name, payload, _ in sorted(files, key=lambda item: item[0])
            ],
        },
    }


def build_from_directory(
    source_dir: Path, output_dir: Path
) -> tuple[Path, Path, dict[str, Any]]:
    files = load_source_files(source_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / OUTPUT_NAME
    manifest_path = output_dir / MANIFEST_NAME
    write_deterministic_archive(files, artifact)
    manifest = build_manifest(files, artifact)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact, manifest_path, manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)

    artifact, manifest_path, manifest = build_from_directory(
        args.source_dir, args.output_dir
    )
    print(
        f"Built {artifact} and {manifest_path}: "
        f"content_sha256={manifest['dataset']['content_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
