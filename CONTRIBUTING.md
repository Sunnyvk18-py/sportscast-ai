# Contributing to SportsCast AI

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/Sunnyvk18-py/sportscast-ai
cd sportscast-ai
pip install -e ".[dev,dashboard,speech]"
```

Set `OPENAI_API_KEY` in `.env` to run the real pipeline locally.

## Running Tests

```bash
pytest tests/ --cov=pipeline
```

Unit tests use synthetic signals and do not call external APIs.

## Code Style

- Python: `black` and `ruff`
- TypeScript: `tsc --noEmit`

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Ensure CI passes
4. Submit a pull request with a clear description
