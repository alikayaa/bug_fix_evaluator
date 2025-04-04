#!/usr/bin/env python3
from setuptools import setup, find_packages

# Read the content of requirements.txt
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Read the content of README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bug-fix-evaluator",
    version="0.1.0",
    description="A system for evaluating AI-generated bug-fix PRs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ali Kaya",
    author_email="iletisim@alikaya.net.tr",
    url="https://github.com/alikayaa/bug-fix-evaluator",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "bug-fix-eval=src.evaluator:main",
        ],
    },
) 