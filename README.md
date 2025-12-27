# sage-lsp

SageMath Language Server Protocol - A Python-based language server for SageMath

## Overview

`sage-lsp` is a Language Server Protocol (LSP) implementation for SageMath, written in Python. Similar to `python-lsp-server`, it provides IDE features for SageMath code including:

- **Autocompletion**: Intelligent code completion for SageMath functions and symbols
- **Hover Information**: Display documentation and type information on hover
- **Document Synchronization**: Real-time document updates
- **Extensible Architecture**: Built on `pygls` for easy extension

## Features

- 🚀 Built with `pygls` (Python Generic Language Server)
- 🔍 SageMath-specific completions and documentation
- 📝 Falls back to Python support when SageMath is not available
- 🔌 Works with any LSP-compatible editor (VS Code, Neovim, Emacs, etc.)
- ⚡ Fast and responsive

## Installation

### From Source

```bash
git clone https://github.com/SeanDictionary/sage-lsp.git
cd sage-lsp
pip install -e .
```

### Requirements

- Python >= 3.8
- SageMath (optional, for full functionality)

The language server will work without SageMath installed, providing basic Python support. For full SageMath features, ensure SageMath is installed and available in your Python environment.

## Usage

### Command Line

Start the language server using stdio (for editor integration):

```bash
sage-lsp
```

Start the language server using TCP:

```bash
sage-lsp --tcp --host 127.0.0.1 --port 2087
```

### Command Line Options

- `--tcp`: Use TCP server instead of stdio
- `--host HOST`: Host for TCP server (default: 127.0.0.1)
- `--port PORT`: Port for TCP server (default: 2087)
- `--log-file PATH`: Path to log file
- `-v, --verbose`: Enable verbose logging

### Editor Integration

#### VS Code

1. Install a generic LSP client extension or create a custom extension
2. Configure it to use `sage-lsp` as the language server for `.sage` files

Example configuration:

```json
{
  "sage-lsp.serverPath": "sage-lsp",
  "sage-lsp.enabled": true
}
```

#### Neovim

Using `nvim-lspconfig`:

```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

-- Configure sage-lsp
if not configs.sage_lsp then
  configs.sage_lsp = {
    default_config = {
      cmd = {'sage-lsp'},
      filetypes = {'sage', 'python'},
      root_dir = lspconfig.util.root_pattern('.git', 'setup.py', 'pyproject.toml'),
      settings = {},
    },
  }
end

lspconfig.sage_lsp.setup{}
```

#### Emacs

Using `lsp-mode`:

```elisp
(require 'lsp-mode)

(add-to-list 'lsp-language-id-configuration '(sage-mode . "sage"))

(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection "sage-lsp")
                  :major-modes '(sage-mode python-mode)
                  :server-id 'sage-lsp))
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/SeanDictionary/sage-lsp.git
cd sage-lsp

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Architecture

The language server is structured as follows:

- `sage_lsp/server.py`: Main LSP server implementation using pygls
- `sage_lsp/sage_features.py`: SageMath-specific features (completion, hover, etc.)
- `sage_lsp/__init__.py`: Package initialization

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pygls](https://github.com/openlawlibrary/pygls) - Python Generic Language Server
- Inspired by [python-lsp-server](https://github.com/python-lsp/python-lsp-server)
- Powered by [SageMath](https://www.sagemath.org/)

## Roadmap

Future features planned:

- [ ] Go to definition support
- [ ] Find references
- [ ] Signature help
- [ ] Code formatting
- [ ] Linting and diagnostics
- [ ] Symbol search
- [ ] Workspace symbols
- [ ] Enhanced SageMath integration
