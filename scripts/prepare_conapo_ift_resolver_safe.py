"""Generate the non-workflow portion of the CONAPO/IFT resolver migration."""

from __future__ import annotations

import subprocess

from prepare_conapo_ift_resolver import (
    ROOT,
    update_loaders,
    update_registry,
    update_shared_data_helper,
)


def main() -> int:
    update_registry()
    update_shared_data_helper()
    update_loaders()
    subprocess.run(["python", "scripts/render_dataset_contract.py"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
