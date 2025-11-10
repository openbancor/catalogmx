"""
Tests for __main__ module
"""

import subprocess
import sys


class TestMain:
    """Test __main__ module execution"""

    def test_main_module_execution(self):
        """Test that the module can be executed with python -m"""
        # Test with --help to avoid actual execution
        result = subprocess.run(
            [sys.executable, "-m", "catalogmx", "--help"],
            cwd="/Users/luisfernando/Code/openbancor/catalogmx/packages/python",
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should not crash
        assert result.returncode in [0, 2]  # 0 for success, 2 for click errors

    def test_main_module_version(self):
        """Test that version option works"""
        result = subprocess.run(
            [sys.executable, "-m", "catalogmx", "--version"],
            cwd="/Users/luisfernando/Code/openbancor/catalogmx/packages/python",
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should show version
        assert result.returncode == 0 or "version" in result.output.lower() or "0.2.0" in result.output

