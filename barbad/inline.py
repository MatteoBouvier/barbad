import ast
from typing import Annotated, override

from barbad.result import Result, ResultError

type Inline__[T] = Annotated[T, "__barbad_inline__"]


class FindInlined(ast.NodeVisitor):
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


def _get_expr_value(expr: ast.expr) -> ast.Constant | str:
    match expr:
        case ast.Constant():
            return expr

        case ast.Name(id, _):
            return id

        case _:
            raise NotImplementedError


def _get_stmt_value(stmt: ast.stmt) -> ast.expr:
    match stmt:
        case ast.Return(value):
            assert value is not None
            return value

        case _:
            raise NotImplementedError


def _get_function_args(if_node: ast.FunctionDef, node: ast.Call) -> dict[str, ast.Constant | str]:
    pos_args = {k.arg: _get_expr_value(v) for k, v in zip(if_node.args.args, node.args)}
    defaults_args = {
        k.arg: _get_expr_value(v)
        for k, v in zip(if_node.args.args[len(if_node.args.args) - len(if_node.args.defaults) :], if_node.args.defaults)
    }
    kwd_args: dict[str, ast.Constant | str] = defaults_args | {
        keyword.arg: _get_expr_value(keyword.value) for keyword in node.keywords
    }  # pyright: ignore[reportAssignmentType]

    if dbl_args := set(pos_args).intersection(kwd_args):
        raise ResultError(12, f"{if_node.name}() got multiple values for argument(s) {', '.join(map(repr, dbl_args))}")

    if mis_args := (len(if_node.args.args) - len(pos_args) - len(kwd_args)):
        raise ResultError(
            13,
            f"{if_node.name}() missing {mis_args} required positional argument(s) {', '.join(map(lambda a: a.arg, if_node.args.args[:-mis_args]))}",
        )

    return pos_args | kwd_args


def _replace_names_and_constants(node: ast.AST, args_translation: dict[str, ast.Constant | str]) -> ast.AST:
    kwargs = {"lineno": node.lineno, "col_offset": node.col_offset} if isinstance(node, ast.expr) else {}
    return type(node)(
        *(_translate(field, args_translation) for field in map(lambda field_: getattr(node, field_), node._fields)),
        **kwargs,
    )


def _translate(field: ast.expr, args_translation: dict[str, ast.Constant | str]):
    if isinstance(field, ast.Name):
        translation = args_translation[field.id]
        if isinstance(translation, ast.Constant):
            return translation

        assert isinstance(translation, str), type(translation)
        return ast.Name(translation, field.ctx, lineno=field.lineno, col_offset=field.col_offset)

    return _replace_names_and_constants(field, args_translation)


class RewriteInline(ast.NodeTransformer):
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

    @override
    def visit_Call(self, node: ast.Call):
        match node:
            case ast.Call(ast.Name(name, _), _, _) if name in self.inline_functions:
                if_node = self.inline_functions[name]

                args_translation = _get_function_args(if_node, node)
                return_node = _get_stmt_value(if_node.body[0])
                return _replace_names_and_constants(return_node, args_translation)

            case _:
                return node


def inline(tree: ast.AST) -> Result:
    """Modify an AST tree to inline functions marked with the barbad.Inline__ return type."""
    finder = FindInlined()

    return Result(tree).attempt(finder.visit, 10).attempt(RewriteInline(finder.inline_functions).visit, 11)
