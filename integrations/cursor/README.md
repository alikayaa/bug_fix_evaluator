# Bug Fix Evaluator - Cursor Extension

A Cursor extension for evaluating and comparing bug fixes implemented by engineers and AI.

## Features

- Evaluate bug fixes by comparing Git commits
- Generate detailed reports with metrics and comparisons
- Visualize strengths and weaknesses of AI-generated fixes
- Compare code changes in a side-by-side view

## Requirements

- Cursor
- Python 3.8 or higher
- Bug Fix Evaluator package installed (`pip install bug-fix-evaluator`)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/alikayaa/bug_fix_evaluator.git
   ```
2. Run `npm install` in the `integrations/cursor` directory
3. Run `npm run package` to build the extension
4. Install the extension in Cursor

## Usage

### Evaluate Bug Fixes from Commits

1. Open a workspace containing a Git repository with both engineer and AI bug fixes
2. Open the Bug Fix Evaluator sidebar
3. Click on the "Evaluate Bug Fix" command
4. Enter the commit SHAs for:
   - The engineer's code before the fix
   - The engineer's code after the fix
   - The AI's code before the fix
   - The AI's code after the fix
5. Wait for the evaluation to complete
6. View the generated report

### View Evaluation Reports

1. Open the Bug Fix Evaluator sidebar
2. Click on any of the listed reports to open them
3. HTML reports will open in a web view, while other formats will open in the editor

## Configuration

You can configure the extension in the Cursor settings:

- `bugFixEvaluator.pythonPath`: Path to the Python executable with bug-fix-evaluator installed
- `bugFixEvaluator.outputDirectory`: Directory for storing evaluation reports
- `bugFixEvaluator.metrics.weights`: Weights for various evaluation metrics

## Development

### Building the Extension

1. Install dependencies: `npm install`
2. Compile the extension: `npm run compile`
3. Package the extension: `npm run package`

### Running Tests

Run the tests with: `npm test`

## Contributing

1. Fork the repository from https://github.com/alikayaa/bug_fix_evaluator
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## Author

Ali Kaya (iletisim@alikaya.net.tr) 