import re
import autopep8
import pycodestyle


def extraneous_whitespace(logical_line=None):
    """
    Patch for `pycodestyle.extraneous_whitespace` to support Sage syntax sugar.
    """
    # R.<x>, A.<x, y>, L.<t1, t2, t3>
    # Fix: E201, E202
    sage_pattern = re.compile(r'\w+\.<\s*\w+\s*(,\s*\w+\s*)*\s*>')
    match = sage_pattern.search(logical_line)
    if match:
        inner = re.search(r'<\s*\w+\s*(,\s*\w+\s*)*\s*>', logical_line)
        if logical_line[inner.start() + 1] == ' ':
            pos = inner.start() + 1
            yield pos, "E201 whitespace after '<'"
        if logical_line[inner.end() - 2] == ' ':
            pos = inner.end() - 2
            yield pos, "E202 whitespace before '>'"

    yield from pycodestyle.extraneous_whitespace(logical_line)


def missing_whitespace(logical_line=None, tokens=None):
    """
    Patch for `pycodestyle.missing_whitespace` to support Sage syntax sugar.
    """
    # R.<x>, A.<x, y>, L.<t1, t2, t3>
    # Fix: E225, E231
    sage_pattern = re.compile(r'\w+\.<\s*\w+\s*(,\s*\w+\s*)*\s*>')
    match = sage_pattern.search(logical_line)
    if match:
        if "=" in logical_line:
            inner = re.search(r'.=.', logical_line)
            if inner:
                if inner and logical_line[inner.start()] != ' ':
                    yield inner.start() + 1, "E225 missing whitespace around operator"
                elif inner and logical_line[inner.start()] == ' ' and logical_line[inner.end() - 1] != ' ':
                    yield inner.end() - 1, "E225 missing whitespace around operator"
        if "," in logical_line:
            for inner in re.finditer(r'\w,.', logical_line):
                if logical_line[inner.end() - 1] != ' ':
                    yield inner.start() + 1, "E231 missing whitespace after ','"
        return

    # 1 ^^ 2
    # Fix: E225, E227
    if "^^" in logical_line:
        inner = re.search(r'.\^\^.', logical_line)
        if inner:
            if logical_line[inner.start()] != ' ':
                yield inner.start() + 1, "E227 missing whitespace around bitwise or shift operator"
            if logical_line[inner.end() - 1] != ' ':
                yield inner.end() - 1, "E227 missing whitespace around bitwise or shift operator"
        return

    # Otherwise, call the original function
    yield from pycodestyle.missing_whitespace(logical_line, tokens)


FUNCS = [
    (
        pycodestyle.extraneous_whitespace,
        extraneous_whitespace,
    ),
    (
        pycodestyle.missing_whitespace,
        missing_whitespace,
    ),
]


def pycodestyle_patch(funcs=FUNCS):
    """
    Patch pycodestyle functions with new implementations.
    """
    for orig_func, new_func in funcs:
        err_codes, args = pycodestyle._checks['logical_line'][orig_func]
        pycodestyle._checks['logical_line'][new_func] = (err_codes, args)
        del pycodestyle._checks['logical_line'][orig_func]


if __name__ == "__main__":
    pycodestyle_patch()
    # test code
    source = """\
a = 1+1
"""
    lines = source.splitlines(keepends=True)

    # test codestyle checker
    checker = pycodestyle.Checker(lines=lines)
    print(checker.check_all())

    options = {

    }

    # test code formatter
    fixed = autopep8.fix_code(source, options=options)
    print(fixed)
