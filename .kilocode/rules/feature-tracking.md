## Brief overview
This rule ensures that all new features and changes are documented in markdown files within a `features` directory. Feature documentation provides a single source of truth for understanding what features exist, their current state, and their evolution over time. Additionally, the main `description.md` file should be kept up-to-date with all project changes.

## When to create or update feature documentation
- When adding a new feature to the project
- When modifying an existing feature's behavior
- When removing or deprecating a feature
- After significant refactoring that affects feature functionality
- When completing a feature milestone or release

## When to update description.md
- After any significant feature addition or modification
- When configuration options change
- When dependencies are added or updated
- When the project architecture or structure changes
- Before releasing a new version

## Feature file structure
- Store all feature documentation in a `features/` directory at the project root
- Each feature gets its own markdown file named descriptively (e.g., `authentication.md`, `rate-limiting.md`)
- Feature files should include:
  - Feature name and description
  - Current status (planned, in-progress, completed, deprecated)
  - Key implementation details
  - Configuration options
  - Related files and dependencies

## Documentation updates
- Update the relevant feature file when making changes to the feature
- Add a changelog entry in `changelogs/` directory for significant changes
- Keep feature descriptions current and accurate
- Remove or mark as deprecated features that are no longer maintained

## File naming conventions
- Use lowercase with hyphens for feature file names (e.g., `proxy-forwarding.md`)
- Avoid spaces and special characters in filenames
- Make filenames descriptive and searchable