"""
Tests for CLI functionality
"""

from click.testing import CliRunner

from catalogmx.cli import curp, curp_generate, curp_validate, main, rfc, rfc_generate_fisica, rfc_generate_moral, rfc_validate


class TestCLI:
    """Test CLI commands"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_main_command(self):
        """Test main command group"""
        result = self.runner.invoke(main, [])
        assert result.exit_code == 0

    def test_main_help(self):
        """Test main command help"""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "RFC" in result.output or "CURP" in result.output

    def test_main_version(self):
        """Test version option"""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_rfc_command(self):
        """Test RFC command group"""
        result = self.runner.invoke(rfc, [])
        assert result.exit_code == 0

    def test_rfc_help(self):
        """Test RFC help"""
        result = self.runner.invoke(rfc, ["--help"])
        assert result.exit_code == 0
        assert "RFC" in result.output

    def test_curp_command(self):
        """Test CURP command group"""
        result = self.runner.invoke(curp, [])
        assert result.exit_code == 0

    def test_curp_help(self):
        """Test CURP help"""
        result = self.runner.invoke(curp, ["--help"])
        assert result.exit_code == 0
        assert "CURP" in result.output


class TestRFCValidate:
    """Test RFC validate command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_rfc_validate_valid(self):
        """Test validating a valid RFC"""
        result = self.runner.invoke(rfc_validate, ["GODE561231GR8"])
        assert result.exit_code == 0
        assert "valid" in result.output
        assert "Type:" in result.output
        assert "Validation details:" in result.output

    def test_rfc_validate_invalid(self):
        """Test validating an invalid RFC"""
        result = self.runner.invoke(rfc_validate, ["INVALID123"])
        assert result.exit_code == 0
        assert "invalid" in result.output

    def test_rfc_validate_moral(self):
        """Test validating a valid RFC moral"""
        result = self.runner.invoke(rfc_validate, ["TSI090909BZ1"])
        assert result.exit_code == 0
        assert "valid" in result.output


class TestRFCGenerateFisica:
    """Test RFC generate-fisica command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_rfc_generate_fisica_valid(self):
        """Test generating RFC for persona fisica"""
        result = self.runner.invoke(
            rfc_generate_fisica,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "1990-05-15"
            ]
        )
        assert result.exit_code == 0
        assert "Generated RFC:" in result.output
        assert "GALJ900515" in result.output

    def test_rfc_generate_fisica_without_materno(self):
        """Test generating RFC without materno"""
        result = self.runner.invoke(
            rfc_generate_fisica,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--fecha", "1990-05-15"
            ]
        )
        assert result.exit_code == 0
        assert "Generated RFC:" in result.output

    def test_rfc_generate_fisica_invalid_date_format(self):
        """Test generating RFC with invalid date format"""
        result = self.runner.invoke(
            rfc_generate_fisica,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "15-05-1990"
            ]
        )
        assert result.exit_code == 0
        assert "Error:" in result.output

    def test_rfc_generate_fisica_short_options(self):
        """Test generating RFC with short options"""
        result = self.runner.invoke(
            rfc_generate_fisica,
            ["-n", "Juan", "-p", "Garcia", "-m", "Lopez", "-f", "1990-05-15"]
        )
        assert result.exit_code == 0
        assert "Generated RFC:" in result.output

    def test_rfc_generate_fisica_missing_required(self):
        """Test generating RFC with missing required arguments"""
        result = self.runner.invoke(rfc_generate_fisica, ["--nombre", "Juan"])
        assert result.exit_code != 0


class TestRFCGenerateMoral:
    """Test RFC generate-moral command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_rfc_generate_moral_valid(self):
        """Test generating RFC for persona moral"""
        result = self.runner.invoke(
            rfc_generate_moral,
            [
                "--razon-social", "Tecnologia Sistemas Integrales",
                "--fecha", "2009-09-09"
            ]
        )
        assert result.exit_code == 0
        assert "Generated RFC:" in result.output
        assert "TSI090909" in result.output

    def test_rfc_generate_moral_short_options(self):
        """Test generating RFC moral with short options"""
        result = self.runner.invoke(
            rfc_generate_moral,
            ["-r", "Tecnologia Sistemas Integrales", "-f", "2009-09-09"]
        )
        assert result.exit_code == 0
        assert "Generated RFC:" in result.output

    def test_rfc_generate_moral_invalid_date_format(self):
        """Test generating RFC moral with invalid date format"""
        result = self.runner.invoke(
            rfc_generate_moral,
            [
                "--razon-social", "Tecnologia Sistemas Integrales",
                "--fecha", "09-09-2009"
            ]
        )
        assert result.exit_code == 0
        assert "Error:" in result.output

    def test_rfc_generate_moral_missing_required(self):
        """Test generating RFC moral with missing required arguments"""
        result = self.runner.invoke(rfc_generate_moral, ["--razon-social", "Test"])
        assert result.exit_code != 0


class TestCURPValidate:
    """Test CURP validate command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_curp_validate_valid(self):
        """Test validating a valid CURP"""
        result = self.runner.invoke(curp_validate, ["GORS561231HVZNNL00"])
        assert result.exit_code == 0
        assert "valid" in result.output

    def test_curp_validate_invalid(self):
        """Test validating an invalid CURP"""
        result = self.runner.invoke(curp_validate, ["INVALID1234567"])
        assert result.exit_code == 0
        assert "invalid" in result.output


class TestCURPGenerate:
    """Test CURP generate command"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_curp_generate_valid(self):
        """Test generating CURP"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "1990-05-15",
                "--sexo", "H",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Generated CURP:" in result.output
        assert "GALJ900515HJCLPN" in result.output
        assert "homoclave" in result.output

    def test_curp_generate_without_materno(self):
        """Test generating CURP without materno"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--fecha", "1990-05-15",
                "--sexo", "H",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Generated CURP:" in result.output

    def test_curp_generate_female(self):
        """Test generating CURP for female"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Maria",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "1990-05-15",
                "--sexo", "M",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Generated CURP:" in result.output
        assert "M" in result.output  # Gender in output

    def test_curp_generate_short_options(self):
        """Test generating CURP with short options"""
        result = self.runner.invoke(
            curp_generate,
            [
                "-n", "Juan",
                "-p", "Garcia",
                "-m", "Lopez",
                "-f", "1990-05-15",
                "-s", "H",
                "-e", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Generated CURP:" in result.output

    def test_curp_generate_case_insensitive_gender(self):
        """Test generating CURP with lowercase gender"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "1990-05-15",
                "--sexo", "h",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Generated CURP:" in result.output

    def test_curp_generate_invalid_date_format(self):
        """Test generating CURP with invalid date format"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "15-05-1990",
                "--sexo", "H",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code == 0
        assert "Error:" in result.output

    def test_curp_generate_invalid_gender(self):
        """Test generating CURP with invalid gender"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "Juan",
                "--paterno", "Garcia",
                "--materno", "Lopez",
                "--fecha", "1990-05-15",
                "--sexo", "X",
                "--estado", "Jalisco"
            ]
        )
        assert result.exit_code != 0

    def test_curp_generate_missing_required(self):
        """Test generating CURP with missing required arguments"""
        result = self.runner.invoke(
            curp_generate,
            ["--nombre", "Juan", "--paterno", "Garcia"]
        )
        assert result.exit_code != 0


class TestCLIExceptionHandling:
    """Test CLI exception handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_rfc_fisica_exception_handling(self):
        """Test exception handling in RFC fisica generation"""
        # This should trigger a ValueError or other exception
        result = self.runner.invoke(
            rfc_generate_fisica,
            [
                "--nombre", "X",
                "--paterno", "Y",
                "--fecha", "1900-01-01"
            ]
        )
        # Should not crash, should display error
        assert result.exit_code == 0 or "Error:" in result.output

    def test_rfc_moral_exception_handling(self):
        """Test exception handling in RFC moral generation"""
        result = self.runner.invoke(
            rfc_generate_moral,
            [
                "--razon-social", "",
                "--fecha", "2009-09-09"
            ]
        )
        # Should handle empty razon social gracefully
        assert result.exit_code == 0 or "Error:" in result.output

    def test_curp_exception_handling(self):
        """Test exception handling in CURP generation"""
        result = self.runner.invoke(
            curp_generate,
            [
                "--nombre", "X",
                "--paterno", "Y",
                "--fecha", "1800-01-01",
                "--sexo", "H",
                "--estado", "InvalidState"
            ]
        )
        # Should handle invalid state gracefully
        assert result.exit_code == 0 or "Error:" in result.output


class TestCLIMainInvocation:
    """Test CLI main invocation"""

    def test_cli_main_callable(self):
        """Test that main() is callable"""
        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 0

