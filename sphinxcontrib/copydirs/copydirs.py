import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from docutils.nodes import inline
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.nodes import make_refnode

logger = logging.getLogger(__name__)


def copy_with_rename(src: str, dst: str, file_rename: dict[str, str] | None) -> None:
    """Copy src to dst, renaming the file if its name appears in file_rename."""
    src_name = Path(src).name
    if file_rename and src_name in file_rename:
        dst = str(Path(dst).parent / file_rename[src_name])
        logger.debug(f"Renaming source file: {src_name} to {dst}")
    shutil.copy2(src, str(dst))


def resolve_out_path(src_path: str, srcdir: str, outdir: str) -> str:
    """Return the destination path inside srcdir that mirrors src_path."""
    base_path = os.path.commonpath([outdir, src_path])
    return os.path.join(srcdir, os.path.relpath(src_path, base_path))


def find_index_target(refdoc: str, reftarget: str, all_docs: dict) -> str | None:
    """Return the normalized index path if it exists in all_docs, else None."""
    refpath = os.path.dirname(refdoc)
    idx = os.path.normpath(os.path.join(refpath, reftarget, "index"))
    return idx if idx in all_docs else None


def is_path_git_ignored(path: str, cwd: str) -> bool:
    """Return True if git considers path to be ignored.

    Returns True (suppressing any warning) when git is not installed
    or cwd is not inside a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "check-ignore", "-q", path],
            capture_output=True,
        )
        # 0 = ignored, 1 = not ignored, 128+ = git error/not a repo;
        # treat any non-1 code as "no warning" to avoid false positives on git errors
        return result.returncode != 1
    except FileNotFoundError:
        return True


def should_warn_not_gitignored(out_path: str, srcdir: str, check_enabled: bool) -> bool:
    """Return True if the gitignore check is enabled and out_path is not git-ignored."""
    return check_enabled and not is_path_git_ignored(out_path, srcdir)


# Paths are relative to the docs/source directory.
def copy_additional_directories(app: Sphinx, _: Any) -> None:
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

    for src in app.config.copydirs_additional_dirs:
        src_path = os.path.abspath(os.path.join(app.srcdir, src))
        if not os.path.exists(src_path):
            logger.info(f"The file to copy does not exist, skipping: {src_path}")
            continue

        out_path = resolve_out_path(src_path, app.srcdir, app.outdir)

        logger.debug(
            "copy to source, common path for output dir and additional dir: ",
            f"{os.path.commonpath([app.outdir, src_path])}",
        )
        logger.info(f"Copying source documentation from: {src_path}")
        logger.info(f"  ...to destination: {out_path}")

        if os.path.exists(out_path) and os.path.isdir(out_path):
            shutil.rmtree(out_path, ignore_errors=True)
        if os.path.exists(out_path) and os.path.isfile(out_path):
            os.unlink(out_path)

        if os.path.isdir(src_path):
            shutil.copytree(
                src_path,
                out_path,
                copy_function=lambda s, d: copy_with_rename(s, d, app.config.copydirs_file_rename),
            )
        else:
            shutil.copyfile(src_path, out_path)

        # app.srcdir is inside the repo tree, so git walks up to find the root and
        # all relevant .gitignore files. If srcdir were outside the repo this check
        # would silently suppress the warning (git returns exit code 128).
        if should_warn_not_gitignored(out_path, app.srcdir, app.config.copydirs_gitignore_check):
            logger.warning(
                "Copied destination is not git-ignored and can be accidentally committed: %s",
                out_path,
            )


# If someone makes a Markdown link to a directory, like [examples](./examples/),
# then attempt to resolve that to the target + "index.md".
def resolve_directory_link(
    app: Sphinx,
    env: BuildEnvironment,
    node: pending_xref,
    contnode: inline,
) -> inline | None:
    """Resolve a Markdown link to a directory, like [examples](./examples),
    by checking for an index file in the directory.

    After a README.md file is renamed to index.md in the source tree, the
    link should be OK.
    """
    if "refdoc" not in node:
        return None
    idx_target = find_index_target(node["refdoc"], node["reftarget"], env.all_docs)
    if idx_target is None:
        return None
    return make_refnode(app.builder, node["refdoc"], idx_target, None, contnode)
