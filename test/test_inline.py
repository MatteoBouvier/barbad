import ast
from types import CodeType

from barbad.inline import inline


def test_inline():
    stmts = """
from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(x, y)
    print(c)
"""

    tree = ast.parse(stmts, "<string>", "exec")
    res = inline(tree)
    assert res.value == 0, res.message

    # TODO: optim! unnecessary STORE_FAST
    comp: CodeType = compile(tree, "<string>", "exec")
    assert comp.co_code == b'\x95\x00S\x03S\x02\x1a\x00j\x04r\x00g\x01'
    assert comp.co_consts[2].co_code == b'\x95\x00S\x01n\x00S\x02n\x01X\x01-\x00\x00\x00n\x02[\x01\x00\x00\x00\x00\x00\x00\x00\x00U\x025\x01\x00\x00\x00\x00\x00\x00 \x00g\x00'
