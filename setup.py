"""Setup script for the Bug Fix Cursor Evaluator package."""

import os
from setuptools import setup, find_packages

# Read version from package
with open(os.path.join("src", "bug_fix_cursor_evaluator", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bug-fix-cursor-evaluator",
    version=version,
    description="A tool for evaluating bug fixes using Cursor agent mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ali Kaya",
    author_email="",
    url="https://github.com/alikayaa/bug_fix_evaluator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "bug_fix_cursor_evaluator": ["templates/*.html", "templates/*.md", "templates/*.txt"],
    },
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bug-fix-evaluator=bug_fix_cursor_evaluator.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="bug, fix, evaluation, cursor, github, pull request",
) 