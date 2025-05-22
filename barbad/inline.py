import abc
import ast
from typing import Annotated, override

from barbad.result import Result

type Inline__[T] = Annotated[T, "__barbad_inline__"]


class AttemptMixin(abc.ABC):
    @abc.abstractmethod
    def visit(self, node: ast.AST) -> None:
        pass

    def attempt_visit(self, node: ast.AST, error: Result | int) -> Result:
        if isinstance(error, Result):
            return error

        try:
            self.visit(node)

        except Result as r:
            return r

        except Exception as e:
            return Result(error, e)

        return Result(0)


class FindInlined(ast.NodeVisitor, AttemptMixin):
    def __init__(self) -> None:
        super().__init__()

        self.inline_functions: dict[str, ast.FunctionDef] = {}

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        match node:
            case ast.FunctionDef(name, _, _, _, ast.Subscript(ast.Name("Inline__", _), _, _), _):
                self.inline_functions[name] = node

            case _:
                return


class RewriteInline(ast.NodeTransformer, AttemptMixin):
    def __init__(self, inline_functions: dict[str, ast.FunctionDef]) -> None:
        self.inline_functions: dict[str, ast.FunctionDef] = inline_functions

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None | ast.ImportFrom:
        match node:
            case ast.ImportFrom("barbad", _, 0):
                return None

            case _:
                return node

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None | ast.AST:
        if node.name in self.inline_functions:
            return None

        return self.generic_visit(node)

    @staticmethod
    def _get_args(if_node: ast.FunctionDef, node: ast.Call) -> dict[str, str]:
        pos_args = {k.arg: v.id for k, v in zip(if_node.args.args, node.args)}
        kwd_args = {keyword.arg: keyword.value.id for keyword in node.keywords}

        if dbl_args := set(pos_args).intersection(kwd_args):
            raise Result(12, f"{if_node.name}() got multiple values for argument(s) {', '.join(map(repr, dbl_args))}")

        if mis_args := (len(if_node.args.args) - len(pos_args) - len(kwd_args)):
            raise Result(
                13,
                f"{if_node.name}() missing {mis_args} required positional argument(s) {', '.join(map(lambda a: a.arg, if_node.args.args[:-mis_args]))}",
            )

        return pos_args | kwd_args

    @override
    def visit_Call(self, node: ast.Call):
        match node:
            case ast.Call(ast.Name(name, _), _, _) if name in self.inline_functions:
                if_node = self.inline_functions[name]

                args_translation = self._get_args(if_node, node)
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
    """Modify an AST tree to inline functions marked with the barbad.Inline__ return type."""
    finder = FindInlined()

    res = finder.attempt_visit(tree, 10)
    return RewriteInline(finder.inline_functions).attempt_visit(tree, res or 11)
