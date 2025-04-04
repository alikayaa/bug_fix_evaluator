#!/usr/bin/env python3
from setuptools import setup, find_packages

# Read the content of requirements.txt
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bug-fix-evaluator",
    version="0.2.0",
    author="Bug Fix Evaluator Team",
    author_email="example@example.com",
    description="A tool for evaluating bug fixes by comparing engineer and AI solutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bug-fix-evaluator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "bug-fix-evaluator=bug_fix_evaluator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bug_fix_evaluator": [
            "templates/*.html",
            "templates/*.txt",
            "templates/*.md",
            "templates/assets/*",
        ],
    },
) 