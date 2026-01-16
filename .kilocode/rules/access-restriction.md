## Brief overview
This rule establishes guidelines for handling .env files to prevent accidental exposure of sensitive configuration data. The rule ensures that .env files are properly ignored and never read, committed, or displayed.

## File handling rules
- Never read .env files directly in code
- Ensure .env files are added to .gitignore
- Do not include .env files in file search results
- Do not display or output .env file contents in any context
- Treat .env files as write-only configuration sources

## Security considerations
- Assume .env files contain sensitive data (API keys, passwords, tokens)
- If .env file access is required, use environment variables or dedicated secret management
- Do not create new .env files without explicit user approval
- Do not modify existing .env files

## Project context
- This rule applies to all operations within the current workspace
- Override this rule only when user explicitly requests .env file operations
