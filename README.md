# Bug Fix Evaluator

A library and command-line tool for evaluating bug fixes by comparing engineer and AI solutions.

## Features

- Compare bug fixes from various sources:
  - GitHub Pull Requests
  - Git commits
  - Directories containing before/after code
  - Patch files
- Analyze code changes to detect bug patterns and complexity
- Generate detailed evaluation reports in multiple formats:
  - HTML with interactive visualizations
  - JSON for programmatic use
  - Markdown for documentation
  - Plain text for quick viewing
- Extensible scoring system with configurable metrics
- Integrations with development tools:
  - Cursor extension
  - More coming soon!

## Installation

```bash
pip install bug-fix-evaluator
```

To install from source:

```bash
git clone https://github.com/alikayaa/bug_fix_evaluator.git
cd bug_fix_evaluator
pip install -e .
```

## Usage

### Command Line Interface

#### Evaluate from PR URLs

```bash
bug-fix-evaluator pr --engineer https://github.com/alikayaa/repo/pull/123 --ai https://github.com/alikayaa/repo/pull/456
```

#### Evaluate from commit SHAs

```bash
bug-fix-evaluator commit --repo https://github.com/alikayaa/repo.git --engineer abc123 --ai def456
```

#### Evaluate from directories

```bash
bug-fix-evaluator directory --engineer-buggy ./engineer/buggy --engineer-fixed ./engineer/fixed --ai-buggy ./ai/buggy --ai-fixed ./ai/fixed
```

#### Evaluate from patch files

```bash
bug-fix-evaluator patch --engineer ./engineer.patch --ai ./ai.patch
```

### Options

- `-c, --config`: Path to configuration file
- `-o, --output`: Output path for the report
- `-f, --format`: Format of the report (`json`, `html`, `text`, `markdown`)
- `-v, --verbose`: Enable verbose output

### Python API

```python
from bug_fix_evaluator import BugFixEvaluator

# Create an evaluator
evaluator = BugFixEvaluator()

# Evaluate from commits
result = evaluator.evaluate_from_commits(
    repo_url="https://github.com/alikayaa/repo.git",
    engineer_commit="abc123",
    ai_commit="def456",
    report_format="html"
)

print(f"Overall score: {result['overall_score']}")
print(f"Report saved to: {result['report_path']}")
```

## Integrations

### Cursor Extension

The Bug Fix Evaluator includes a Cursor extension for evaluating bug fixes directly within the editor:

- Evaluate bug fixes by comparing Git commits
- View evaluation reports within Cursor
- Configure evaluation metrics and settings

For more details, see the [Cursor integration documentation](./integrations/cursor/README.md).

## Configuration

You can customize the evaluator by providing a configuration file:

```json
{
  "log_level": "INFO",
  "metrics": {
    "weight_correctness": 0.30,
    "weight_completeness": 0.15,
    "weight_pattern_match": 0.10,
    "weight_cleanliness": 0.15,
    "weight_efficiency": 0.15,
    "weight_complexity": 0.15
  },
  "report": {
    "output_dir": "reports",
    "html_template_path": "path/to/custom/template.html"
  }
}
```

## Evaluation Metrics

The evaluator scores bug fixes using several metrics:

1. **Correctness (30%)**: Does the fix correctly address the bug?
2. **Completeness (15%)**: Does the fix address all aspects of the bug?
3. **Pattern Match (10%)**: How well does the fix pattern match the reference?
4. **Cleanliness (15%)**: Does the code follow good practices?
5. **Efficiency (15%)**: Is the fix efficient in terms of code size and complexity?
6. **Complexity (15%)**: Is the fix appropriately complex for the problem?

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 