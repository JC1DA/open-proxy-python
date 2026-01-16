## Brief overview
This rule ensures code is properly formatted before task completion when using automatic code formatters like Black or Ruff. The project uses Ruff for code formatting and linting.

## Code formatting requirements
- Always run code formatters before finishing any task that involves code changes
- Check for `ruff.toml` or `pyproject.toml` to determine if Ruff is configured
- Check for `pyproject.toml` with `[tool.black]` section to determine if Black is configured
- Run formatters on all modified files, not just the main entry point

## Formatting commands
- For Ruff: `ruff format .` or `ruff format <file_path>`
- For Black: `black .` or `black <file_path>`
- Run formatters from the project root directory

## Task completion checklist
- [ ] Code changes implemented
- [ ] Code formatted with appropriate formatter (Ruff/Black)
- [ ] No formatting errors or warnings
- [ ] Task marked complete

## Project context
- This project uses Ruff for code formatting (evidenced by `ruff.toml` in project root)
- Ruff configuration should be respected when formatting code
- Format before creating changelog entries or finalizing documentation
