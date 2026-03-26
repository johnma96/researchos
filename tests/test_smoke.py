"""Smoke test — verifies the project is importable and configured correctly."""

from researchos import __version__


def test_version_exists():
    """The package should expose a version string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"
