# sage-lsp

## Description

![Release](https://img.shields.io/github/v/release/SeanDictionary/sage-lsp) ![Platform](https://img.shields.io/badge/platform-Linux-green) ![License](https://img.shields.io/github/license/SeanDictionary/sage-lsp) ![GitHub repo size](https://img.shields.io/github/repo-size/SeanDictionary/sage-lsp) ![GitHub last commit](https://img.shields.io/github/last-commit/SeanDictionary/sage-lsp) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![SageMath](https://img.shields.io/badge/SageMath-Suggested%2010.8%2B-yellow)

SageMath Language Server Protocol

> [!TIP]
> This project may work well with SageMath 10.8+. Other versions lack stubs for Cython files, so they may have limited functionality.
>
> However, until now (2026-2-13), SageMath 10.8 is not accessible from conda-forge (but it released on github).
>Meanwhile, maintainer doesn't include `.pyi` files in the build system, so you can't simply install it from pip either.
>
>You may need to [install it from source code](https://doc.sagemath.org/html/en/installation/source.html). And edit some code.
>```bash
>git clone --branch 10.8 --single-branch https://github.com/sagemath/sage.git
>cd sage
>mamba env create --file environment-3.12-linux.yml --name sage10.8
>mamba activate sage10.8
>```
>Edit `./tools/update-meson.py` like this
>```diff
>@@ -93,3 +93,3 @@
>        python_files = sorted(
>-            list(folder.glob("*.py")) + list(folder.glob('*.pxd')) + list(folder.glob('*.pyx'))
>+            list(folder.glob("*.py")) + list(folder.glob('*.pxd')) + list(folder.glob('*.pyx')) + list(folder.glob('*.pyi'))
>        )  # + list(folder.glob('*.pxd')) + list(folder.glob('*.h')))
>```
>Run `./tools/update-meson.py` to regenerate `meson.build` files. Then you can install it.
>```bash
>python ./tools/update-meson.py
>pip install .
>```
>Using `sage --version` to check if successfully installed.

>[!WARNING]
>If raising error about `ImportError: cysignals.signals does not export expected C function _do_raise_exception`, using following command to fix it.
>```bash
>pip uninstall cysignals
>conda install cysignals
>```

## Features

Supported from plugins(very thanks to those projects, they finished a lot of work):

- [pygls](https://github.com/openlawlibrary/pygls) basic LSP server framework
- [pycodestyle](https://github.com/PyCQA/pycodestyle) linter for style checking
- [autopep8](https://github.com/hhatto/autopep8) formatter for code formatting
- [pyflakes](https://github.com/PyCQA/pyflakes) linter for error checking
- [jedi](https://github.com/davidhalter/jedi) definition, type definiton, hover, references provider
- [parso](https://github.com/davidhalter/parso)(dependency of jedi) for folding
- [docstring-to-markdown](https://github.com/python-lsp/docstring-to-markdown) praser for converting docstrings to markdown for hover information


Supported from native code:

- Only support using `from sage.xxx import xxx` or `import sage.xxx` (no alias)
- Local symbols cache for Sage
- Custom formatting rules for Sage
- Custom error checking for Sage
- Custom definition for Sage symbols
- Custom hover information for Sage symbols
- Check references for Sage (only in current file)
- Jump to definiton in Cython files (`.pyx`) from Stubs (`.pyi`) in Sage 10.8+
- Support type inference for Sage (depend on `.pyi` in Sage 10.8+)
- Support type hints hover info for unfollowed variables
- Quick fix for undefined name in Sage

## Change Logs

See [CHANGELOG.md](./CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](./LICENSE) file for details.

## TODO

- [ ] Add type definition support
- [x] Add definition location ~~for symbols_cache~~ from global info
- [x] Add definition for .pyx
- [x] Add hover for .pyx
- [x] Add folding support
- [x] Add reference support
- [x] Add type inference support (only for .py/.pyi files)
- [ ] Add code completion support (only for .py/.pyi files)
- [x] Add type hints support (only for hover info, no type definition)
- [x] Add runtime sage env info

