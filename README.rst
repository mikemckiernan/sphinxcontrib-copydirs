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
       "README.rst": "index.rst",                  # 2
   }
   copydirs_search_suffix = [".png"]               # 3


1. Specify the directories to copy as relative to the Sphinx source directory.
   You can also specify individual files.
2. If a file with the key is found, ``README.rst``, the file is renamed to the
   value, ``index.rst``, as the extension copies it.
3. If the directory to copy has subdirectories for files like images, then
   copy the files that match the suffix and their directories to the Sphinx
   build output directory. The default value is ``[ ".png", ".tif", ".jpg", ".svg"]``.

Links
-----

- Source: https://github.com/mikemckiernan/shinxcontrib-copydirs
- Bugs: https://github.com/mikemckiernan/sphinxcontrib-copydirs/issues
