## Brief overview
This rule set focuses on ensuring proper documentation and planning before implementing new projects or features. It mandates creating a description.md file for project documentation and plan files in the `plans/` directory for detailed planning before any implementation work begins.

## Communication style
- When the user requests to create a project or add new features, always confirm the need for documentation and planning.
- Use concise, direct communication; avoid unnecessary verbosity.
- Provide clear status updates on documentation and planning steps.

## Development workflow
- Before starting implementation of any new project or feature, create or update `description.md` with project overview, goals, and scope.
- Create a detailed step-by-step plan in the `plans/` directory with a descriptive filename (e.g., `feature-name.md`).
- Ensure the plan is reviewed and approved by the user before proceeding to implementation.
- Use markdown formatting for readability.

## Coding best practices
- Follow existing project coding conventions and style guides.
- Write clear, self-documenting code with minimal comments unless complex logic requires explanation.
- Ensure any new dependencies are justified and documented in `description.md`.

## Project context
- This rule applies to all new projects and major feature additions within existing projects.
- For minor changes or bug fixes, documentation may be limited to commit messages and inline comments.
- The `description.md` should include: project purpose, target audience, key features, technology stack, and setup instructions.
- Plan files in `plans/` directory should include: task breakdown, risks, and validation criteria.

## Changelog management
- After completing any fix, feature, or refactoring, create a changelog entry in the `changelogs/` directory.
- Changelog file naming format: `MM-DD-YY_HH-MM-SS_{name_of_change}.md`
- Each changelog should include: date, description, root cause (for fixes), changes made, files changed, and testing notes.
- Commit changelogs separately or with the related code changes.

## Other guidelines
- Keep documentation up-to-date as the project evolves.
- Use version control for documentation files to track changes.
- Encourage user feedback on documentation and planning to improve future iterations.
- If the user provides specific templates or formats for documentation, adhere to those templates.