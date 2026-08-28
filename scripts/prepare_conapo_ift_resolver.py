#!/usr/bin/env python3
"""One-shot branch preparation for CONAPO/IFT resolver migration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "packages" / "shared-data" / "catalog-registry.json"
SHARED_DATA = ROOT / "packages" / "python" / "catalogmx" / "utils" / "shared_data.py"
PUBLISH = ROOT / ".github" / "workflows" / "publish-reference-data.yml"
WHEEL = ROOT / ".github" / "workflows" / "python-wheel-data.yml"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected one match in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def update_registry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    profiles = registry["profiles"]
    geo = profiles["mexico-geo"]["datasets"]
    if "conapo.territorial" not in geo:
        geo.append("conapo.territorial")
    profiles["mexico-telecom"] = {
        "description": "IFT numbering and reviewed telecom reference snapshots.",
        "datasets": ["ift.numbering"],
    }

    datasets = {item["id"]: item for item in registry["datasets"]}

    conapo = datasets["conapo.territorial"]
    conapo["distribution"] = "mixed"
    conapo["source_subpath"] = "conapo"
    conapo["upstream"] = [
        {
            "role": "authoritative_publication",
            "url": "https://www.gob.mx/conapo/documentos/sistema-urbano-nacional-2020",
            "format": "publication",
        },
        {
            "role": "authoritative_dataset",
            "url": "https://www.datos.gob.mx/dataset/sistema_urbano_nacional",
            "format": "csv",
        },
        {
            "role": "authoritative_metropolitan_dataset",
            "url": "https://www.datos.gob.mx/dataset/metropolis_mexico_2020",
            "format": "csv",
        },
    ]
    conapo["freshness"]["upstream_checked_at"] = "2026-08-28"
    conapo["implementation"] = {
        "status": "resolver_ready",
        "canonical_distribution": "release",
        "release_artifact": "conapo_territorial.tar.gz",
        "manifest": "conapo_territorial.manifest.json",
        "reviewed_files": ["municipios_tipologia.csv", "sun_2020.csv"],
        "legacy_view_path": "packages/shared-data/conapo",
        "publish_from_reviewed_master": True,
        "consumer_migration_required_before_removal": True,
    }
    conapo["artifact"] = {
        "version": "2020",
        "channel": "data-conapo-territorial-2020-latest",
        "file": "conapo_territorial.tar.gz",
        "manifest": "conapo_territorial.manifest.json",
        "format": "tar.gz",
        "mount_path": "conapo",
        "discovery": "release-pointer",
    }
    conapo["notes"] = (
        "SUN 2020 and Metrópolis de México 2020 remain versioned territorial "
        "classifications. CatalogMX distributes the two reviewed CSV compatibility "
        "views as a deterministic release bundle so installed runtimes do not depend "
        "on a repository checkout. The bundle preserves reviewed project semantics; "
        "authority refresh remains a separate review step."
    )

    ift = datasets["ift.numbering"]
    ift["distribution"] = "mixed"
    ift["source_subpath"] = "ift"
    ift["upstream"] = [
        {
            "role": "authoritative_numbering_service",
            "url": "https://sns.ift.org.mx/sns-frontend/consulta-numeracion/numeracion-geografica.xhtml",
            "format": "interactive_portal",
        },
        {
            "role": "authoritative_numbering_areas",
            "url": "https://sns.ift.org.mx/sns-frontend/areas-geograficas-numeracion/areas-numeracion.xhtml",
            "format": "interactive_portal",
        },
        {
            "role": "authoritative_portal",
            "url": "https://www.ift.org.mx/usuarios-y-audiencias/recursos-usuarios/recursos/numeracion",
            "format": "portal",
        },
    ]
    ift["freshness"]["upstream_checked_at"] = "2026-08-28"
    ift["implementation"] = {
        "status": "resolver_ready",
        "canonical_distribution": "release",
        "release_artifact": "ift_numbering.tar.gz",
        "manifest": "ift_numbering.manifest.json",
        "reviewed_files": [
            "codigos_lada.json",
            "operadores_moviles.json",
            "operadores_pnn.json",
        ],
        "legacy_view_path": "packages/shared-data/ift",
        "publish_from_reviewed_master": True,
        "consumer_migration_required_before_removal": True,
    }
    ift["artifact"] = {
        "version": "1",
        "channel": "data-ift-numbering-1-latest",
        "file": "ift_numbering.tar.gz",
        "manifest": "ift_numbering.manifest.json",
        "format": "tar.gz",
        "mount_path": "ift",
        "discovery": "release-pointer",
    }
    ift["notes"] = (
        "The IFT SNS is authoritative for numbering assignments. The tracked JSON "
        "files also contain CatalogMX compatibility enrichments (for example INEGI "
        "mapping, metropolitan overlays and mobile-operator convenience fields), so "
        "the runtime artifact is a reviewed snapshot rather than a claimed one-to-one "
        "IFT export. Source refresh and enrichment review remain separate from release "
        "distribution."
    )

    registry["inventory_checked_at"] = "2026-08-28"
    REGISTRY.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def update_shared_data_helper() -> None:
    replace_once(
        SHARED_DATA,
        '_DATASET_PREFIXES = {\n    "banxico": "banxico.reference",\n}',
        '_DATASET_PREFIXES = {\n    "banxico": "banxico.reference",\n    "conapo": "conapo.territorial",\n    "ift": "ift.numbering",\n}',
    )


def update_loaders() -> None:
    sun = ROOT / "packages/python/catalogmx/catalogs/conapo/sistema_urbano_nacional.py"
    replace_once(sun, "import csv\nfrom pathlib import Path\n", "import csv\n\nfrom catalogmx.utils.shared_data import get_shared_data_path\n")
    replace_once(
        sun,
        '        data_path = Path(__file__).resolve().parents[4] / "shared-data" / "conapo" / "sun_2020.csv"\n',
        '        data_path = get_shared_data_path("conapo", "sun_2020.csv")\n',
    )

    metro = ROOT / "packages/python/catalogmx/catalogs/conapo/zonas_metropolitanas.py"
    replace_once(metro, "import csv\nfrom pathlib import Path\n", "import csv\n\nfrom catalogmx.utils.shared_data import get_shared_data_path\n")
    replace_once(
        metro,
        '        data_path = (\n            Path(__file__).resolve().parents[4]\n            / "shared-data"\n            / "conapo"\n            / "municipios_tipologia.csv"\n        )\n',
        '        data_path = get_shared_data_path("conapo", "municipios_tipologia.csv")\n',
    )

    lada = ROOT / "packages/python/catalogmx/catalogs/ift/codigos_lada.py"
    replace_once(
        lada,
        "import json\nimport random\nfrom pathlib import Path\n",
        "import json\nimport random\n\nfrom catalogmx.utils.shared_data import get_shared_data_path\n",
    )
    replace_once(
        lada,
        '        data_path = (\n            Path(__file__).resolve().parents[4] / "shared-data" / "ift" / "codigos_lada.json"\n        )\n',
        '        data_path = get_shared_data_path("ift", "codigos_lada.json")\n',
    )

    mobile = ROOT / "packages/python/catalogmx/catalogs/ift/operadores_moviles.py"
    replace_once(
        mobile,
        "import json\nfrom pathlib import Path\nfrom typing import TypedDict\n",
        "import json\nfrom typing import TypedDict\n\nfrom catalogmx.utils.shared_data import get_shared_data_path\n",
    )
    replace_once(
        mobile,
        '        # Path: catalogmx/packages/python/catalogmx/catalogs/ift/operadores_moviles.py\n        # Target: catalogmx/packages/shared-data/ift/operadores_moviles.json\n        data_path = (\n            Path(__file__).parent.parent.parent.parent.parent\n            / "shared-data"\n            / "ift"\n            / "operadores_moviles.json"\n        )\n',
        '        data_path = get_shared_data_path("ift", "operadores_moviles.json")\n',
    )


def update_publish_workflow() -> None:
    text = PUBLISH.read_text(encoding="utf-8")
    marker = "      - 'packages/shared-data/banxico/**'\n"
    addition = (
        marker
        + "      - 'packages/shared-data/conapo/**'\n"
        + "      - 'packages/shared-data/ift/**'\n"
    )
    if text.count(marker) != 1:
        raise RuntimeError("publish path marker changed")
    text = text.replace(marker, addition)

    marker = "      - 'scripts/banxico/build_reference.py'\n"
    addition = marker + "      - 'scripts/build_reviewed_reference.py'\n"
    if text.count(marker) != 1:
        raise RuntimeError("publish builder marker changed")
    text = text.replace(marker, addition)

    job_marker = "  resolver-file-datasets:\n"
    job = r'''  reviewed-reference-datasets:
    name: ${{ matrix.name }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: CONAPO territorial reference
            dataset_id: conapo.territorial
            output_dir: dist/catalog-artifacts/conapo-territorial
          - name: IFT numbering reference
            dataset_id: ift.numbering
            output_dir: dist/catalog-artifacts/ift-numbering

    steps:
      - name: Checkout reviewed master
        uses: actions/checkout@v4
        with:
          ref: master
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate registry, runtime contract and publisher
        run: |
          python scripts/catalog_registry.py validate
          python scripts/render_dataset_contract.py --check
          bash -n scripts/publish_dataset_release.sh

      - name: Build reviewed reference bundle
        shell: bash
        run: |
          set -euo pipefail
          python scripts/build_reviewed_reference.py \
            --dataset "${{ matrix.dataset_id }}" \
            --output-dir "${{ matrix.output_dir }}"
          git diff --exit-code -- packages/shared-data

      - name: Verify generated manifest against runtime contract
        shell: bash
        run: |
          set -euo pipefail
          contract=packages/python/catalogmx/data/dataset_contract.json
          dataset_id='${{ matrix.dataset_id }}'
          dir='${{ matrix.output_dir }}'
          artifact_name=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.file' "$contract")
          manifest_name=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.manifest' "$contract")
          expected_version=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.version | tostring' "$contract")
          expected_format=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.format' "$contract")
          expected_mount=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.mount_path' "$contract")
          manifest="$dir/$manifest_name"
          artifact="$dir/$artifact_name"
          test -f "$manifest"
          test -f "$artifact"
          jq -e \
            --arg id "$dataset_id" \
            --arg version "$expected_version" \
            --arg file "$artifact_name" \
            --arg format "$expected_format" \
            --arg mount "$expected_mount" \
            '.schema_version == 1
             and .dataset_id == $id
             and (.dataset_version | tostring) == $version
             and .dataset.file == $file
             and .dataset.format == $format
             and .dataset.mount_path == $mount
             and (.dataset.file_sha256 | test("^[0-9a-f]{64}$"))
             and (.dataset.content_sha256 | test("^[0-9a-f]{64}$"))
             and (.dataset.files | length > 0)' \
            "$manifest" >/dev/null

      - name: Publish immutable bundle and move channel pointer
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        shell: bash
        run: |
          set -euo pipefail
          reviewed_sha=$(git rev-parse HEAD)
          git fetch origin master
          master_sha=$(git rev-parse origin/master)
          if [ "$reviewed_sha" != "$master_sha" ]; then
            echo "Checked-out publication source is not origin/master" >&2
            exit 1
          fi
          contract=packages/python/catalogmx/data/dataset_contract.json
          dataset_id='${{ matrix.dataset_id }}'
          dir='${{ matrix.output_dir }}'
          channel=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.channel' "$contract")
          artifact_name=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.file' "$contract")
          manifest_name=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.manifest' "$contract")
          bash scripts/publish_dataset_release.sh \
            --manifest "$dir/$manifest_name" \
            --artifact "$dir/$artifact_name" \
            --channel "$channel" \
            --target "$reviewed_sha"

'''
    if text.count(job_marker) != 1:
        raise RuntimeError("publish job marker changed")
    text = text.replace(job_marker, job + job_marker)
    PUBLISH.write_text(text, encoding="utf-8")


def update_wheel_workflow() -> None:
    text = WHEEL.read_text(encoding="utf-8")
    marker = "      - name: Build wheel\n"
    fixture_step = r'''      - name: Build CONAPO and IFT release fixtures
        shell: bash
        run: |
          set -euo pipefail
          contract=packages/python/catalogmx/data/dataset_contract.json
          metadata_dir="$RUNNER_TEMP/release-metadata"
          mkdir -p "$metadata_dir"
          for dataset_id in conapo.territorial ift.numbering; do
            slug=$(printf '%s' "$dataset_id" | tr '.' '-')
            build_dir="$RUNNER_TEMP/${slug}-build"
            mkdir -p "$build_dir"
            python scripts/build_reviewed_reference.py \
              --dataset "$dataset_id" \
              --output-dir "$build_dir"
            channel=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.channel' "$contract")
            artifact=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.file' "$contract")
            manifest=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.manifest' "$contract")
            version=$(jq -er --arg id "$dataset_id" '.datasets[$id].artifact.version | tostring' "$contract")
            content_sha=$(jq -er '.dataset.content_sha256' "$build_dir/$manifest")
            immutable="${channel%-latest}-${content_sha}"
            release_dir="$RUNNER_TEMP/releases/$immutable"
            mkdir -p "$release_dir"
            cp "$build_dir/$artifact" "$release_dir/"
            cp "$build_dir/$manifest" "$release_dir/"
            pointer=$(jq -cn \
              --arg dataset_id "$dataset_id" \
              --arg dataset_version "$version" \
              --arg release_tag "$immutable" \
              --arg content_sha256 "$content_sha" \
              --arg artifact "$artifact" \
              --arg manifest "$manifest" \
              '{schema_version:1,dataset_id:$dataset_id,dataset_version:$dataset_version,release_tag:$release_tag,content_sha256:$content_sha256,artifact:$artifact,manifest:$manifest}')
            jq -cn \
              --arg tag_name "$channel" \
              --arg body "$pointer" \
              '{tag_name:$tag_name,body:$body}' \
              > "$metadata_dir/$channel"
          done

'''
    if text.count(marker) != 1:
        raise RuntimeError("wheel build marker changed")
    text = text.replace(marker, fixture_step + marker)

    resolve_step = r'''
      - name: Resolve CONAPO and IFT from release fixtures
        shell: bash
        env:
          CATALOGMX_DATA_MODE: fetch-missing
        run: |
          export CATALOGMX_RELEASE_BASE_URL="file://$RUNNER_TEMP/releases"
          export CATALOGMX_RELEASE_METADATA_BASE_URL="file://$RUNNER_TEMP/release-metadata"
          export CATALOGMX_CACHE_DIR="$RUNNER_TEMP/catalogmx-cache-secondary"
          unset CATALOGMX_SHARED_DATA

          "$RUNNER_TEMP/venv/bin/python" - <<'PY'
          from catalogmx.catalogs.conapo.sistema_urbano_nacional import SistemaUrbanoNacionalCatalog
          from catalogmx.catalogs.conapo.zonas_metropolitanas import ZonasMetropolitanasCatalog
          from catalogmx.catalogs.ift.codigos_lada import CodigosLADACatalog
          from catalogmx.catalogs.ift.operadores_moviles import OperadoresMovilesCatalog
          from catalogmx.data import DatasetResolver

          assert SistemaUrbanoNacionalCatalog.get_all()
          assert ZonasMetropolitanasCatalog.get_metropolis()
          assert CodigosLADACatalog.get_all()
          assert OperadoresMovilesCatalog.get_all()

          resolver = DatasetResolver()
          assert resolver.verify_cached_dataset("conapo.territorial")
          assert resolver.verify_cached_dataset("ift.numbering")
          assert resolver.verify_profile("mexico-telecom") == {"ift.numbering": True}
          PY
'''
    if not text.endswith("\n"):
        raise RuntimeError("wheel workflow must end with newline")
    text += resolve_step
    WHEEL.write_text(text, encoding="utf-8")


def cleanup_scaffolding() -> None:
    (ROOT / "scripts" / "prepare_conapo_ift_resolver.py").unlink()
    (ROOT / ".github" / "workflows" / "prepare-conapo-ift-resolver.yml").unlink()


def main() -> int:
    update_registry()
    update_shared_data_helper()
    update_loaders()
    update_publish_workflow()
    update_wheel_workflow()
    subprocess.run(["python", "scripts/render_dataset_contract.py"], cwd=ROOT, check=True)
    cleanup_scaffolding()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
