from unittest.mock import MagicMock
from sphinxcontrib.copydirs import setup, __version__
from sphinxcontrib.copydirs.copydirs import copy_additional_directories, resolve_directory_link


def test_setup_returns_correct_metadata():
    app = MagicMock()
    result = setup(app)
    assert result["version"] == __version__
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_setup_registers_config_values():
    app = MagicMock()
    setup(app)
    app.add_config_value.assert_any_call("copydirs_additional_dirs", None, "html")
    app.add_config_value.assert_any_call("copydirs_file_rename", None, "html")
    app.add_config_value.assert_any_call("copydirs_gitignore_check", True, "html")


def test_setup_connects_event_handlers():
    app = MagicMock()
    setup(app)
    app.connect.assert_any_call("config-inited", copy_additional_directories)
    app.connect.assert_any_call("missing-reference", resolve_directory_link)
    assert app.connect.call_count == 2
