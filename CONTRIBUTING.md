# Contributing to HOLY REMIX

Thank you for your interest in contributing! Please follow these guidelines to help us review your changes quickly and smoothly.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .[dev]
   ```
3. Copy `.env.example` to `.env` and fill in your credentials.

## Code Style
- Use [Black](https://black.readthedocs.io/) for formatting.
- Use [Ruff](https://docs.astral.sh/ruff/) for linting.
- Use [mypy](http://mypy-lang.org/) for type checking.
- Run `pre-commit install` to enable pre-commit hooks.

## Making Changes
- Create a new branch for each feature or bugfix.
- Write clear, concise commit messages.
- Add or update tests as needed.

## Running Tests
```bash
pytest
```

## Pull Requests
- Ensure your branch is up to date with `main`.
- All checks (lint, type, tests) must pass before review.
- Describe your changes clearly in the PR description.

Thank you for helping make HOLY REMIX better! 