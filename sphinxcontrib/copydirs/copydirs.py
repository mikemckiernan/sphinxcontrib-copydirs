import errno
import os
import shutil
import logging

from pathlib import Path

level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)

# Paths are relative to the docs/source directory.
def copy_additional_directories(app, _):
    """Copy the directories specified in
    ``copydirs_additional_dirs`` from within the
    repository into the Sphinx source directory.

    If ``copydirs_file_rename[key]`` is set, then rename
    the file as the directories is copied. For example,
    the following sample renames README.md to index.md::

    copydirs_file_rename = {
        "README.md": "index.md",
    }
    """
    if not app.config.copydirs_additional_dirs:
        return

    def copy_with_rename(src: str, dst: str):
        src_name = Path(src).name
        if src_name in app.config.copydirs_file_rename.keys():
            dst = Path(dst).parent / app.config.copydirs_file_rename[src_name]
            logger.debug(f"Renaming source file: {src_name} to {dst}")
        shutil.copy2(src, str(dst))

    for src in app.config.copydirs_additional_dirs:
        src_path = os.path.abspath(os.path.join(app.srcdir, src))
        if not os.path.exists(src_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src_path)
        base_path = os.path.commonpath([app.outdir, src_path])
        if app.config.smv_metadata:
            base_path = app.config.smv_metadata[app.config.smv_current_version][
                "basedir"
            ]
        logger.debug(
            f"copy to source, common path for output dir and additional dir: {base_path}"
        )
        out_path = os.path.relpath(src_path, base_path)
        out_path = os.path.join(app.srcdir, out_path)

        logger.info(f"Copying source documentation from: {src_path}")
        logger.info(f"  ...to destination: {out_path}")

        if os.path.exists(out_path) and os.path.isdir(out_path):
            shutil.rmtree(out_path, ignore_errors=True)
        if os.path.exists(out_path) and os.path.isfile(out_path):
            os.unlink(out_path)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, out_path, copy_function=copy_with_rename)
        else:
            shutil.copyfile(src_path, out_path)


# The cwd when this runs is the root of the repo.
# The paths in `copydirs_additional_dirs` are relative
# to app.srcdir (docs/source).
# def copy_directories_to_output(app):
#     """Copy directories and files specified in
#     ``copydirs_additional_dirs`` to the Sphinx output.

#     Only copy a file if the suffix matches
#     ``copydirs_search_suffix``. Directories are copied
#     if the directory contains a file with a matching
#     suffix.

#     The anticipated use is to copy directories with
#     image files that match ``.png``, ``.jpg``, ``.tif``,
#     or ``.svg``. You can add or subtract suffixes by
#     setting ``copydirs_search_suffix`` to the file name
#     suffixes you want to copy to the Sphinx output.
#     """
#     if not app.config.copydirs_additional_dirs:
#         return {}

#     def copy_by_suffix(src: str, dst: str):
#         if os.path.isdir(src):
#             return
#         if Path(dst).suffix.lower() not in app.config.copydirs_search_suffixes:
#             return
#         shutil.copy2(src, dst)

#     for src in app.config.copydirs_additional_dirs:
#         # This is a value, when resolved, like ".../examples".
#         src_path = os.path.abspath(os.path.join(app.srcdir, src))
#         # Only copy specially-suffixed files like graphics *from directories*.
#         if os.path.isfile(src_path):
#             continue
#         # Copy this directory's contents (subject to suffix), from "root/.../examples"
#         # to "app.outdir/.../examples"
#         # Get the common path (likely the repo), for example, from
#         # /x/repo/docs/build/html
#         # /x/repo/examples
#         # /x/repo/blah/foo
#         base_path = os.path.commonpath([app.outdir, src_path])
#         if app.config.smv_metadata:
#             base_path = app.config.smv_metadata[app.config.smv_current_version][
#                 "basedir"
#             ]
#         logger.debug(
#             f"copy to output, common path for output dir and additional dir: {base_path}"
#         )
#         out_path = os.path.relpath(src_path, base_path)
#         out_path = os.path.join(app.outdir, out_path)

#         logger.info(f"Copying files by suffix from: {src_path}")
#         logger.info(f"  ...to destination: {out_path}")

#         if not os.path.exists(out_path):
#             raise RuntimeError(f"Output directory should already exist: {out_path}")
#         if os.path.isdir(src_path):
#             shutil.copytree(
#                 src_path, out_path, copy_function=copy_by_suffix, dirs_exist_ok=True
#             )
#     return {}
