copydirs
========

Copy directories into the Sphinx source directory. After the build, copy directories and images to output.

Overview
--------

Assumptions:

- Documentation source is in ``docs/source``
- A directory with valuable information is in ``examples``

With these assumptions, adding the following configuration to ``docs/source/conf.py``
results in copying the ``examples`` directory to ``docs/source/examples`` so the
content can be build.

.. code-block:: python

   extensions = [ "sphinxcontrib.copydirs" ]
   copydirs_additional_dirs = [
       "../../examples",                           # 1
       "../../README.rst",
   ]
   copydirs_file_rename = {
       "README.md": "index.md",                    # 2
   }


1. Specify the directories to copy as relative to the Sphinx source directory.
   You can also specify individual files.
2. If a file with the key is found, ``README.rst``, the file is renamed to the
   value, ``index.rst``, as the extension copies it.

In the `README.md` file, you can add Markdown-style links to subdirectories.
For example, with the following directory structure, the following like
in the `examples/README.md` file resolves to `examples/getting-started/index.md`.

.. code-block:: markdown

   ...see the [getting started](./getting-started) examples.


.. code-block::

   examples
   ├── one-example
   │   ├── 01-notebook.ipynb
   │   ├── 02-notebook.ipynb
   │   └── README.md
   ├── getting-started
   │   ├── 01-notebook.ipynb
   │   ├── 02-notebook.ipynb
   │   └── README.md
   ├── README.md

By default, the extension checks that you have git-ignored the destination
path, such as `docs/source/examples`, and logs a warning if it is not ignored.
To disable the check, set `copydirs_gitignore_check = False`.

Releasing
---------

1. Bump ``version`` in ``pyproject.toml``.
2. Commit and merge to ``main``.
3. Create a release from the command line::

      gh release create v<version> --generate-notes

   For example::

      gh release create v0.4.0 --generate-notes

   GitHub generates release notes automatically from pull request titles and
   commit messages since the last release.

Installing a specific release::

   pip install git+https://github.com/mikemckiernan/sphinxcontrib-copydirs.git@v0.4.0

   uv add git+https://github.com/mikemckiernan/sphinxcontrib-copydirs@v0.4.0


Links
-----

- Source: https://github.com/mikemckiernan/shinxcontrib-copydirs
- Bugs: https://github.com/mikemckiernan/sphinxcontrib-copydirs/issues
