# Contributing

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Environment setup

Clone the repository and let uv create a virtual environment with the project installed in editable mode:

```bash
git clone https://github.com/mikemckiernan/sphinxcontrib-copydirs.git
cd sphinxcontrib-copydirs
uv sync --all-groups
```

`uv sync` creates `.venv` in the project root and installs the extension plus all development dependencies. You do not need to activate the virtual environment manually — prefix commands with `uv run` and uv handles it.

## Running tests

```bash
uv run --group test pytest
```

## Linting and formatting

Check for style issues:

```bash
uv run --group lint ruff check sphinxcontrib
```

Check formatting without modifying files:

```bash
uv run --group lint ruff format --check sphinxcontrib
```

Apply formatting automatically:

```bash
uv run --group lint ruff format sphinxcontrib
```

## Type checking

```bash
uv run --group typing mypy sphinxcontrib
```

## Submitting changes

1. Fork the repository and create a branch from `main`.
2. Make your changes and ensure all checks pass (`pytest`, `ruff`, `mypy`).
3. Open a pull request against `main`. CI will run the full test matrix across Python 3.10, 3.11, and 3.12.

For broader questions about contributing to extensions in the `sphinxcontrib` namespace, see the [Sphinx contributing guide](https://www.sphinx-doc.org/en/master/internals/contributing).
