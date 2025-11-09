
from click.testing import CliRunner

from catalogmx.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    # Should show help text with commands
    assert 'Mexican RFC and CURP calculator and validator' in result.output
    assert 'rfc' in result.output
    assert 'curp' in result.output
    # Exit code 2 is expected when no command is provided to Click group
    assert result.exit_code == 2
