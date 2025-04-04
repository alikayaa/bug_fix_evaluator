#!/bin/bash
# Build script for the Bug Fix Evaluator Cursor extension

# Make the script exit on any error
set -e

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed. Please install Node.js and try again."
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "npm is required but not installed. Please install npm and try again."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the extension
echo "Building the extension..."
npm run package

# Create extension directory if it doesn't exist
mkdir -p ../../dist/cursor

# Copy built files to dist directory
echo "Copying files to dist directory..."
cp -r dist package.json README.md resources ../../dist/cursor/

echo "Build complete!"
echo "The extension is available in ../../dist/cursor/" 