from math import e
from lsprotocol import types
from typing import List, Tuple
from functools import lru_cache

from pygls.uris import from_fs_path
import inspect
import json
import logging

log = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    # Only include whitelisted attributes to avoid excessive data
    WHITELIST = {
        # name/identifier
        'name', 'class_name', 'module_name', 'full_module_name',

        # structure
        'body', 'stats', 'args', 'bases', 'base',

        # type
        'base_type', 'type', 'declarator', 'declarators',

        # attribute
        'attribute', 'obj',

        # expressions
        'lhs', 'rhs', 'operand1', 'operand2', 'operator', 'value', 'function',

        # documentation
        'doc',

        # position
        'pos',
    }

    def default(self, obj):
        if hasattr(obj, '__dict__'):
            filtered = {k: v[-2:] if k == 'pos' else v for k, v in obj.__dict__.items()
                        if k in self.WHITELIST}
            return {'_type': obj.__class__.__name__, **filtered}
        if isinstance(obj, (list, tuple)):
            return list(obj)
        return str(obj)


@lru_cache()
def cython_prase(file_path: str) -> dict:
    """Parse a Cython file into a JSON-like dict structure"""
    from types import SimpleNamespace
    from Cython.Compiler import Parsing
    from Cython.Compiler.Scanning import PyrexScanner, FileSourceDescriptor
    from Cython.Compiler.Main import Context, CompilationOptions

    try:
        file = open(file_path, 'r', encoding='utf-8')
    except Exception as e:
        log.error(f"Failed to open Cython file {file_path}: {e}")
        return {}
    filename = FileSourceDescriptor(file_path)

    scope = SimpleNamespace(included_files=[])
    ctx = Context.from_options(CompilationOptions(language_level=3))

    scanner = PyrexScanner(file, filename, scope=scope, context=ctx, source_encoding='utf-8')

    tree = Parsing.p_module(scanner, pxd=False, full_module_name=file_path)

    json_str = json.dumps(tree, cls=JSONEncoder, indent=2)
    return json.loads(json_str)


@lru_cache()
def locate_symbol(tree: dict, node: dict, symbol_name: str, file_path: str) -> Tuple[types.Location, dict]:
    """Recursively locate the symbol in the AST node. Return its location and the node."""

    # ! import modules are not handled yet

    if not node:
        return None, None

    _type = node.get('_type')

    if _type == "ModuleNode":
        bode_node = node.get('body')
        return locate_symbol(tree, bode_node, symbol_name, file_path)

    elif _type == "StatListNode":
        stats = node.get('stats', [])
        for stat in stats:
            location, found_node = locate_symbol(tree, stat, symbol_name, file_path)
            if location and found_node:
                return location, found_node

    elif _type == "CClassDefNode":
        class_name = node.get('class_name')
        if class_name == symbol_name:
            pos = node.get('pos')
            location = types.Location(
                uri=from_fs_path(file_path),
                range=types.Range(
                    start=types.Position(line=pos[0] - 1, character=pos[1] + 6),
                    end=types.Position(line=pos[0] - 1, character=pos[1] + 6 + len(symbol_name)),
                )
            )
            return location, node

    elif _type == "PyClassDefNode":
        class_name = node.get('name')
        if class_name == symbol_name:
            pos = node.get('pos')
            location = types.Location(
                uri=from_fs_path(file_path),
                range=types.Range(
                    start=types.Position(line=pos[0] - 1, character=pos[1] + 6),
                    end=types.Position(line=pos[0] - 1, character=pos[1] + 6 + len(symbol_name)),
                )
            )
            return location, node

    elif _type == "CFuncDefNode":
        declarator = node.get('declarator', {})
        base = declarator.get('base', {})
        func_name = base.get('name')
        if func_name == symbol_name:
            pos = base.get('pos')
            location = types.Location(
                uri=from_fs_path(file_path),
                range=types.Range(
                    start=types.Position(line=pos[0] - 1, character=pos[1]),
                    end=types.Position(line=pos[0] - 1, character=pos[1] + len(symbol_name)),
                )
            )
            return location, node

    elif _type == "DefNode":
        func_name = node.get('name')
        if func_name == symbol_name:
            pos = node.get('pos')
            location = types.Location(
                uri=from_fs_path(file_path),
                range=types.Range(
                    start=types.Position(line=pos[0] - 1, character=pos[1] + 4),
                    end=types.Position(line=pos[0] - 1, character=pos[1] + 4 + len(symbol_name)),
                )
            )
            return location, node

    elif _type == "SingleAssignmentNode":
        lhs = node.get('lhs', {})
        rhs = node.get('rhs', {})
        lhs_type = lhs.get('_type')
        rhs_type = rhs.get('_type')
        if lhs_type == "NameNode":
            lhs_name = lhs.get('name')
            if lhs_name == symbol_name:
                # In theory, `x=y;y=x` will caused infinite loop, but in projects it won't
                # Besides, as exported symbols are always defined in global scope
                # ? if it's necessary to add a finding alias definition, anyway I add it
                if rhs_type == "NameNode":
                    rhs_name = rhs.get('name')
                    return locate_symbol(tree, tree, rhs_name, file_path)

                elif rhs_type == "SimpleCallNode":
                    args = rhs.get('args', [])
                    # I think only no-arg function calls can be assignment sources
                    if not args:
                        function = rhs.get('function', {})
                        func_name = function.get('name')
                        return locate_symbol(tree, tree, func_name, file_path)

    return None, None


@lru_cache()
def definition(file_path: str, symbol_name: str) -> List[types.Location]:
    """Find the definition location of a symbol from .pyx file"""
    tree = cython_prase(file_path)
    if not tree:
        return []

    locations = []
    # Traverse the tree to find the symbol definition

    location, _ = locate_symbol(tree, tree, symbol_name, file_path)
    if location:
        locations.append(location)
    return locations


def signature(file_path: str, symbol_name: str) -> str:
    """Find the signature of a symbol from .pyx file"""
    tree = cython_prase(file_path)
    if not tree:
        return ""

    _, node = locate_symbol(tree, tree, symbol_name, file_path)
    _type = node['_type']

    if _type in ["PyClassDefNode", "CClassDefNode"]:
        node_name = node.get('name') or node.get('class_name')
        stats = node['body']['stats']
        for stat in stats:
            if stat['name'] == '__init__':
                init_node = stat
                break
        else:
            # If no __init__ method, use base class as signature
            # ? seems not very accurate, but it's better than nothing
            base = node.get('bases', {})
            base_args = base.get('args', [])
            args = []
            for arg in base_args:
                arg_name = arg.get('name')
                if arg_name:
                    args.append(arg_name)
            
            return f"{'cdef ' if _type == 'CClassDefNode' else ''}class {node_name}({', '.join(args)})"

        
        init_args = init_node['args']
        args = []
        for arg in init_args:
            base_type = arg.get('base_type', {}).get('name')
            arg_name = arg.get('declarator', {}).get('name')
            if base_type:
                args.append(f"{arg_name}: {base_type}")
            else:
                args.append(arg_name)
        
        return f"{'cdef ' if _type == 'CClassDefNode' else ''}class {node_name}({', '.join(args)})"
    
    elif _type == "DefNode":
        func_args = node['args']
        args = []
        for func_arg in func_args:
            base_type = func_arg.get('base_type').get('name')
            arg_name = func_arg.get('declarator').get('name')
            if base_type:
                args.append(f"{arg_name}: {base_type}")
            else:
                args.append(arg_name)
        
        return f"def {symbol_name}({', '.join(args)})"

    elif _type == "CFuncDefNode":
        func_base_type = node.get('base_type').get('name')
        func_args = node['declarator']['args']
        args = []
        for func_arg in func_args:
            base_type = func_arg.get('base_type', {}).get('name')
            arg_name = func_arg.get('declarator', {}).get('name')
            if arg_name:
                args.append(f"{arg_name}: {base_type}")
            else:
                args.append(base_type)
        
        return f"cdef {func_base_type} {symbol_name}({', '.join(args)})"

def docstring(file_path: str, symbol_name: str) -> str:
    """Find the docstring of a symbol from .pyx file"""
    tree = cython_prase(file_path)
    if not tree:
        return ""

    _, node = locate_symbol(tree, tree, symbol_name, file_path)
    if node:
        doc = node.get('doc', '')
        return inspect.cleandoc(doc)

    return ""


def pyx_path(import_path: str) -> str:
    """Get the .pyx file path from import path"""
    from sage.env import SAGE_LIB

    return SAGE_LIB + "/" + import_path.replace(".", "/") + ".pyx"

if __name__ == "__main__":
    path = "/home/sean/miniforge3/envs/sage/lib/python3.11/site-packages/sage/rings/integer_ring.pyx"
    symbol_name = "ZZ"
    pos = definition(path, symbol_name)
    doc = docstring(path, symbol_name)
    sig = signature(path, symbol_name)
    print(sig)
