import ast
import dis
import io
from difflib import unified_diff
from itertools import zip_longest
from types import CodeType


def show_code_diff(code: bytes, ref: bytes) -> str:
    code_res = io.StringIO()
    dis.dis(code, file=code_res)
    code_res.seek(0)

    ref_res = io.StringIO()
    dis.dis(ref, file=ref_res)
    ref_res.seek(0)

    return "Codes do not match\n" + "".join(
        unified_diff(code_res.readlines(), ref_res.readlines(), fromfile="parsed", tofile="expected", n=1)
    )


def assert_code_equals(code: CodeType, main: bytes, *others: bytes) -> None:
    assert code.co_code == main, show_code_diff(code.co_code, main)
    for code_, other_ in zip_longest(filter(lambda e: isinstance(e, CodeType), code.co_consts), others, fillvalue=None):
        assert code_ is not None, "Not enough code objects in source"
        assert other_ is not None, "Too many code objects in source"
        assert code_.co_code == other_, show_code_diff(code_.co_code, other_)


def astp(node: ast.AST) -> None:
    print(ast.dump(node, indent=2))
