# sage-lsp

## Description

SageMath Language Server Protocol

## Features

Supported from plugins(very thanks to those projects, they finished a lot of work):

- [pycodestyle](https://github.com/PyCQA/pycodestyle) linter for style checking
- [autopep8](https://github.com/hhatto/autopep8) formatter for code formatting
- [pyflakes](https://github.com/PyCQA/pyflakes) linter for error checking
- [jedi](https://github.com/davidhalter/jedi) definition

Supported from native code:

- Local symbols cache for Sage
- Custom formatting rules for Sage
- Custom error checking for Sage

## Change Logs

See [CHANGELOG.md](./CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](./LICENSE) file for details.

## TODO

- [ ] Add type definition support
- [ ] Add definition location for symbols_cache
- [ ] Add definition for .pyx
- [ ] It seems that Sage adds .pyi for Cython from 10.8, it'll be easier for definition of pyx

