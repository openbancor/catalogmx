"""
Data updater module for catalogmx

This module handles automatic updates of dynamic data (UDI, tipo cambio, etc.)
from GitHub Releases, allowing data updates without requiring library releases.
"""

from catalogmx.data.updater import DataUpdater

__all__ = ["DataUpdater"]
