import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import Any, Callable, Literal, NoReturn, NotRequired, TypedDict, final, override

from barbad.main import OptimizationFlag, compile_code, show_code


class Argument(TypedDict):
    name_or_flags: list[str]
    action: NotRequired[Literal["store", "store_const", "store_true"]]
    const: NotRequired[Any]
    default: NotRequired[Any]
    choices: NotRequired[Iterable[str] | None]
    help: NotRequired[str | None]


# TODO: benchmark command to compare run times
# TODO: show --diff option to compare optimizations


@final
class CLIParser(argparse.ArgumentParser):
    def __init__(self, prog: str, description: str, sub_command_dest: str | None = None) -> None:
        super().__init__(prog, description=description)

        if sub_command_dest is not None:
            self._sub_commands = self.add_subparsers(title="action", dest="__cmd__")
        else:
            self._sub_commands = None

        self._sub_command_callbacks: dict[str, Callable[[argparse.Namespace], int]] = {}
        self.default_action: str | None = None

    @override
    def error(self, message: str) -> NoReturn:
        self.print_help(sys.stderr)
        self.exit(2, f"\nerror: {message}\n")

    def _set_default_action(self, action: str) -> None:
        if self.default_action is not None:
            raise ValueError("Default action was already set")

        assert self._sub_commands is not None
        self.usage = f"{self.prog} [action] [-h] ..."
        self._action_groups[-1].title = f"action (default: {action})"
        self.default_action = action

    def register_cmd(self, name: str, *arguments: Argument, help: str | None = None, is_default: bool = False):
        assert self._sub_commands is not None, "This parser does not have sub commands"
        sub_command_parser = self._sub_commands.add_parser(name, description=None, help=help)

        for arg in arguments:
            sub_command_parser.add_argument(*arg.pop("name_or_flags"), **arg)

        if is_default:
            self._set_default_action(name)

        def inner(sub_command: Callable[[argparse.Namespace], int]):
            self._sub_command_callbacks[name] = sub_command

            def _():
                raise RuntimeError("Callback should not be called directly")

        return inner

    @override
    def parse_args(
        self, args: Sequence[str] | None = None, namespace: argparse.Namespace | None = None
    ) -> argparse.Namespace:
        if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
            parser.print_help(sys.stdout)
            sys.exit(0)

        elif sys.argv[1] in ("compile", "show"):
            return super().parse_args(sys.argv[1:])

        else:
            return super().parse_args(["compile"] + sys.argv[1:])

    def run_sub_command(self, args: argparse.Namespace) -> NoReturn:
        sys.exit(self._sub_command_callbacks[args.__cmd__](args))


parser = CLIParser("barbad", description="A bytecode optimization tool for CPython", sub_command_dest="__cmd__")


def cli() -> None:
    args = parser.parse_args()
    parser.run_sub_command(args)


@parser.register_cmd(
    "compile",
    Argument(name_or_flags=["file"], help="read python code from file or from stdin if '-'"),
    Argument(name_or_flags=["-r", "--run"], action="store_true", help="run optimized code"),
    Argument(
        name_or_flags=["-oinline"],
        action="store_const",
        const=OptimizationFlag.inline,
        default=OptimizationFlag.none,
        help="inline functions marked with the Inline__ return type",
    ),
    help="Compile python file",
    is_default=True,
)
def compile(args: argparse.Namespace) -> int:
    optimizations = OptimizationFlag(0)
    for opt in ("oinline",):
        optimizations |= getattr(args, opt)

    return compile_code(args.file, optimizations, args.run)


@parser.register_cmd(
    "show",
    Argument(
        name_or_flags=["mode"],
        choices=["raw", "ast", "bytecode"],
        help="show raw python code, parsed AST or bytecodes after optimization",
    ),
    Argument(name_or_flags=["file"], help="read python code from file or from stdin if '-'"),
    Argument(
        name_or_flags=["-oinline"],
        action="store_const",
        const=OptimizationFlag.inline,
        default=OptimizationFlag.none,
        help="inline functions marked with the Inline__ return type",
    ),
    help="Show optimized python code",
)
def show(args: argparse.Namespace) -> int:
    optimizations = OptimizationFlag(0)
    for opt in ("oinline",):
        optimizations |= getattr(args, opt)

    return show_code(args.file, optimizations, args.mode)
