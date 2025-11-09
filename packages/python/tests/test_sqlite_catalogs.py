import pytest
from catalogmx.catalogs.sepomex.codigos_postales import CodigosPostalesSQLite

def test_sqlite_connection():
    """Test that the SQLite database can be connected to."""
    try:
        conn = CodigosPostalesSQLite._get_connection()
        assert conn is not None
    except FileNotFoundError:
        pytest.fail("The sepomex.db file was not found. Please run the migration script.")

def test_get_by_cp_sqlite():
    """Test retrieving postal code data by CP from SQLite."""
    results = CodigosPostalesSQLite.get_by_cp('01000')
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]['asentamiento'] == 'San Ángel'
    assert results[0]['municipio'] == 'Álvaro Obregón'

def test_is_valid_cp_sqlite_true():
    """Test that an existing postal code is reported as valid from SQLite."""
    assert CodigosPostalesSQLite.is_valid('06700') == True

def test_is_valid_cp_sqlite_false():
    """Test that a non-existing postal code is reported as invalid from SQLite."""
    assert CodigosPostalesSQLite.is_valid('99999') == False
