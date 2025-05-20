import ast
from pathlib import Path
from enum import IntFlag, auto

from barbad.inline import inline


class OptimizationFlag(IntFlag):
    inline = auto()


def main(source: str | Path, optimizations: OptimizationFlag, run: bool = False) -> int:
    source = Path(source)
    with open(source) as f:
        tree = ast.parse(f.read(), source.name, "exec")

    if optimizations & OptimizationFlag.inline:
        inline(tree).or_exit()

    if run:
        print(ast.dump(tree, indent=2))
        exec(compile(tree, source.name, "exec"), globals())

    return 0
