from barbad import Inline__


def add(a: int, b: int) -> Inline__[int]:
    return a + b


def main() -> None:
    x = 3
    y = 4
    c = add(x, y)
    print(c)


main()
