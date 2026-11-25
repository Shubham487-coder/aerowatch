"""Phase 0 placeholder test: proves the package installs and imports."""

import aerowatch


def test_package_imports_and_has_version() -> None:
    assert isinstance(aerowatch.__version__, str)
    assert aerowatch.__version__ != ""
