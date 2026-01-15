# Open Proxy Python

A Python project for open proxy functionality.

## Development Setup

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting.

### Configuration

- **Line length**: 120 characters
- **Indentation**: 4 spaces
- **Quote style**: Double quotes
- **Target Python version**: 3.11+

### Auto-formatting on Save

VSCode is configured to automatically format Python files on save using Ruff. The configuration is in `.vscode/settings.json`.

### Installation

1. Install [uv](https://github.com/astral-sh/uv) if not already installed:
   ```bash
   pip install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Ruff is installed as a dev dependency.

### Usage

- Format all files:
  ```bash
  ruff format .
  ```

- Lint all files:
  ```bash
  ruff check .
  ```

- Fix lint issues:
  ```bash
  ruff check --fix .
  ```

### Configuration Files

- `ruff.toml`: Ruff configuration with line-length = 120 and other settings.
- `pyproject.toml`: Project metadata and dev dependencies.
- `.vscode/settings.json`: VSCode settings for format on save.

### Notes

- The Ruff formatter will automatically wrap lines longer than 120 characters.
- Unused imports and variables are ignored (F401, F841) for convenience.
- Missing docstrings are ignored (D) for now.
