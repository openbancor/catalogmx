"""Temporary branch-local patcher for Python Wheel Data coverage."""

from pathlib import Path


path = Path(".github/workflows/python-wheel-data.yml")
text = path.read_text(encoding="utf-8")

build_anchor = "      - name: Build wheel\n"
build_step = r'''      - name: Build SAT Nomina release fixture
        shell: bash
        run: |
          set -euo pipefail
          source_db="$RUNNER_TEMP/nomina-source.sqlite3"
          build_dir="$RUNNER_TEMP/nomina-build"
          metadata_dir="$RUNNER_TEMP/release-metadata"
          mkdir -p "$build_dir" "$metadata_dir"

          SOURCE_DB="$source_db" python - <<'PYFIXTURE'
          import os
          import sqlite3
          from pathlib import Path

          path = Path(os.environ["SOURCE_DB"])
          connection = sqlite3.connect(path)
          try:
              connection.execute(
                  "CREATE TABLE nomina_bancos ("
                  "id TEXT PRIMARY KEY, texto TEXT NOT NULL, razon_social TEXT NOT NULL, "
                  "vigencia_desde TEXT NOT NULL, vigencia_hasta TEXT NOT NULL)"
              )
              connection.execute(
                  "INSERT INTO nomina_bancos VALUES (?, ?, ?, ?, ?)",
                  ("002", "BANAMEX", "Banco Nacional de México, S.A.", "2017-01-01", ""),
              )

              two_column = {
                  "nomina_origenes_recursos": [("IP", "Ingresos propios.")],
                  "nomina_tipos_contratos": [("10", "Jubilación, pensión, retiro.")],
                  "nomina_tipos_horas": [("01", "Dobles")],
                  "nomina_tipos_incapacidades": [("04", "Licencia por cuidados médicos")],
                  "nomina_tipos_jornadas": [("08", "Por hora")],
                  "nomina_tipos_nominas": [
                      ("E", "Nómina extraordinaria"),
                      ("O", "Nómina ordinaria"),
                  ],
              }
              for table, rows in two_column.items():
                  connection.execute(
                      f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
                  )
                  connection.executemany(f'INSERT INTO "{table}" VALUES (?, ?)', rows)

              four_column = {
                  "nomina_periodicidades_pagos": [
                      ("04", "Quincenal", "2016-11-01", "")
                  ],
                  "nomina_riesgos_puestos": [
                      ("1", "Clase I", "2017-01-01", ""),
                      ("99", "No aplica", "2017-08-13", ""),
                  ],
                  "nomina_tipos_deducciones": [
                      ("115", "Deducción revision E", "2026-01-01", "")
                  ],
                  "nomina_tipos_otros_pagos": [
                      ("999", "Pagos distintos", "2017-01-01", "")
                  ],
                  "nomina_tipos_percepciones": [
                      ("057", "Percepción revision E", "2026-01-01", "")
                  ],
                  "nomina_tipos_regimenes": [
                      ("13", "Indemnización o separación", "2017-01-01", "")
                  ],
              }
              for table, rows in four_column.items():
                  connection.execute(
                      f'CREATE TABLE "{table}" ('
                      "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
                      "vigencia_desde TEXT NOT NULL, vigencia_hasta TEXT NOT NULL)"
                  )
                  connection.executemany(
                      f'INSERT INTO "{table}" VALUES (?, ?, ?, ?)', rows
                  )

              connection.execute(
                  "CREATE TABLE nomina_estados (id TEXT PRIMARY KEY, texto TEXT NOT NULL)"
              )
              connection.execute(
                  "INSERT INTO nomina_estados VALUES (?, ?)", ("AGU", "Aguascalientes")
              )
              connection.commit()
          finally:
              connection.close()
          PYFIXTURE

          python scripts/sat/build_nomina_12.py \
            --source-db "$source_db" \
            --source-tag wheel-fixture \
            --output-dir "$build_dir"

          contract=packages/python/catalogmx/data/dataset_contract.json
          dataset_id=sat.nomina_1_2
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

'''

if build_anchor not in text:
    raise SystemExit("Build wheel anchor not found")
if "Build SAT Nomina release fixture" not in text:
    text = text.replace(build_anchor, build_step + build_anchor, 1)

runtime_anchor = "      - name: Resolve Banxico from release fixture\n"
runtime_step = r'''      - name: Resolve SAT Nomina public APIs from release fixture
        shell: bash
        env:
          CATALOGMX_DATA_MODE: fetch-missing
        run: |
          export CATALOGMX_RELEASE_BASE_URL="file://$RUNNER_TEMP/releases"
          export CATALOGMX_RELEASE_METADATA_BASE_URL="file://$RUNNER_TEMP/release-metadata"
          export CATALOGMX_CACHE_DIR="$RUNNER_TEMP/nomina-consumer-cache"
          unset CATALOGMX_SHARED_DATA

          "$RUNNER_TEMP/venv/bin/python" - <<'PY'
          from catalogmx.catalogs.sat.nomina import (
              BancoCatalog,
              OrigenRecursoCatalog,
              PeriodicidadPagoCatalog,
              RiesgoPuestoCatalog,
              TipoContratoCatalog,
              TipoDeduccionCatalog,
              TipoHorasCatalog,
              TipoIncapacidadCatalog,
              TipoJornadaCatalog,
              TipoNominaCatalog,
              TipoOtroPagoCatalog,
              TipoPercepcionCatalog,
              TipoRegimenCatalog,
          )
          from catalogmx.data import DatasetResolver

          samples = [
              (BancoCatalog, "002"),
              (OrigenRecursoCatalog, "IP"),
              (PeriodicidadPagoCatalog, "04"),
              (RiesgoPuestoCatalog, "99"),
              (TipoContratoCatalog, "10"),
              (TipoDeduccionCatalog, "115"),
              (TipoHorasCatalog, "01"),
              (TipoIncapacidadCatalog, "04"),
              (TipoJornadaCatalog, "08"),
              (TipoNominaCatalog, "O"),
              (TipoOtroPagoCatalog, "999"),
              (TipoPercepcionCatalog, "057"),
              (TipoRegimenCatalog, "13"),
          ]
          for catalog, code in samples:
              item = catalog.get_by_code(code)
              assert item is not None
              assert item["code"] == code
              assert item["clave"] == code

          banco = BancoCatalog.get_banco("002")
          assert banco is not None
          assert banco["full_name"] == "Banco Nacional de México, S.A."
          assert PeriodicidadPagoCatalog.get_days("04") == 15
          assert RiesgoPuestoCatalog.get_prima_media("1") == 0.54355
          assert TipoNominaCatalog.is_ordinaria("O") is True
          assert TipoNominaCatalog.is_extraordinaria("E") is True

          resolver = DatasetResolver()
          assert resolver.verify_cached_dataset("sat.nomina_1_2")
          state = resolver.cache_status("sat.nomina_1_2")
          assert state["release_tag"].startswith(
              "data-sat-nomina-1-2-1-2-revision-e-"
          )
          PY

'''

if runtime_anchor not in text:
    raise SystemExit("Banxico runtime anchor not found")
if "Resolve SAT Nomina public APIs from release fixture" not in text:
    text = text.replace(runtime_anchor, runtime_step + runtime_anchor, 1)

path.write_text(text, encoding="utf-8")
