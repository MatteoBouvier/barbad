import sys
import argparse
from typing import NoReturn, override

from barbad.main import OptimizationFlag, main


class CLIParser(argparse.ArgumentParser):
    @override
    def error(self, message: str) -> NoReturn:
        self.print_help(sys.stderr)
        self.exit(2, f"\nerror: {message}\n")


def cli() -> None:
    parser = CLIParser("barbad", description="barbad: bytecode optimization for CPython")

    parser.add_argument("file", help="read python code from file or from stdin if '-'")
    parser.add_argument("-r", "--run", action="store_true", help="run optimized code")
    parser.add_argument(
        "-s",
        "--show",
        choices=["raw", "ast", "bytecode"],
        help="show raw python code, parsed AST or bytecodes after optimization",
    )
    parser.add_argument(
        "-oinline",
        action="store_const",
        const=OptimizationFlag.inline,
        default=OptimizationFlag.none,
        help="inline functions marked with the Inline__ return type",
    )

    args = parser.parse_args()

    optimizations = OptimizationFlag(0)
    for opt in ("oinline",):
        optimizations |= getattr(args, opt)

    sys.exit(main(args.file, optimizations, args.show, args.run))
