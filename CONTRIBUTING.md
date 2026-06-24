# Contributing to SportsCast AI

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/Sunnyvk18-py/sportscast-ai
cd sportscast-ai
pip install -e ".[dev,dashboard]"
```

## Running Tests

```bash
pytest tests/ --cov=pipeline
python examples/no_api_key_example.py
```

## Code Style

- Python: `black` and `ruff`
- TypeScript: `tsc --noEmit`

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Ensure CI passes (no API keys required)
4. Submit a pull request with a clear description

## Mock Pipeline First

All tests and CI run without API keys. Use `MockPipeline` and mock detectors for new features before integrating real models.
