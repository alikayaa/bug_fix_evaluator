#!/bin/bash
# Install script for Bug Fix Evaluator

# Function to show usage
show_usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  --help              Show this help message"
  echo "  --no-python         Skip Python package installation"
  echo "  --no-extension      Skip VS Code extension installation"
  echo "  --pip-args ARGS     Additional arguments to pass to pip"
  echo "  --python-path PATH  Path to Python executable (default: python)"
  echo "  --open-cursor       Open the extension in Cursor after installation"
}

# Default values
INSTALL_PYTHON=true
INSTALL_EXTENSION=true
PIP_ARGS=""
PYTHON_PATH="python"
OPEN_CURSOR=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help)
      show_usage
      exit 0
      ;;
    --no-python)
      INSTALL_PYTHON=false
      shift
      ;;
    --no-extension)
      INSTALL_EXTENSION=false
      shift
      ;;
    --pip-args)
      PIP_ARGS="$2"
      shift 2
      ;;
    --python-path)
      PYTHON_PATH="$2"
      shift 2
      ;;
    --open-cursor)
      OPEN_CURSOR=true
      shift
      ;;
    *)
      echo "Error: Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Print header
echo "====================================="
echo "Bug Fix Evaluator Installation Script"
echo "====================================="
echo

# Check if Python is available
if ! command -v "$PYTHON_PATH" &> /dev/null; then
  echo "Error: Python not found at $PYTHON_PATH"
  echo "Please install Python or specify the path with --python-path"
  exit 1
fi

# Check Python version
PYTHON_VERSION=$("$PYTHON_PATH" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
  echo "Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
  exit 1
fi

# Install Python package
if $INSTALL_PYTHON; then
  echo "Installing Bug Fix Evaluator Python package..."
  $PYTHON_PATH -m pip install $PIP_ARGS -e .
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python package"
    exit 1
  fi
  echo "Python package installed successfully!"
  echo
fi

# Install VS Code extension
if $INSTALL_EXTENSION; then
  echo "Checking for VS Code extension..."
  
  # Check if the VSIX file exists
  VSIX_PATH="dist/bug-fix-evaluator-0.1.0.vsix"
  if [ ! -f "$VSIX_PATH" ]; then
    echo "Error: VS Code extension not found at $VSIX_PATH"
    echo "Please run 'cd vscode-extension && npm run package' first"
    exit 1
  fi
  
  echo "VS Code extension found at $VSIX_PATH"
  
  # Check if Cursor is installed
  CURSOR_PATH="/Applications/Cursor.app"
  if [ ! -d "$CURSOR_PATH" ]; then
    echo "Warning: Cursor IDE not found at $CURSOR_PATH"
    echo "You'll need to manually install the extension in Cursor"
    echo "See docs/extension_installation.md for instructions"
  else
    echo "Cursor IDE found at $CURSOR_PATH"
    
    if $OPEN_CURSOR; then
      echo "Opening Cursor with the extension..."
      open -a Cursor "$VSIX_PATH"
      echo "Please use the 'Extensions: Install from VSIX' command in Cursor to install the extension"
    else
      echo "To install the extension in Cursor:"
      echo "1. Open Cursor"
      echo "2. Press Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux)"
      echo "3. Type 'Extensions: Install from VSIX' and select that option"
      echo "4. Browse to $PWD/$VSIX_PATH and select it"
    fi
  fi
  
  echo
  echo "For detailed installation instructions, see docs/extension_installation.md"
fi

echo
echo "Installation completed!"
echo "For usage instructions, see README.md" 