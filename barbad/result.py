import sys
import traceback
from typing import final


@final
class Result(BaseException):
    def __init__(self, value: int, error: str | Exception = "") -> None:
        self.value = value
        self.message = error if isinstance(error, str) else "".join(traceback.format_exception(error))
        super().__init__()

    def __bool__(self) -> bool:
        return bool(self.value)

    def or_exit(self) -> None:
        if self.value:
            if self.message:
                print(self.message, file=sys.stderr)

            sys.exit(self.value)
