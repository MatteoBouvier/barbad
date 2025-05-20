import sys
import argparse

from barbad.main import OptimizationFlag, main


def cli() -> None:
    parser = argparse.ArgumentParser("barbad", description="barbad: bytecode optimization for CPython")
    parser.add_argument("file", help="program read from script file")
    parser.add_argument("-r", "--run", action="store_true", help="Run optimized code")
    parser.add_argument(
        "-o", action="extend", choices=["inline"], help="Select optimizations to apply", dest="optimizations", nargs=1
    )

    args = parser.parse_args()

    optimizations = OptimizationFlag(0)
    if args.optimizations is not None:
        for opt in args.optimizations:
            optimizations |= OptimizationFlag[opt]

    sys.exit(main(args.file, optimizations, args.run))
