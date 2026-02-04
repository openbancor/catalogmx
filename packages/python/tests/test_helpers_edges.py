from catalogmx import get_clabe_info, get_nss_info, get_project_root


def test_get_clabe_info_invalid_inputs():
    assert get_clabe_info("") is None
    assert get_clabe_info("123") is None
    assert get_clabe_info("12345678901234567A") is None


def test_get_nss_info_invalid_inputs():
    assert get_nss_info("") is None
    assert get_nss_info("123") is None
    assert get_nss_info("1234567890A") is None


def test_get_project_root_exists():
    root = get_project_root()
    assert (root / ".git").exists()
