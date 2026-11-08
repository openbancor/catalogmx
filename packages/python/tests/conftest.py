"""Suite-wide fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _suite_allows_dataset_downloads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the suite on the pre-0.9 data policy.

    The library default is ``offline`` (no consumer downloads unless asked), but many
    catalog tests exercise datasets that have no packaged fallback and are only
    obtainable from the published releases. They opt in explicitly here; tests of the
    default itself (``test_default_offline_mode.py``) remove the variable.
    """
    monkeypatch.setenv("CATALOGMX_DATA_MODE", "fetch-missing")
