# SageMath LSP Integration Examples

This directory contains examples demonstrating how to integrate sage-lsp with different editors and test the language server.

## Example SageMath Code

The `example.sage` file demonstrates various SageMath features that the language server should support:
- Variable declarations
- Symbolic computation
- Calculus operations
- Matrix operations
- Number theory functions
- Graphics

## Testing the Language Server

### Manual Testing with TCP

You can test the language server manually using TCP mode:

```bash
# Start the server
sage-lsp --tcp --port 2087 -v

# In another terminal, you can connect with telnet or netcat
# and send LSP requests
```

### Testing with an LSP Client

For real-world testing, configure your editor's LSP client to use `sage-lsp`:

**VS Code** (using generic LSP extension):
1. Install a generic LSP extension
2. Configure it to run `sage-lsp` for `.sage` files

**Neovim** (using nvim-lspconfig):
```lua
-- Add to your config
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

if not configs.sage_lsp then
  configs.sage_lsp = {
    default_config = {
      cmd = {'sage-lsp'},
      filetypes = {'sage', 'python'},
      root_dir = lspconfig.util.root_pattern('.git'),
    },
  }
end

lspconfig.sage_lsp.setup{}
```

## Features Demonstrated

- **Completion**: Type partially and see suggestions
- **Hover**: Hover over SageMath functions to see documentation
- **Syntax Support**: Proper handling of `.sage` files
