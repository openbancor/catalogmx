"""Build deterministic bundles from reviewed small reference-data snapshots.

This builder is for datasets whose tracked files are reviewed compatibility or
reference views rather than independently normalized SQLite datasets. It never
contacts the authority and never mutates source data. Authority-specific refresh
and review remain separate from distribution.

JSON members are canonicalized by parsed semantics; text members normalize line
endings. The resulting tar.gz is byte-reproducible and its manifest records a
semantic content hash plus per-file SHA-256 values for safe runtime extraction.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[1]

Encoding = Literal["json", "text"]


@dataclass(frozen=True)
class ReviewedDataset:
    dataset_id: str
    dataset_version: str
    source_dir: Path
    output_name: str
    manifest_name: str
    mount_path: str
    files: tuple[tuple[str, Encoding], ...]
    authority: dict[str, Any]


DATASETS = {
    "conapo.territorial": ReviewedDataset(
        dataset_id="conapo.territorial",
        dataset_version="2020",
        source_dir=REPO_ROOT / "packages" / "shared-data" / "conapo",
        output_name="conapo_territorial.tar.gz",
        manifest_name="conapo_territorial.manifest.json",
        mount_path="conapo",
        files=(
            ("municipios_tipologia.csv", "text"),
            ("sun_2020.csv", "text"),
        ),
        authority={
            "name": "CONAPO/SEDATU/INEGI",
            "reviewed_compatibility_views": True,
        },
    ),
    "ift.numbering": ReviewedDataset(
        dataset_id="ift.numbering",
        dataset_version="1",
        source_dir=REPO_ROOT / "packages" / "shared-data" / "ift",
        output_name="ift_numbering.tar.gz",
        manifest_name="ift_numbering.manifest.json",
        mount_path="ift",
        files=(
            ("codigos_lada.json", "json"),
            ("operadores_moviles.json", "json"),
            ("operadores_pnn.json", "json"),
        ),
        authority={
            "name": "IFT",
            "reviewed_compatibility_views": True,
        },
    ),
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: bytes, name: str) -> bytes:
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON reference file: {name}") from exc
    if not isinstance(parsed, (list, dict)):
        raise TypeError(f"JSON reference root must be object/array: {name}")
    return (
        json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_text_bytes(payload: bytes, name: str) -> bytes:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"invalid UTF-8 reference file: {name}") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized.encode("utf-8")


def load_source_files(
    dataset: ReviewedDataset, source_dir: Path
) -> list[tuple[str, bytes]]:
    expected_names = [name for name, _ in dataset.files]
    observed = sorted(path.name for path in source_dir.iterdir())
    if observed != sorted(expected_names):
        missing = sorted(set(expected_names) - set(observed))
        extra = sorted(set(observed) - set(expected_names))
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("unexpected=" + ",".join(extra))
        raise RuntimeError(
            f"{dataset.dataset_id} reference namespace changed; review required: "
            + "; ".join(details)
        )

    files: list[tuple[str, bytes]] = []
    for name, encoding in dataset.files:
        path = source_dir / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"reference member is not a regular file: {name}")
        raw = path.read_bytes()
        if encoding == "json":
            canonical = canonical_json_bytes(raw, name)
        elif encoding == "text":
            canonical = canonical_text_bytes(raw, name)
        else:  # pragma: no cover - ReviewedDataset is static trusted configuration.
            raise AssertionError(f"unsupported reference encoding: {encoding}")
        files.append((name, canonical))
    return files


def semantic_hash(files: Sequence[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for name, payload in sorted(files):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
    return digest.hexdigest()


def write_deterministic_archive(
    dataset: ReviewedDataset,
    files: Sequence[tuple[str, bytes]],
    output_path: Path,
) -> None:
    tar_buffer = io.BytesIO()
    with tarfile.open(
        fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT
    ) as archive:
        for name, payload in sorted(files):
            info = tarfile.TarInfo(name=f"{dataset.mount_path}/{name}")
            info.size = len(payload)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(payload))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as raw, gzip.GzipFile(
        fileobj=raw, mode="wb", filename="", mtime=0
    ) as compressed:
        compressed.write(tar_buffer.getvalue())


def build_manifest(
    dataset: ReviewedDataset,
    files: Sequence[tuple[str, bytes]],
    artifact: Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "dataset_id": dataset.dataset_id,
        "dataset_version": dataset.dataset_version,
        "authority": dataset.authority,
        "ingestion": {
            "release": "repository-reviewed",
            "source": str(dataset.source_dir.relative_to(REPO_ROOT)),
            "release_member_encoding": "reviewed-reference-v1",
        },
        "dataset": {
            "file": artifact.name,
            "file_sha256": sha256_file(artifact),
            "content_sha256": semantic_hash(files),
            "format": "tar.gz",
            "mount_path": dataset.mount_path,
            "files": [
                {
                    "path": f"{dataset.mount_path}/{name}",
                    "bytes": len(payload),
                    "sha256": sha256_bytes(payload),
                }
                for name, payload in sorted(files)
            ],
        },
    }


def build_dataset(
    dataset_id: str,
    output_dir: Path,
    source_dir: Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    dataset = DATASETS[dataset_id]
    source = source_dir or dataset.source_dir
    files = load_source_files(dataset, source)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / dataset.output_name
    manifest_path = output_dir / dataset.manifest_name
    write_deterministic_archive(dataset, files, artifact)
    manifest = build_manifest(dataset, files, artifact)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact, manifest_path, manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=sorted(DATASETS))
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Override the reviewed source directory (tests/local verification only)",
    )
    args = parser.parse_args(argv)

    artifact, manifest_path, manifest = build_dataset(
        args.dataset, args.output_dir, args.source_dir
    )
    print(
        f"Built {artifact} and {manifest_path}: "
        f"content_sha256={manifest['dataset']['content_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
