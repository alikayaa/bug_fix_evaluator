# Bug-Fix PR Evaluation System

A system that evaluates AI-generated bug-fix Pull Requests (PRs) by comparing them to engineer-created PRs for the same bug. This tool provides objective metrics to assess code correctness, readability, quality, problem-solving accuracy, and similarity.

## Overview

This evaluation system is designed to:

1. **Analyze PRs**: Parse and compare two PRs (AI-generated vs. engineer-created) fixing the same bug.
2. **Run Tests**: Verify that the bug is properly fixed by running test suites.
3. **Analyze Code Quality**: Measure code quality metrics like complexity, style adherence, and maintainability.
4. **Score Solutions**: Provide a composite score with detailed breakdowns for each metric.
5. **Generate Reports**: Create comprehensive evaluation reports with actionable insights.

## Installation

```bash
# Clone the repository
git clone https://github.com/alikayaa/bug-fix-evaluator.git
cd bug-fix-evaluator

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python src/evaluator.py --engineer-pr <engineer-pr> --ai-pr <ai-pr> --output report.json
```

Where:
- `<engineer-pr>` is either a GitHub PR URL or a path to a JSON file with PR data
- `<ai-pr>` is either a GitHub PR URL or a path to a JSON file with PR data

### Custom Weights

You can customize the weights for different metrics:

```bash
python src/evaluator.py --engineer-pr <engineer-pr> --ai-pr <ai-pr> --weights '{"correctness": 0.4, "readability": 0.1, "quality": 0.2, "problem_solving": 0.2, "similarity": 0.1}'
```

## Metrics

The system evaluates PRs based on the following metrics:

1. **Correctness (30%)**: 
   - Does the code compile and pass tests?
   - Is the bug fixed correctly?

2. **Readability (15%)**:
   - Does the code follow style guidelines?
   - Is the code easy to understand?

3. **Quality (20%)**:
   - Is the code well-structured and efficient?
   - Does it adhere to best practices?
   - Is the complexity reasonable?

4. **Problem Solving (25%)**:
   - Does the approach address the core issue?
   - Is the solution robust and complete?

5. **Similarity (10%)**:
   - How similar is the AI solution to the engineer's solution?

## Example Output

```json
{
  "scores": {
    "correctness": 0.85,
    "readability": 0.92,
    "quality": 0.78,
    "problem_solving": 0.80,
    "similarity": 0.67
  },
  "final_score": 0.82,
  "weights": {
    "correctness": 0.30,
    "readability": 0.15,
    "quality": 0.20,
    "problem_solving": 0.25,
    "similarity": 0.10
  },
  "details": {
    "engineer_pr": {
      "url": "https://github.com/owner/repo/pull/123",
      "title": "Fix null pointer exception in user authentication",
      "author": "engineer",
      "created_at": "2023-05-15T10:30:45Z",
      "merged_at": "2023-05-16T14:20:10Z"
    },
    "ai_pr": {
      "url": "https://github.com/owner/repo/pull/456",
      "title": "Fix authentication null pointer bug",
      "author": "ai-assistant",
      "created_at": "2023-05-15T09:45:30Z"
    },
    "improvement_suggestions": [
      "Refactor code to improve structure and efficiency"
    ]
  }
}
```

## Requirements

- Python 3.8+
- Git
- GitHub API token (optional, for higher rate limits)

## Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token for API requests (optional)

## HTML Reports

The Bug Fix Evaluator can now generate modern, visually appealing HTML reports from the JSON evaluation data. This makes it easier to understand and share the evaluation results.

### Generating HTML Reports

You can generate HTML reports using one of these methods:

1. **Using the CLI with the `--html` flag**:
   ```bash
   python -m src.evaluator --engineer-pr path/to/engineer_pr.json --ai-pr path/to/ai_pr.json --output report.json --html
   ```

2. **Using the Python API**:
   ```python
   from src.evaluator import BugFixEvaluator
   
   evaluator = BugFixEvaluator("path/to/engineer_pr.json", "path/to/ai_pr.json")
   report = evaluator.run_evaluation("report.json", generate_html=True)
   ```

3. **Converting an existing JSON report**:
   ```python
   from src.evaluator import BugFixEvaluator
   
   evaluator = BugFixEvaluator("", "")  # Placeholder values
   html_path = evaluator.generate_html_report("path/to/existing/report.json")
   ```

### HTML Report Features

The HTML report includes:

- Summary of both PRs (Engineer and AI)
- Final evaluation score with visual indicator
- Detailed breakdown of individual metric scores
- Bug information and affected files
- Improvement suggestions for the AI-generated solution

The reports are self-contained HTML files that can be viewed in any modern browser without additional dependencies.

## License

MIT 