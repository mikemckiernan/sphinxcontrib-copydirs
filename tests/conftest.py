import os
import sphinxcontrib

# Extend the sphinxcontrib namespace package to include the local dev copy.
# The venv's sphinxcontrib namespace may not include the editable source dir.
_repo_root = os.path.dirname(os.path.dirname(__file__))
_copydirs_sphinxcontrib = os.path.join(_repo_root, "sphinxcontrib")
if _copydirs_sphinxcontrib not in sphinxcontrib.__path__:
    sphinxcontrib.__path__.append(_copydirs_sphinxcontrib)
