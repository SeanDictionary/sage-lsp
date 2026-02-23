# Contributing to sage-lsp

Thanks for your interest in improving `sage-lsp`.

## Development setup

>[!TIP]
>Install in a sage-enabled environment

```bash
git clone https://github.com/SeanDictionary/sage-lsp.git && cd sage-lsp
pip install -e .
```

## Run tests

>[!WARNING]
>All tests will successfully run without any Error. They are only used to simulate a simple LSP client and check the results.

```bash
pytest test/
```

Useful commands: exp.

```bash
pytest tests/test_completion.py
pytest tests/test_hover.py -k basic
pytest -s -v --tb=short
```

For more LSP test details, see [tests/README.md](./tests/README.md).

## Project structure

```
.
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── pyproject.toml
├── src
│   └── sagelsp
│       ├── config                  style/config helpers
│       ├── plugins                 plugin implementations (lint, format, hover, completion, etc.)
│       ├── __init__.py
│       ├── __main__.py
│       ├── _version.py
│       ├── server.py               LSP feature registration and request handlers
│       └── symbols_cache.py        local cache for Sage symbols and import paths
└── tests                           end-to-end style LSP tests and utilities
```

## Pull request guidelines

Please keep PRs focused and small when possible.

Before opening a PR:

1. Ensure tests pass locally.
2. Update docs if behavior changed (`README.md`, this file, or test docs).
3. Add an entry under `Unreleased` in `CHANGELOG.md`.
4. Include a short summary of what changed and why.

## Coding notes

- Keep plugin behavior resilient: failed plugin hooks should not crash the whole server.
- Prefer minimal, targeted changes over broad refactors.
- When changing LSP behavior, add or update tests in `tests/`.

## Reporting issues

When filing an issue, include:

- SageMath version (`sagelsp --sage` output if possible)
- Python version
- Editor and LSP client configuration
- Minimal reproducible code sample

