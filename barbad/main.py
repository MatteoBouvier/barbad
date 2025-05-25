import ast
import dis
import sys
from contextlib import closing
from enum import IntFlag, auto
from pathlib import Path
from typing import Literal

from barbad.inline import inline


class OptimizationFlag(IntFlag):
    none = 0
    inline = auto()


def optimize(source: str | Path, optimizations: OptimizationFlag) -> tuple[str, ast.Module]:
    input_code = sys.stdin if source == "-" else open(source)
    input_name = "<string>" if source == "-" else Path(source).name

    with closing(input_code):
        tree = ast.parse(input_code.read(), input_name, "exec")

    if optimizations & OptimizationFlag.inline:
        inline(tree).or_exit()

    return input_name, tree


def compile_code(source: str | Path, optimizations: OptimizationFlag, run: bool = False) -> int:
    input_name, tree = optimize(source, optimizations)

    if run:
        exec(compile(tree, input_name, "exec"), globals())

    return 0


def show_code(source: str | Path, optimizations: OptimizationFlag, mode: Literal["raw", "ast", "bytecode"]) -> int:
    input_name, tree = optimize(source, optimizations)

    if mode == "raw":
        print(ast.unparse(tree))

    elif mode == "ast":
        print(ast.dump(tree, indent=2))

    elif mode == "bytecode":
        dis.dis(compile(tree, input_name, "exec"))

    return 0
