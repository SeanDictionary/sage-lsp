# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-27

### Fixed

- Fix using `import_statements` in `symbols_cache` when Sage is not available, which caused errors when trying to get symbol information.
- Fix sage available check error

### Added

- Add `language_id` check to `pyflakes_lint` plugin to avoid errors when trying to lint non-Sage files without Sage available.
- Add lint for codes in notebook cells
- Add notebook check

### Changed

- Split `sagelsp_lint` into `sagelsp_semantic_lint` and `sagelsp_style_lint` to separate diagnostics that are safe on virtual notebook documents and those that should run on original document or cell text.
- Change config load

## [1.0.3] - 2026-03-12

### Fixed

- Fix formatting for code like `a ^^= 1`

### Changed

- Changed `pyproject.toml`

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
