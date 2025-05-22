import ast
from types import CodeType

import pytest

from barbad.inline import inline
from test.testutils import assert_code_equals


@pytest.mark.parametrize(
    "stmts",
    [
        """from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(x, y)
    print(c)
""",
        """from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(b=y, a=x)
    print(c)
""",
        """from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(x, b=y)
    print(c)
""",
    ],
)
def test_inline(stmts: str):
    tree = ast.parse(stmts, "<string>", "exec")
    res = inline(tree)
    assert res.value == 0, res.message

    # TODO: optim! unnecessary STORE_FAST
    comp: CodeType = compile(tree, "<string>", "exec")
    assert_code_equals(
        comp,
        b"\x95\x00S\x03S\x02\x1a\x00j\x04r\x00g\x01",
        b"\x95\x00S\x01n\x00S\x02n\x01X\x01-\x00\x00\x00n\x02[\x01\x00\x00\x00\x00\x00\x00\x00\x00U\x025\x01\x00\x00\x00\x00\x00\x00 \x00g\x00",
    )


@pytest.mark.parametrize(
    "stmts, err_code",
    [
        (
            """from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(x, a=x, b=y)
    print(c)
""",
            12,
        ),
        (
            """from barbad import Inline__

def add(a: int, b: int) -> Inline__[int]:
    return a + b

def main() -> None:
    x = 3
    y = 4
    c = add(x, c=x, d=y)
    print(c)
""",
            13,
        ),
    ],
)
def test_inline_should_fail(stmts: str, err_code: int):
    tree = ast.parse(stmts, "<string>", "exec")
    res = inline(tree)

    assert res.value == err_code
