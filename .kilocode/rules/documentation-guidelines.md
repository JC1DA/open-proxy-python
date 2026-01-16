## Brief overview
This rule set ensures proper documentation and planning throughout the project lifecycle. It mandates creating and maintaining `description.md` for project overview, plan files in `plans/` for detailed implementation planning, and feature documentation in `features/` for tracking feature evolution.

## Mandatory Documentation Checklist
Before any task is considered complete, the following MUST be completed:
- [ ] Plan created in `plans/` directory (before implementation)
- [ ] Feature documentation created/updated in `features/` directory (for each feature)
- [ ] Changelog entry created in `changelogs/` directory (after completion)
- [ ] `description.md` updated if project scope or architecture changed

## Communication style
- When the user requests to create a project or add new features, always confirm the need for documentation and planning.
- Use concise, direct communication; avoid unnecessary verbosity.
- Provide clear status updates on documentation and planning steps.

## Project documentation (description.md)
The `description.md` file serves as the single source of truth for project overview. It MUST be updated:
- After any significant feature addition or modification
- When configuration options change
- When dependencies are added or updated
- When the project architecture or structure changes
- Before releasing a new version

The `description.md` MUST include:
- Project purpose and goals
- Target audience
- Key features
- Technology stack
- Setup instructions

## Planning workflow (plans/)

**Planning is MANDATORY, not optional.** Before starting implementation of any new project or feature:

1. Create or update `description.md` with project overview, goals, and scope
2. Create a detailed step-by-step plan in the `plans/` directory with a timestamped filename (e.g., `MM-DD-YY_HH-MM-SS_feature-name.md`)
3. Ensure the plan is reviewed and approved by the user before proceeding to implementation
4. Use markdown formatting for readability

Plan files MUST include:
- Task breakdown
- Risks
- Validation criteria

**No implementation work should begin without an approved plan.**

## Feature tracking (features/)
All new features and changes MUST be documented in markdown files within the `features/` directory. Feature documentation provides a single source of truth for understanding what features exist, their current state, and their evolution over time.

### When to create or update feature documentation
Feature documentation MUST be created or updated:
- When adding a new feature to the project
- When modifying an existing feature's behavior
- When removing or deprecating a feature
- After significant refactoring that affects feature functionality
- When completing a feature milestone or release

### Feature file structure
- Store all feature documentation in a `features/` directory at the project root
- Each feature MUST have its own markdown file named descriptively (e.g., `authentication.md`, `rate-limiting.md`)
- Feature files MUST include:
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

**Changelog entries are REQUIRED for all completed work.** After completing any fix, feature, or refactoring, create a changelog entry in the `changelogs/` directory.

- Changelog file naming format: `MM-DD-YY_HH-MM-SS_{name_of_change}.md`
- Each changelog MUST include: date, description, root cause (for fixes), changes made, files changed, and testing notes
- Commit changelogs separately or with the related code changes

**No task is complete without a changelog entry.**

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

## Mode-specific requirements

### All modes (architect, code, debug, orchestrator)
- MUST ensure proper documentation is created for all work
- MUST follow the mandatory documentation checklist
- MUST not consider a task complete without documentation

### Orchestrator mode
When delegating subtasks, orchestrator mode MUST:
- Ensure documentation requirements are communicated to delegated modes
- Verify that all delegated tasks include proper documentation
- Track documentation completion as part of overall task management
- Include documentation steps in the task breakdown

## Other guidelines
- Keep documentation up-to-date as the project evolves
- Use version control for documentation files to track changes
- Encourage user feedback on documentation and planning to improve future iterations
- If the user provides specific templates or formats for documentation, adhere to those templates
