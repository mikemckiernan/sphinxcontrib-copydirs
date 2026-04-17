from importlib.metadata import PackageNotFoundError, version
from typing import Any

from sphinx.application import Sphinx

from .copydirs import copy_additional_directories, resolve_directory_link

try:
    __version__ = version("sphinxcontrib-copydirs")
except PackageNotFoundError:
    __version__ = "unknown"


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("copydirs_additional_dirs", None, "html")
    app.add_config_value("copydirs_file_rename", None, "html")
    app.add_config_value("copydirs_gitignore_check", True, "html")
    app.connect("config-inited", copy_additional_directories)
    app.connect("missing-reference", resolve_directory_link)
    # app.connect("html-collect-pages", copy_directories_to_output)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
