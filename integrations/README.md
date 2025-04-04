# Bug Fix Evaluator Integrations

This directory contains integrations of the Bug Fix Evaluator with various tools and platforms.

## Available Integrations

### Cursor Extension

A Cursor extension for evaluating bug fixes directly within the editor.

- **Directory**: [cursor](./cursor)
- **Features**: 
  - Evaluate bug fixes by comparing Git commits
  - View evaluation reports within Cursor
  - Configure evaluation metrics and settings

### Future Integrations

We plan to add more integrations in the future:

- **VS Code Extension**: Similar to the Cursor extension, but for VS Code
- **Windsurf Integration**: Integration with the Windsurf AI coding assistant
- **Web Interface**: A standalone web application for evaluation
- **CI/CD Integration**: Run evaluations as part of continuous integration

## Developing Integrations

To create a new integration, follow these steps:

1. Create a new directory under `integrations/` for your integration
2. Use the core library from `src/bug_fix_evaluator/` in your integration
3. Create an adapter in `src/bug_fix_evaluator/integrations/` if needed
4. Add documentation and examples for your integration
5. Update this README with information about your integration

For more details, refer to the [development guidelines](../docs/development.md). 