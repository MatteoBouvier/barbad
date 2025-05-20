import ast
from typing import Annotated, override

from barbad.result import Result

type Inline__[T] = Annotated[T, "__barbad_inline__"]


class FindInlined(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()

        self.inline_functions: dict[str, ast.AST] = {}

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        match node:
            case ast.FunctionDef(name, _, _, _, ast.Subscript(ast.Name("Inline__", _), _, _), _):
                self.inline_functions[name] = node

            case _:
                return


class RewriteInline(ast.NodeTransformer):
    def __init__(self, inline_functions: dict[str, ast.AST]) -> None:
        self.inline_functions: dict[str, ast.AST] = inline_functions

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None | ast.ImportFrom:
        match node:
            case ast.ImportFrom("barbad", _, 0):
                return None

            case _:
                return node

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None | ast.FunctionDef:
        if node.name in self.inline_functions:
            return None

        return self.generic_visit(node)

    @override
    def visit_Call(self, node: ast.Call):
        match node:
            case ast.Call(ast.Name(name, _), _, _) if name in self.inline_functions:
                if_node = self.inline_functions[name]

                args_translation = {k.arg: v.id for k, v in zip(if_node.args.args, node.args)}

                return_node = if_node.body[0].value
                return type(return_node)(
                    *(
                        ast.Name(
                            args_translation[field.id], field.ctx, lineno=field.lineno, col_offset=field.col_offset
                        )
                        if isinstance(field, ast.Name)
                        else field
                        for field in map(lambda f: getattr(return_node, f), return_node._fields)
                    ),
                    lineno=return_node.lineno,
                    col_offset=return_node.col_offset,
                )

            case _:
                return node


def inline(tree: ast.AST) -> Result:
    """Modify an AST tree to inline functions marked with the barbad._inline_ return type."""
    finder = FindInlined()
    try:
        finder.visit(tree)
    except Exception as e:
        return Result(10, str(e))

    try:
        RewriteInline(finder.inline_functions).visit(tree)
    except Exception as e:
        return Result(11, str(e))

    return Result(0)
