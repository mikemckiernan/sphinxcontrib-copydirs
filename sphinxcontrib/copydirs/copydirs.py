import errno
import os
import shutil
import logging

from pathlib import Path
from typing import cast

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.addnodes import pending_xref
from sphinx.util.nodes import make_refnode
from sphinx.domains.std import StandardDomain
from docutils import nodes
from docutils.nodes import inline

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
        if "smv_metadata" in app.config and len(app.config.smv_metadata) > 0:
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


# If someone makes a Markdown link to a directory, like [examples](./examples/),
# then attempt to resolve that to the target + "index.md".
def resolve_directory_link(
    app: Sphinx, env: BuildEnvironment, node: pending_xref, contnode: inline
):
    """Resolve a Markdown link to a directory, like [examples](./examples),
    by checking for an index file in the directory.

    After a README.md file is renamed to index.md in the source tree, the
    link should be OK.
    """
    if "refdoc" not in node:
        return None
    refpath = os.path.dirname(node["refdoc"])
    idx_target = os.path.join(refpath, node["reftarget"], "index")
    idx_target = os.path.normpath(idx_target)
    if idx_target not in env.all_docs:
        return None

    fromdoc = node["refdoc"]
    return make_refnode(app.builder, fromdoc, idx_target, None, contnode)
