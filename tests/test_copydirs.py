import os
import pytest
from sphinxcontrib.copydirs.copydirs import copy_with_rename, resolve_out_path, find_index_target


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
