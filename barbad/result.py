from __future__ import annotations

import ast
import sys
import traceback
from typing import Callable, final


@final
class ResultError(BaseException):
    def __init__(self, value: int, msg: str | Exception = "") -> None:
        self.value = value
        self.msg = msg if isinstance(msg, str) else "".join(traceback.format_exception(msg))
        super().__init__()


@final
class Result:
    def __init__(self, node: ast.AST, error: ResultError | None = None) -> None:
        self.node = node
        self.error = error

    def or_exit(self) -> None:
        if self.error is not None:
            if self.error.msg:
                print(self.error.msg, file=sys.stderr)

            sys.exit(self.error.value)

    def attempt(self, func: Callable[[ast.AST], None], error_code: int) -> Result:
        if self.error is not None:
            return self

        try:
            func(self.node)

        except ResultError as r:
            return Result(self.node, r)

        except Exception as e:
            return Result(self.node, ResultError(error_code, e))

        return Result(self.node)
