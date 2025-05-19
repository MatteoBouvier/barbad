import sys
from typing import final


@final
class Result:
    def __init__(self, value: int, message: str = "") -> None:
        self.value = value
        self.message = message

    def or_exit(self) -> None:
        if self.value:
            if self.message:
                print(self.message, file=sys.stderr)

            sys.exit(self.value)
