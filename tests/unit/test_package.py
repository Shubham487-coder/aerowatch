"""Phase 0 placeholder test: proves the package installs and imports."""

import predictiq


def test_package_imports_and_has_version() -> None:
    assert isinstance(predictiq.__version__, str)
    assert predictiq.__version__ != ""
