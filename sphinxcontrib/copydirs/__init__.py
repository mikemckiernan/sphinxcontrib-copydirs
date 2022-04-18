import pbr.version

from .copydirs import *

# __import__('pkg_resources').declare_namespace(__name__)

__version__ = pbr.version.VersionInfo("sphinxcontrib-copydirs").version_string()


def setup(app):
    app.add_config_value("copydirs_additional_dirs", None, "html")
    # app.add_config_value(
    #     "copydirs_search_suffixes", [".png", ".tif", ".jpg", ".svg"], "html"
    # )
    app.add_config_value("copydirs_file_rename", None, "html")
    app.connect("config-inited", copy_additional_directories)
    # app.connect("html-collect-pages", copy_directories_to_output)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
