# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2026-02-24

### Added

- Show Log Level in Server Log
- Add extension support for pre-release 2.0.2-beta

## [1.0.1] - 2026-02-23

### Added

- Github Actions CI workflow for publishing to PyPI and Github releases

### Fixed

- Fix pyproject.toml

## [1.0.0] - 2026-02-23

### Added

- Initial SageMath-focused LSP server built on `pygls`.
- Plugin-based architecture via `pluggy` entry points.
- Diagnostics using `pycodestyle` and `pyflakes`.
- Formatting support using `autopep8` (document and range).
- Language intelligence via `jedi`: definition, type definition, references, hover, and completion.
- Folding range support.
- Quick-fix code actions for selected diagnostics.
