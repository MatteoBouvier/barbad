import ast
import dis
import sys
from contextlib import closing
from enum import IntFlag, auto
from pathlib import Path
from types import CodeType
from typing import Literal

from barbad.inline import inline


class OptimizationFlag(IntFlag):
    none = 0
    inline = auto()


def show_code(mode: Literal["raw", "ast", "bytecode"], tree: ast.AST, compiled: CodeType | None):
    if mode == "raw":
        print(ast.unparse(tree))

    elif mode == "ast":
        print(ast.dump(tree, indent=2))

    elif mode == "bytecode":
        assert compiled is not None
        dis.dis(compiled)


def main(
    source: str | Path,
    optimizations: OptimizationFlag,
    show: Literal["raw", "ast", "bytecode"] | None,
    run: bool = False,
) -> int:
    input_code = sys.stdin if source == "-" else open(source)
    input_name = "<string>" if source == "-" else Path(source).name

    with closing(input_code):
        tree = ast.parse(input_code.read(), input_name, "exec")

    if optimizations & OptimizationFlag.inline:
        inline(tree).or_exit()

    if run or show == "bytecode":
        comp = compile(tree, input_name, "exec")

    else:
        comp = None

    if show is not None:
        show_code(show, tree, comp)

    if run:
        assert comp is not None
        exec(comp, globals())

    return 0
