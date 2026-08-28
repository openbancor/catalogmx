"""Restore package Black formatting after root-level preparation formatting."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one formatting match in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    lada = ROOT / "packages/python/catalogmx/catalogs/ift/codigos_lada.py"
    replace_once(
        lada,
        "    def get_prefijos_por_municipio(\n"
        "        cls, cve_entidad: str, cve_municipio: str\n"
        "    ) -> list[str]:\n",
        "    def get_prefijos_por_municipio(cls, cve_entidad: str, cve_municipio: str) -> list[str]:\n",
    )

    mobile = ROOT / "packages/python/catalogmx/catalogs/ift/operadores_moviles.py"
    replace_once(
        mobile,
        '            if "grupo_empresarial" in op\n'
        '            and grupo_lower in op["grupo_empresarial"].lower()\n',
        '            if "grupo_empresarial" in op and grupo_lower in op["grupo_empresarial"].lower()\n',
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
