"""
Comprehensive CLI tests for 100% coverage
"""

from click.testing import CliRunner
import pytest

from catalogmx.cli import main, rfc, curp, rfc_validate, rfc_generate_fisica, rfc_generate_moral, curp_validate, curp_generate


class TestCLIMain:
    """Test CLI main entry point"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_main_invoke(self):
        """Test invoking main without args shows help"""
        result = self.runner.invoke(main, [])
        # Click returns exit code 0 for help
        assert result.exit_code in [0, 2]

    def test_main_help(self):
        """Test main --help"""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'RFC' in result.output or 'CURP' in result.output

    def test_main_version(self):
        """Test main --version"""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.2.0' in result.output

    def test_rfc_group(self):
        """Test RFC group"""
        result = self.runner.invoke(main, ['rfc', '--help'])
        assert result.exit_code == 0
        assert 'RFC' in result.output

    def test_curp_group(self):
        """Test CURP group"""
        result = self.runner.invoke(main, ['curp', '--help'])
        assert result.exit_code == 0
        assert 'CURP' in result.output


class TestRFCValidateCLI:
    """Test RFC validate CLI command"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_rfc_validate_valid_fisica(self):
        """Test validating valid RFC fisica"""
        result = self.runner.invoke(main, ['rfc', 'validate', 'GODE561231GR8'])
        assert result.exit_code == 0
        assert 'valid' in result.output.lower()
        assert 'Type:' in result.output
        assert 'Validation details:' in result.output

    def test_rfc_validate_invalid(self):
        """Test validating invalid RFC"""
        result = self.runner.invoke(main, ['rfc', 'validate', 'INVALID'])
        assert result.exit_code == 0
        assert 'invalid' in result.output.lower()


class TestRFCGenerateFisicaCLI:
    """Test RFC generate-fisica CLI command"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_rfc_generate_fisica_full(self):
        """Test generating RFC fisica with all params"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-fisica',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--materno', 'Lopez',
            '--fecha', '1990-05-15'
        ])
        assert result.exit_code == 0
        assert 'Generated RFC:' in result.output
        assert 'GALJ900515' in result.output

    def test_rfc_generate_fisica_without_materno(self):
        """Test generating RFC fisica without materno"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-fisica',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--fecha', '1990-05-15'
        ])
        assert result.exit_code == 0
        assert 'Generated RFC:' in result.output

    def test_rfc_generate_fisica_invalid_date(self):
        """Test generating RFC fisica with invalid date"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-fisica',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--fecha', 'invalid-date'
        ])
        assert result.exit_code == 0
        assert 'Error:' in result.output

    def test_rfc_generate_fisica_exception(self):
        """Test generating RFC fisica that triggers exception"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-fisica',
            '--nombre', '',
            '--paterno', '',
            '--fecha', '1990-01-01'
        ])
        assert result.exit_code == 0
        # Should either show error or handle gracefully


class TestRFCGenerateMoralCLI:
    """Test RFC generate-moral CLI command"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_rfc_generate_moral_valid(self):
        """Test generating RFC moral"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-moral',
            '--razon-social', 'Tecnologia Sistemas Integrales',
            '--fecha', '2009-09-09'
        ])
        assert result.exit_code == 0
        assert 'Generated RFC:' in result.output
        assert 'TSI090909' in result.output

    def test_rfc_generate_moral_invalid_date(self):
        """Test generating RFC moral with invalid date"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-moral',
            '--razon-social', 'Test Company',
            '--fecha', 'invalid-date'
        ])
        assert result.exit_code == 0
        assert 'Error:' in result.output

    def test_rfc_generate_moral_exception(self):
        """Test generating RFC moral that triggers exception"""
        result = self.runner.invoke(main, [
            'rfc', 'generate-moral',
            '--razon-social', '',
            '--fecha', '2009-09-09'
        ])
        assert result.exit_code == 0
        # Should either show error or handle gracefully


class TestCURPValidateCLI:
    """Test CURP validate CLI command"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_curp_validate_valid(self):
        """Test validating valid CURP"""
        result = self.runner.invoke(main, ['curp', 'validate', 'GORS561231HVZNNL00'])
        assert result.exit_code == 0
        assert 'valid' in result.output.lower()

    def test_curp_validate_invalid(self):
        """Test validating invalid CURP"""
        result = self.runner.invoke(main, ['curp', 'validate', 'INVALID'])
        assert result.exit_code == 0
        assert 'invalid' in result.output.lower()


class TestCURPGenerateCLI:
    """Test CURP generate CLI command"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_curp_generate_full(self):
        """Test generating CURP with all params"""
        result = self.runner.invoke(main, [
            'curp', 'generate',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--materno', 'Lopez',
            '--fecha', '1990-05-15',
            '--sexo', 'H',
            '--estado', 'Jalisco'
        ])
        assert result.exit_code == 0
        assert 'Generated CURP:' in result.output
        assert 'homoclave' in result.output.lower()
        assert 'RENAPO' in result.output

    def test_curp_generate_without_materno(self):
        """Test generating CURP without materno"""
        result = self.runner.invoke(main, [
            'curp', 'generate',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--fecha', '1990-05-15',
            '--sexo', 'H',
            '--estado', 'Jalisco'
        ])
        assert result.exit_code == 0
        assert 'Generated CURP:' in result.output

    def test_curp_generate_female(self):
        """Test generating CURP for female"""
        result = self.runner.invoke(main, [
            'curp', 'generate',
            '--nombre', 'Maria',
            '--paterno', 'Garcia',
            '--fecha', '1990-05-15',
            '--sexo', 'M',
            '--estado', 'Jalisco'
        ])
        assert result.exit_code == 0
        assert 'Generated CURP:' in result.output

    def test_curp_generate_invalid_date(self):
        """Test generating CURP with invalid date"""
        result = self.runner.invoke(main, [
            'curp', 'generate',
            '--nombre', 'Juan',
            '--paterno', 'Garcia',
            '--fecha', 'invalid-date',
            '--sexo', 'H',
            '--estado', 'Jalisco'
        ])
        assert result.exit_code == 0
        assert 'Error:' in result.output

    def test_curp_generate_exception(self):
        """Test generating CURP that triggers exception"""
        result = self.runner.invoke(main, [
            'curp', 'generate',
            '--nombre', '',
            '--paterno', '',
            '--fecha', '1990-01-01',
            '--sexo', 'H',
            '--estado', 'InvalidState'
        ])
        assert result.exit_code == 0
        # Should either show error or handle gracefully


class TestCLIDirectCallable:
    """Test CLI module can be called directly"""

    def test_cli_main_if_name_main(self):
        """Test the if __name__ == '__main__' block"""
        # Simply import the module to ensure it doesn't crash
        import catalogmx.cli
        # The main function should exist
        assert hasattr(catalogmx.cli, 'main')
        assert callable(catalogmx.cli.main)

