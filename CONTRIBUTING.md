# Contributing to sage-lsp

Thank you for your interest in contributing to the SageMath Language Server!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/SeanDictionary/sage-lsp.git
cd sage-lsp
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest tests/ -v
```

## Project Structure

```
sage-lsp/
├── sage_lsp/          # Main package
│   ├── __init__.py    # Package initialization
│   ├── server.py      # LSP server implementation
│   └── sage_features.py  # SageMath-specific features
├── tests/             # Test suite
│   └── test_sage_features.py
├── examples/          # Example files
│   └── example.sage
├── pyproject.toml     # Project configuration
└── README.md          # Documentation
```

## Testing

We use pytest for testing. Before submitting a PR, ensure all tests pass:

```bash
pytest tests/ -v
```

To run tests with coverage:
```bash
pip install pytest-cov
pytest tests/ --cov=sage_lsp --cov-report=html
```

## Adding New Features

When adding new LSP features:

1. **Define the feature handler** in `sage_lsp/server.py`
2. **Implement SageMath-specific logic** in `sage_lsp/sage_features.py`
3. **Add tests** in `tests/test_sage_features.py`
4. **Update documentation** in README.md

### Example: Adding a New Feature

```python
# In server.py
from lsprotocol.types import TEXT_DOCUMENT_REFERENCES

async def find_references(ls, params):
    """Find references to a symbol."""
    # Implementation here
    pass

# In create_server(), register the feature
self.protocol.fm.feature(TEXT_DOCUMENT_REFERENCES)(find_references)
```

## Code Style

- Follow PEP 8 for Python code style
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep functions focused and maintainable

## Submitting Changes

1. Create a new branch for your feature/fix
2. Make your changes
3. Add or update tests as needed
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## Questions?

If you have questions or need help, please open an issue on GitHub.
