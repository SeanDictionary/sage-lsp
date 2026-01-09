import re
import autopep8
import pycodestyle
from pycodestyle import *

ARITHMETIC_OP = frozenset(['**', '*', '/', '//', '+', '-', '@', '^'])
WS_OPTIONAL_OPERATORS = ARITHMETIC_OP.union(['^^', '&', '|', '<<', '>>', '%'])

OPERATOR_REGEX = re.compile(r'(?=(?:[^,\s])(\s*)(?:[-+*/|!<=>%&^]+|:=)(\s*))')


def _retokenize(tokens):
    """Retokenize to handle operator like '^^'.

    Merges consecutive ^ tokens into a single ^^ token.
    """
    tokens_list = list(tokens)
    i = 0

    while i < len(tokens_list):
        token_type, text, start, end, line = tokens_list[i]

        # Check if this is a ^ followed immediately by another ^
        if (text == '^' and
            i + 1 < len(tokens_list) and
            tokens_list[i + 1][1] == '^' and
                tokens_list[i + 1][2] == end):  # Next ^ starts where this one ends

            # Merge into ^^
            next_token = tokens_list[i + 1]
            merged_token = (
                tokenize.OP,           # token_type
                '^^',                   # text
                start,                  # start position (from first ^)
                next_token[3],          # end position (from second ^)
                line                    # line text
            )
            yield merged_token
            i += 2  # Skip both ^ tokens
        else:
            # Keep original token
            yield tokens_list[i]
            i += 1


def extraneous_whitespace(logical_line):
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


def whitespace_around_operator(logical_line):
    """
    Patch for `pycodestyle.whitespace_around_operator` to support Sage syntax sugar.
    """
    # R.<x> = PolynomialRing(ZZ)
    # Fix: E221, E222, E223, E224
    for match in OPERATOR_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E223 tab before operator"
        elif len(before) > 1:
            yield match.start(1), "E221 multiple spaces before operator"

        if '\t' in after:
            yield match.start(2), "E224 tab after operator"
        elif len(after) > 1:
            yield match.start(2), "E222 multiple spaces after operator"


def missing_whitespace(logical_line, tokens):
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

    # Original logic handle missing whitespace with patch
    need_space = False
    prev_type = tokenize.OP
    prev_text = prev_end = None
    operator_types = (tokenize.OP, tokenize.NAME)
    brace_stack = []
    for token_type, text, start, end, line in _retokenize(tokens):
        if token_type == tokenize.OP and text in {'[', '(', '{'}:
            brace_stack.append(text)
        elif token_type == FSTRING_START:  # pragma: >=3.12 cover
            brace_stack.append('f')
        elif token_type == TSTRING_START:  # pragma: >=3.14 cover
            brace_stack.append('t')
        elif token_type == tokenize.NAME and text == 'lambda':
            brace_stack.append('l')
        elif brace_stack:
            if token_type == tokenize.OP and text in {']', ')', '}'}:
                brace_stack.pop()
            elif token_type == FSTRING_END:  # pragma: >=3.12 cover
                brace_stack.pop()
            elif token_type == TSTRING_END:  # pragma: >=3.14 cover
                brace_stack.pop()
            elif (
                    brace_stack[-1] == 'l' and
                    token_type == tokenize.OP and
                    text == ':'
            ):
                brace_stack.pop()

        if token_type in SKIP_COMMENTS:
            continue

        if token_type == tokenize.OP and text in {',', ';', ':'}:
            next_char = line[end[1]:end[1] + 1]
            if next_char not in WHITESPACE and next_char not in '\r\n':
                # slice
                if text == ':' and brace_stack[-1:] == ['[']:
                    pass
                # 3.12+ fstring format specifier
                elif text == ':' and brace_stack[-2:] == ['f', '{']:  # pragma: >=3.12 cover  # noqa: E501
                    pass
                # 3.14+ tstring format specifier
                elif text == ':' and brace_stack[-2:] == ['t', '{']:  # pragma: >=3.14 cover  # noqa: E501
                    pass
                # tuple (and list for some reason?)
                elif text == ',' and next_char in ')]':
                    pass
                else:
                    yield start, f'E231 missing whitespace after {text!r}'

        if need_space:
            if start != prev_end:
                # Found a (probably) needed space
                if need_space is not True and not need_space[1]:
                    yield (need_space[0],
                           "E225 missing whitespace around operator")
                need_space = False
            elif (
                    # def f(a, /, b):
                    #           ^
                    # def f(a, b, /):
                    #              ^
                    # f = lambda a, /:
                    #                ^
                    prev_text == '/' and text in {',', ')', ':'} or
                    # def f(a, b, /):
                    #               ^
                    prev_text == ')' and text == ':'
            ):
                # Tolerate the "/" operator in function definition
                # For more info see PEP570
                pass
            else:
                if need_space is True or need_space[1]:
                    # A needed trailing space was not found
                    yield prev_end, "E225 missing whitespace around operator"
                elif prev_text not in ('**', '^'):
                    code, optype = 'E226', 'arithmetic'
                    if prev_text == '%':
                        code, optype = 'E228', 'modulo'
                    elif prev_text not in ARITHMETIC_OP:
                        code, optype = 'E227', 'bitwise or shift'
                    yield (need_space[0], "%s missing whitespace "
                           "around %s operator" % (code, optype))
                need_space = False
        elif token_type in operator_types and prev_end is not None:
            if (
                    text == '=' and (
                        # allow lambda default args: lambda x=None: None
                        brace_stack[-1:] == ['l'] or
                        # allow keyword args or defaults: foo(bar=None).
                        brace_stack[-1:] == ['('] or
                        # allow python 3.8 fstring repr specifier
                        brace_stack[-2:] == ['f', '{'] or
                        # allow python 3.8 fstring repr specifier
                        brace_stack[-2:] == ['t', '{']
                    )
            ):
                pass
            elif text in WS_NEEDED_OPERATORS:
                need_space = True
            elif text in UNARY_OPERATORS:
                # Check if the operator is used as a binary operator
                # Allow unary operators: -123, -x, +1.
                # Allow argument unpacking: foo(*args, **kwargs).
                if prev_type == tokenize.OP and prev_text in '}])' or (
                    prev_type != tokenize.OP and
                    prev_text not in KEYWORDS and
                    not keyword.issoftkeyword(prev_text)
                ):
                    need_space = None
            elif text in WS_OPTIONAL_OPERATORS:
                need_space = None

            if need_space is None:
                # Surrounding space is optional, but ensure that
                # trailing space matches opening space
                need_space = (prev_end, start != prev_end)
            elif need_space and start == prev_end:
                # A needed opening space was not found
                yield prev_end, "E225 missing whitespace around operator"
                need_space = False
        prev_type = token_type
        prev_text = text
        prev_end = end


FUNCS = [
    (
        pycodestyle.extraneous_whitespace,
        extraneous_whitespace,
    ),
    (
        pycodestyle.missing_whitespace,
        missing_whitespace,
    ),
    (
        pycodestyle.whitespace_around_operator,
        whitespace_around_operator,
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
R.<x> =    PolynomialRing(ZZ)
"""
    lines = source.splitlines(keepends=True)

    # test codestyle checker
    checker = pycodestyle.Checker(lines=lines)
    print(checker.check_all())

    # test code formatter
    fixed = autopep8.fix_code(source)
    print(fixed)
