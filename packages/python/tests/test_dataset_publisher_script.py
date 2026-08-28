"""Executable integration coverage for the generic release publisher shell script."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLISHER = REPO_ROOT / "scripts" / "publish_dataset_release.sh"

FAKE_GH = r'''#!/usr/bin/env python3
import json
import os
import re
import shutil
import sys
from pathlib import Path

root = Path(os.environ["FAKE_GH_STATE"])
releases = root / "releases"
releases.mkdir(parents=True, exist_ok=True)
args = sys.argv[1:]


def release_dir(tag):
    return releases / tag


def load_meta(tag):
    path = release_dir(tag) / "meta.json"
    return json.loads(path.read_text()) if path.exists() else None


def save_meta(tag, body, target):
    directory = release_dir(tag)
    directory.mkdir(parents=True, exist_ok=True)
    meta = {"id": tag, "draft": False, "body": body, "target": target}
    (directory / "meta.json").write_text(json.dumps(meta))


if args and args[0] == "api":
    if "--method" in args:
        raise SystemExit("delete is not expected in the happy-path fixture")
    query = args[args.index("--jq") + 1]
    match = re.search(r'tag_name == \\"([^\"]+)\\"', query)
    if match is None:
        match = re.search(r'tag_name == "([^"]+)"', query)
    if match is None:
        raise SystemExit(f"cannot parse tag from jq query: {query}")
    meta = load_meta(match.group(1))
    if meta is not None:
        print(json.dumps(meta))
    raise SystemExit(0)

if args[:2] == ["release", "create"]:
    tag = args[2]
    notes = args[args.index("--notes") + 1]
    target = args[args.index("--target") + 1]
    save_meta(tag, notes, target)
    assets = release_dir(tag) / "assets"
    assets.mkdir(exist_ok=True)
    # `gh release create TAG [files...] [flags]`: only positional arguments
    # between TAG and the first flag are assets. Do not probe flag values with
    # Path.is_file(); long --notes strings raise ENAMETOOLONG on Python <=3.13.
    asset_values = []
    for value in args[3:]:
        if value.startswith("--"):
            break
        asset_values.append(value)
    for value in asset_values:
        path = Path(value)
        shutil.copy2(path, assets / path.name)
    raise SystemExit(0)

if args[:2] == ["release", "download"]:
    tag = args[2]
    destination = Path(args[args.index("--dir") + 1])
    destination.mkdir(parents=True, exist_ok=True)
    patterns = [args[index + 1] for index, value in enumerate(args) if value == "--pattern"]
    assets = release_dir(tag) / "assets"
    for pattern in patterns:
        source = assets / pattern
        if not source.exists():
            raise SystemExit(1)
        shutil.copy2(source, destination / pattern)
    raise SystemExit(0)

if args[:2] == ["release", "edit"]:
    tag = args[2]
    notes = args[args.index("--notes") + 1]
    target = args[args.index("--target") + 1]
    if load_meta(tag) is None:
        raise SystemExit(1)
    save_meta(tag, notes, target)
    raise SystemExit(0)

raise SystemExit(f"unexpected fake gh invocation: {args}")
'''


def test_generic_publisher_creates_verified_immutable_release_then_pointer(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_gh = bin_dir / "gh"
    fake_gh.write_text(FAKE_GH, encoding="utf-8")
    fake_gh.chmod(0o755)

    artifact = tmp_path / "dataset.bin"
    artifact.write_bytes(b"reviewed dataset bytes\n")
    file_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    content_sha = "a" * 64
    manifest = tmp_path / "dataset.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "dataset_id": "test.dataset",
                "dataset_version": "1",
                "dataset": {
                    "file": artifact.name,
                    "file_sha256": file_sha,
                    "content_sha256": content_sha,
                },
            }
        ),
        encoding="utf-8",
    )

    state = tmp_path / "state"
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["FAKE_GH_STATE"] = str(state)
    env["GITHUB_REPOSITORY"] = "openbancor/catalogmx"
    channel = "data-test-dataset-1-latest"
    target = "1" * 40
    command = [
        "bash",
        str(PUBLISHER),
        "--manifest",
        str(manifest),
        "--artifact",
        str(artifact),
        "--channel",
        channel,
        "--target",
        target,
    ]

    subprocess.run(command, check=True, env=env, capture_output=True, text=True)

    immutable = f"data-test-dataset-1-{content_sha}"
    immutable_dir = state / "releases" / immutable
    channel_dir = state / "releases" / channel
    assert (immutable_dir / "assets" / artifact.name).read_bytes() == artifact.read_bytes()
    assert (immutable_dir / "assets" / manifest.name).read_bytes() == manifest.read_bytes()
    assert list((channel_dir / "assets").iterdir()) == []

    channel_meta = json.loads((channel_dir / "meta.json").read_text(encoding="utf-8"))
    pointer = json.loads(channel_meta["body"])
    assert pointer == {
        "schema_version": 1,
        "dataset_id": "test.dataset",
        "dataset_version": "1",
        "release_tag": immutable,
        "content_sha256": content_sha,
        "artifact": artifact.name,
        "manifest": manifest.name,
    }
    assert channel_meta["target"] == target

    second = subprocess.run(command, check=True, env=env, capture_output=True, text=True)
    assert "unchanged and verified" in second.stdout
