# sage-lsp

## Description

SageMath Language Server Protocol

## Features

Supported from plugins(very thanks to those projects, they finished a lot of work):

- [pycodestyle](https://github.com/PyCQA/pycodestyle) linter for style checking
- [autopep8](https://github.com/hhatto/autopep8) formatter for code formatting
- [pyflakes](https://github.com/PyCQA/pyflakes) linter for error checking
- [jedi](https://github.com/davidhalter/jedi) definition and hover
- [docstring-to-markdown](https://github.com/python-lsp/docstring-to-markdown) praser for converting docstrings to markdown for hover information


Supported from native code:

- Local symbols cache for Sage
- Custom formatting rules for Sage
- Custom error checking for Sage
- Custom definition for Sage symbols
- Custom hover information for Sage symbols

## Change Logs

See [CHANGELOG.md](./CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](./LICENSE) file for details.

## TODO

- [ ] Add type definition support
- [ ] Add definition location for symbols_cache
- [x] Add definition for .pyx
- [x] Add hover for .pyx

