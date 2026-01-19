# CLAUDE.md - Bug Fix Evaluator

This file provides guidance for AI assistants working with this codebase.

## Project Overview

**Bug Fix Evaluator** is a tool for evaluating bug fixes by comparing local code changes against approved PR solutions. It leverages Cursor IDE's agent mode for AI-powered code analysis and generates comprehensive evaluation reports.

**Key Capabilities:**
- Compare local bug fixes against approved GitHub PR solutions
- Generate evaluation reports (HTML, Markdown, JSON, Text)
- Integrate with Cursor IDE through a VS Code extension
- Evaluate both remote GitHub PRs and local repositories

## Directory Structure

```
bug_fix_evaluator/
├── src/bug_fix_cursor_evaluator/    # Main Python package
│   ├── __init__.py                  # Package exports (version 0.1.0)
│   ├── cli.py                       # CLI entry point (bug-fix-evaluator command)
│   ├── cursor_agent.py              # CursorAgentEvaluator - main orchestrator
│   ├── evaluator.py                 # Core evaluation logic
│   ├── repository.py                # RepositoryHandler - GitHub API integration
│   ├── reporter.py                  # ReportGenerator - report generation
│   ├── results.py                   # Result loading and processing
│   ├── utils.py                     # Utilities (logging, git, file watching)
│   └── templates/                   # Jinja2 report templates
│       ├── report.html
│       ├── report.md
│       └── report.txt
├── extension/                       # VS Code/Cursor extension
│   ├── extension.js                 # Extension entry point
│   ├── package.json                 # Extension manifest
│   └── *.vsix                       # Compiled extension package
├── tests/                           # Test suite
│   └── test_cursor_evaluator.py     # Unit tests
├── docs/                            # Documentation
│   └── extension_installation.md
├── setup.py                         # Python package configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # Main documentation
```

## Core Modules

### `cli.py` - Command Line Interface
Entry point for the `bug-fix-evaluator` CLI tool. Provides these commands:
- `prepare` - Prepare a GitHub PR for evaluation
- `prepare-local` - Prepare a local repository PR
- `wait` - Wait for evaluation results
- `report` - Generate report from results
- `evaluate` - Combined prepare + wait workflow
- `evaluate-local` - Combined prepare-local + wait workflow

### `cursor_agent.py` - Main Orchestrator
`CursorAgentEvaluator` class that:
- Parses PR URLs
- Fetches PR diffs from GitHub
- Creates instruction files for Cursor agent
- Manages evaluation workflow

### `repository.py` - GitHub Integration
`RepositoryHandler` class for:
- Parsing GitHub PR URLs via regex
- Fetching PR diffs via GitHub API
- Supporting optional GitHub token authentication

### `reporter.py` - Report Generation
`ReportGenerator` class that:
- Generates reports in multiple formats (HTML, Markdown, JSON, Text)
- Uses Jinja2 templating
- Creates timestamped output files

### `results.py` - Result Processing
Functions for:
- `load_cursor_results()` - Load and validate JSON results
- `process_results()` - Transform results into report format
- `get_metric_weight()` - Return predefined weights for metrics

### `utils.py` - Utilities
Contains:
- `LoggerManager` - Centralized logging setup
- `GitUtils` - Git operations
- `FileWatcher` - File monitoring with timeout
- `setup_logger()` - Convenience logging function

## Evaluation Criteria

The tool evaluates bug fixes against these weighted criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 30% | Does the fix correctly address the bug? |
| Completeness | 15% | Does the fix cover all edge cases? |
| Code Quality | 15% | Is the code clean and well-structured? |
| Efficiency | 15% | Is the fix performant? |
| Testing | 10% | Does it include appropriate tests? |
| Documentation | 15% | Is the fix well-documented? |

## Development Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Running the CLI
```bash
# Prepare PR for evaluation
bug-fix-evaluator prepare https://github.com/owner/repo/pull/123 --open-cursor

# Prepare local PR
bug-fix-evaluator prepare-local /path/to/repo 123

# Generate report from results
bug-fix-evaluator report path/to/results.json --format html --open

# Full evaluation workflow
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --report --open-cursor
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/bug_fix_cursor_evaluator
```

### Building the VS Code Extension
```bash
cd extension
npm install
npm run package
# Creates bug-fix-evaluator-0.1.0.vsix
```

## Code Conventions

### Python Style
- Python 3.8+ compatibility required
- Use type hints for function signatures
- Follow PEP 8 style guidelines
- Use docstrings for public functions and classes
- Import order: standard library, third-party, local

### Logging
- Use `logging` module, not print statements (except for CLI user output)
- Get logger via `logging.getLogger(__name__)`
- Use `setup_logger()` from utils for configuration

### Error Handling
- Raise specific exceptions with descriptive messages
- Use try/except with proper error logging
- Return meaningful error codes from CLI (sys.exit(1) on failure)

### File Organization
- Keep modules focused on single responsibilities
- Public API exports defined in `__init__.py`
- Templates stored in `templates/` directory

## VS Code Extension

The extension (`extension/extension.js`) provides three commands:
- `bugFixEvaluator.evaluatePR` - Evaluate GitHub PR
- `bugFixEvaluator.evaluateLocalPR` - Evaluate local PR
- `bugFixEvaluator.showReport` - View evaluation report

Extension configuration options (in VS Code settings):
- `bugFixEvaluator.pythonPath` - Python executable path
- `bugFixEvaluator.outputDirectory` - Results/reports storage
- `bugFixEvaluator.githubToken` - GitHub API authentication
- `bugFixEvaluator.reportFormat` - Default report format
- `bugFixEvaluator.watchTimeout` - Results timeout in seconds

## Environment Variables

- `GITHUB_TOKEN` - GitHub API token for authentication (optional, enables higher rate limits)

## Dependencies

### Python (from setup.py)
- `requests>=2.25.0` - HTTP client for GitHub API
- `jinja2>=3.0.0` - Template engine for reports

### Development (from requirements.txt)
- `GitPython>=3.1.31` - Git operations
- `pytest>=7.3.1` - Testing framework
- `pylint`, `black`, `flake8` - Code quality tools

## Common Tasks for AI Assistants

### Adding a New Report Format
1. Create template in `src/bug_fix_cursor_evaluator/templates/`
2. Update `ReportGenerator.generate_report()` in `reporter.py`
3. Add format option to CLI in `cli.py`

### Adding a New CLI Command
1. Add subparser in `parse_args()` in `cli.py`
2. Create handler function
3. Add command dispatch in `main()`

### Modifying Evaluation Criteria
1. Update weights in `get_metric_weight()` in `results.py`
2. Update report templates if needed
3. Update documentation

### Updating the VS Code Extension
1. Modify `extension/extension.js`
2. Update `extension/package.json` if adding commands/settings
3. Rebuild with `npm run package`

## Repository Information

- **Author:** Ali Kaya
- **License:** MIT
- **Python Version:** 3.8+
- **Repository:** https://github.com/alikayaa/bug_fix_evaluator
