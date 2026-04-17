import logging
import os
import subprocess
from unittest.mock import MagicMock, patch

from sphinxcontrib.copydirs.copydirs import (
    copy_additional_directories,
    copy_with_rename,
    find_index_target,
    is_path_git_ignored,
    resolve_out_path,
    should_warn_not_gitignored,
)


class TestCopyWithRename:
    def test_copies_file_when_file_rename_is_none(self, tmp_path):
        src = tmp_path / "README.md"
        src.write_text("hello")
        dst = tmp_path / "dest" / "README.md"
        dst.parent.mkdir()
        copy_with_rename(str(src), str(dst), None)
        assert dst.read_text() == "hello"

    def test_copies_file_when_key_not_in_file_rename(self, tmp_path):
        src = tmp_path / "CONTRIBUTING.md"
        src.write_text("contrib")
        dst = tmp_path / "dest" / "CONTRIBUTING.md"
        dst.parent.mkdir()
        copy_with_rename(str(src), str(dst), {"README.md": "index.md"})
        assert (tmp_path / "dest" / "CONTRIBUTING.md").read_text() == "contrib"
        assert not (tmp_path / "dest" / "index.md").exists()

    def test_renames_file_when_key_matches(self, tmp_path):
        src = tmp_path / "README.md"
        src.write_text("readme content")
        dst = tmp_path / "dest" / "README.md"
        dst.parent.mkdir()
        copy_with_rename(str(src), str(dst), {"README.md": "index.md"})
        assert (tmp_path / "dest" / "index.md").read_text() == "readme content"
        assert not (tmp_path / "dest" / "README.md").exists()

    def test_empty_file_rename_dict_does_not_rename(self, tmp_path):
        src = tmp_path / "README.md"
        src.write_text("hello")
        dst = tmp_path / "dest" / "README.md"
        dst.parent.mkdir()
        copy_with_rename(str(src), str(dst), {})
        assert (tmp_path / "dest" / "README.md").read_text() == "hello"


class TestResolveOutPath:
    def test_returns_path_under_srcdir(self, tmp_path):
        srcdir = str(tmp_path / "src")
        outdir = str(tmp_path / "out")
        src_path = str(tmp_path / "mylib")
        result = resolve_out_path(src_path, srcdir, outdir)
        assert result == os.path.join(srcdir, "mylib")

    def test_nested_source_path(self, tmp_path):
        srcdir = str(tmp_path / "src")
        outdir = str(tmp_path / "out")
        src_path = str(tmp_path / "docs" / "api")
        result = resolve_out_path(src_path, srcdir, outdir)
        assert result == os.path.join(srcdir, "docs", "api")


class TestFindIndexTarget:
    def test_returns_index_path_when_present(self):
        # refdoc at root level: refpath="" -> normpath("examples/index") -> "examples/index"
        result = find_index_target("intro", "examples", {"examples/index": 1})
        assert result == "examples/index"

    def test_returns_none_when_not_in_all_docs(self):
        result = find_index_target("guide/intro", "examples", {})
        assert result is None

    def test_refdoc_subdir_affects_resolution(self):
        # refdoc="guide/intro" -> refpath="guide"
        # normpath("guide/examples/index") -> "guide/examples/index"
        result = find_index_target("guide/intro", "examples", {"guide/examples/index": 1})
        assert result == "guide/examples/index"

    def test_parent_traversal_in_reftarget(self):
        # normpath(join("guide", "../api", "index")) -> "api/index"
        result = find_index_target("guide/intro", "../api", {"api/index": 1})
        assert result == "api/index"

    def test_dot_slash_reftarget(self):
        # normpath(join("guide", "./examples", "index")) -> "guide/examples/index"
        result = find_index_target("guide/intro", "./examples", {"guide/examples/index": 1})
        assert result == "guide/examples/index"


class TestIsPathGitIgnored:
    def test_returns_true_when_path_is_ignored(self, tmp_path):
        subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
        (tmp_path / ".gitignore").write_text("examples/\n")
        examples = tmp_path / "examples"
        examples.mkdir()
        assert is_path_git_ignored(str(examples), str(tmp_path)) is True

    def test_returns_false_when_path_is_not_ignored(self, tmp_path):
        subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
        (tmp_path / ".gitignore").write_text("# nothing here\n")
        examples = tmp_path / "examples"
        examples.mkdir()
        assert is_path_git_ignored(str(examples), str(tmp_path)) is False

    def test_returns_false_when_no_gitignore(self, tmp_path):
        subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
        examples = tmp_path / "examples"
        examples.mkdir()
        assert is_path_git_ignored(str(examples), str(tmp_path)) is False

    def test_returns_true_when_not_in_git_repo(self, tmp_path):
        # tmp_path has no .git/ — git returns exit code 128
        examples = tmp_path / "examples"
        examples.mkdir()
        assert is_path_git_ignored(str(examples), str(tmp_path)) is True

    def test_returns_true_when_git_not_installed(self, tmp_path):
        with patch(
            "sphinxcontrib.copydirs.copydirs.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            assert is_path_git_ignored(str(tmp_path / "examples"), str(tmp_path)) is True


class TestShouldWarnNotGitignored:
    def test_returns_false_when_check_disabled(self, tmp_path):
        # Short-circuit: is_path_git_ignored is never called when check_enabled=False
        assert should_warn_not_gitignored(str(tmp_path), str(tmp_path), False) is False

    def test_returns_false_when_check_enabled_and_path_is_ignored(self, tmp_path):
        with patch(
            "sphinxcontrib.copydirs.copydirs.is_path_git_ignored", return_value=True
        ):
            assert should_warn_not_gitignored(str(tmp_path), str(tmp_path), True) is False

    def test_returns_true_when_check_enabled_and_path_not_ignored(self, tmp_path):
        with patch(
            "sphinxcontrib.copydirs.copydirs.is_path_git_ignored", return_value=False
        ):
            assert should_warn_not_gitignored(str(tmp_path), str(tmp_path), True) is True

    def test_returns_false_when_check_enabled_and_not_in_git_repo(self, tmp_path):
        # is_path_git_ignored returns True when outside a repo (suppresses warning)
        with patch(
            "sphinxcontrib.copydirs.copydirs.is_path_git_ignored", return_value=True
        ):
            assert should_warn_not_gitignored(str(tmp_path), str(tmp_path), True) is False


class TestCopyAdditionalDirectoriesGitignoreWarning:
    """Verifies that copy_additional_directories warns when the destination
    is not covered by .gitignore."""

    def _make_app(self, srcdir: str, outdir: str, dirs: list[str]) -> object:
        app = MagicMock()
        app.srcdir = srcdir
        app.outdir = outdir
        app.config.copydirs_additional_dirs = dirs
        app.config.copydirs_file_rename = None
        app.config.copydirs_gitignore_check = True
        return app

    def _setup_repo(self, tmp_path: object, gitignore_content: str) -> tuple:
        """Return (srcdir, outdir, src) paths after creating a minimal repo."""
        subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
        (tmp_path / ".gitignore").write_text(gitignore_content)
        srcdir = tmp_path / "docs" / "source"
        srcdir.mkdir(parents=True)
        outdir = tmp_path / "docs" / "source" / "_build"
        outdir.mkdir()
        src = tmp_path / "examples"
        src.mkdir()
        (src / "readme.txt").write_text("hello")
        return str(srcdir), str(outdir), str(src)

    def test_warns_when_destination_not_gitignored(self, tmp_path, caplog):
        srcdir, outdir, _ = self._setup_repo(tmp_path, "")  # empty .gitignore
        app = self._make_app(srcdir, outdir, ["../../examples"])

        with caplog.at_level(logging.WARNING, logger="sphinxcontrib.copydirs.copydirs"):
            copy_additional_directories(app, None)

        assert any("not git-ignored" in msg for msg in caplog.messages)

    def test_no_warning_when_destination_is_gitignored(self, tmp_path, caplog):
        srcdir, outdir, _ = self._setup_repo(tmp_path, "examples/\n")
        app = self._make_app(srcdir, outdir, ["../../examples"])

        with caplog.at_level(logging.WARNING, logger="sphinxcontrib.copydirs.copydirs"):
            copy_additional_directories(app, None)

        assert not any("not git-ignored" in msg for msg in caplog.messages)

    def test_no_warning_when_not_in_git_repo(self, tmp_path, caplog):
        # No git init — tmp_path is not a repo
        srcdir = tmp_path / "docs" / "source"
        srcdir.mkdir(parents=True)
        outdir = tmp_path / "docs" / "source" / "_build"
        outdir.mkdir()
        src = tmp_path / "examples"
        src.mkdir()
        (src / "readme.txt").write_text("hello")
        app = self._make_app(str(srcdir), str(outdir), ["../../examples"])

        with caplog.at_level(logging.WARNING, logger="sphinxcontrib.copydirs.copydirs"):
            copy_additional_directories(app, None)

        assert not any("not git-ignored" in msg for msg in caplog.messages)

    def test_warns_for_file_copy_when_not_gitignored(self, tmp_path, caplog):
        subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
        (tmp_path / ".gitignore").write_text("")  # nothing ignored

        srcdir = tmp_path / "docs" / "source"
        srcdir.mkdir(parents=True)
        outdir = tmp_path / "docs" / "source" / "_build"
        outdir.mkdir()
        src_file = tmp_path / "README.md"
        src_file.write_text("# hello")

        app = self._make_app(str(srcdir), str(outdir), ["../../README.md"])

        with caplog.at_level(logging.WARNING, logger="sphinxcontrib.copydirs.copydirs"):
            copy_additional_directories(app, None)

        assert any("not git-ignored" in msg for msg in caplog.messages)

    def test_no_warning_when_gitignore_check_is_disabled(self, tmp_path, caplog):
        srcdir, outdir, _ = self._setup_repo(tmp_path, "")  # empty .gitignore
        app = self._make_app(srcdir, outdir, ["../../examples"])
        app.config.copydirs_gitignore_check = False

        with caplog.at_level(logging.WARNING, logger="sphinxcontrib.copydirs.copydirs"):
            copy_additional_directories(app, None)

        assert not any("not git-ignored" in msg for msg in caplog.messages)
