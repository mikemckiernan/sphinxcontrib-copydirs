# tests/test_integration.py
import logging
import shutil
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


def _make_sphinx_project(srcdir: Path) -> None:
    """Write the minimum files Sphinx requires to initialise."""
    srcdir.mkdir(parents=True, exist_ok=True)
    (srcdir / "conf.py").write_text("extensions = ['sphinxcontrib.copydirs']\n")
    (srcdir / "index.rst").write_text("Root\n====\n")


class TestDirectoryCopyIntegration:
    """copydirs copies a directory from outside srcdir into srcdir at build time."""

    def test_directory_is_copied_into_srcdir(self, tmp_path):
        srcdir = tmp_path / "src"
        _make_sphinx_project(srcdir)

        external = tmp_path / "external"
        external.mkdir()
        (external / "readme.txt").write_text("hello from external\n")

        app = SphinxTestApp(
            srcdir=srcdir,
            confoverrides={"copydirs_additional_dirs": [str(external)]},
        )
        try:
            app.build()
            copied = srcdir / "external" / "readme.txt"
            assert copied.exists(), f"Expected {copied} to exist after copydirs ran"
            assert copied.read_text() == "hello from external\n"
        finally:
            app.cleanup()

    def test_file_is_renamed_during_copy(self, tmp_path):
        srcdir = tmp_path / "src"
        _make_sphinx_project(srcdir)

        external = tmp_path / "external"
        external.mkdir()
        (external / "README.md").write_text("# External Readme\n")
        (external / "other.md").write_text("other content\n")

        app = SphinxTestApp(
            srcdir=srcdir,
            confoverrides={
                "copydirs_additional_dirs": [str(external)],
                "copydirs_file_rename": {"README.md": "index.md"},
            },
        )
        try:
            app.build()
            dest = srcdir / "external"
            assert (dest / "index.md").exists(), "README.md should have been renamed to index.md"
            assert not (dest / "README.md").exists(), "README.md should not exist at destination"
            assert (dest / "other.md").exists(), "other.md should be copied unchanged"
        finally:
            app.cleanup()


class TestMissingSourceIntegration:
    """A missing source path in copydirs_additional_dirs is logged and skipped."""

    def test_missing_source_does_not_raise(self, tmp_path, caplog):
        srcdir = tmp_path / "src"
        _make_sphinx_project(srcdir)
        nonexistent = str(tmp_path / "does_not_exist")

        with caplog.at_level(logging.INFO, logger="sphinxcontrib.copydirs.copydirs"):
            app = SphinxTestApp(
                srcdir=srcdir,
                confoverrides={"copydirs_additional_dirs": [nonexistent]},
            )
            try:
                app.build()
            finally:
                app.cleanup()

        assert any(
            "does not exist" in record.message
            for record in caplog.records
            if record.name == "sphinxcontrib.copydirs.copydirs"
        ), (
            f"Expected 'does not exist' in copydirs log. "
            f"Got: {[r.message for r in caplog.records]}"
        )


class TestDirectoryLinkResolutionIntegration:
    """resolve_directory_link resolves :doc:`dir` to dir/index when dir/index is in all_docs."""

    def _setup_srcdir(self, tmp_path: Path) -> Path:
        """Copy the test-root into tmp_path and return the srcdir path."""
        roots_dir = Path(__file__).parent / "roots" / "test-dir-link"
        srcdir = tmp_path / "src"
        shutil.copytree(roots_dir, srcdir)
        return srcdir

    def test_directory_link_resolves_without_warning(self, tmp_path):
        srcdir = self._setup_srcdir(tmp_path)
        app = SphinxTestApp(srcdir=srcdir)
        try:
            app.build()
            warning_output = app.warning.getvalue()
            assert "unknown document" not in warning_output, (
                f"Expected directory link to be resolved silently. "
                f"Got warnings: {warning_output!r}"
            )
        finally:
            app.cleanup()

    def test_directory_link_produces_html_href(self, tmp_path):
        srcdir = self._setup_srcdir(tmp_path)
        app = SphinxTestApp(srcdir=srcdir)
        try:
            app.build()
            doc1_html = (Path(app.outdir) / "doc1.html").read_text(encoding="utf-8")
            assert "examples/index.html" in doc1_html, (
                f"Expected a link to examples/index.html in doc1.html. "
                f"Snippet: {doc1_html[doc1_html.find('<body'):doc1_html.find('</body>')][:500]}"
            )
        finally:
            app.cleanup()
