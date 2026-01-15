## Brief overview
This rule set ensures proper documentation and planning throughout the project lifecycle. It mandates creating and maintaining `description.md` for project overview, plan files in `plans/` for detailed implementation planning, and feature documentation in `features/` for tracking feature evolution.

## Communication style
- When the user requests to create a project or add new features, always confirm the need for documentation and planning.
- Use concise, direct communication; avoid unnecessary verbosity.
- Provide clear status updates on documentation and planning steps.

## Project documentation (description.md)
The `description.md` file serves as the single source of truth for project overview. It should be updated:
- After any significant feature addition or modification
- When configuration options change
- When dependencies are added or updated
- When the project architecture or structure changes
- Before releasing a new version

The `description.md` should include:
- Project purpose and goals
- Target audience
- Key features
- Technology stack
- Setup instructions

## Planning workflow (plans/)
Before starting implementation of any new project or feature:
1. Create or update `description.md` with project overview, goals, and scope
2. Create a detailed step-by-step plan in the `plans/` directory with a timestamped filename (e.g., `MM-DD-YY_HH-MM-SS_feature-name.md`)
3. Ensure the plan is reviewed and approved by the user before proceeding to implementation
4. Use markdown formatting for readability

Plan files should include:
- Task breakdown
- Risks
- Validation criteria

## Feature tracking (features/)
All new features and changes should be documented in markdown files within the `features/` directory. Feature documentation provides a single source of truth for understanding what features exist, their current state, and their evolution over time.

### When to create or update feature documentation
- When adding a new feature to the project
- When modifying an existing feature's behavior
- When removing or deprecating a feature
- After significant refactoring that affects feature functionality
- When completing a feature milestone or release

### Feature file structure
- Store all feature documentation in a `features/` directory at the project root
- Each feature gets its own markdown file named descriptively (e.g., `authentication.md`, `rate-limiting.md`)
- Feature files should include:
  - Feature name and description
  - Current status (planned, in-progress, completed, deprecated)
  - Key implementation details
  - Configuration options
  - Related files and dependencies

### Documentation updates
- Update the relevant feature file when making changes to the feature
- Keep feature descriptions current and accurate
- Remove or mark as deprecated features that are no longer maintained

## Changelog management
After completing any fix, feature, or refactoring, create a changelog entry in the `changelogs/` directory.
- Changelog file naming format: `MM-DD-YY_HH-MM-SS_{name_of_change}.md`
- Each changelog should include: date, description, root cause (for fixes), changes made, files changed, and testing notes
- Commit changelogs separately or with the related code changes

## File naming conventions
- Use lowercase with hyphens for file names (e.g., `proxy-forwarding.md`, `auth-implementation.md`)
- Avoid spaces and special characters in filenames
- Make filenames descriptive and searchable

## Coding best practices
- Follow existing project coding conventions and style guides
- Write clear, self-documenting code with minimal comments unless complex logic requires explanation
- Ensure any new dependencies are justified and documented in `description.md`

## Project context
- This rule applies to all new projects and major feature additions within existing projects
- For minor changes or bug fixes, documentation may be limited to commit messages and inline comments

## Other guidelines
- Keep documentation up-to-date as the project evolves
- Use version control for documentation files to track changes
- Encourage user feedback on documentation and planning to improve future iterations
- If the user provides specific templates or formats for documentation, adhere to those templates
