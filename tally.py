"""Count words, lines and characters in a file."""
import argparse
import sys


def count(text):
    lines = text.count("\n")
    if text and not text.endswith("\n"):
        lines += 1
    return {"words": len(text.split()), "lines": lines, "chars": len(text)}


def read_text(path):
    """Return the contents of path, or of standard input if path is "-", as UTF-8."""
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="tally",
        description="Count words, lines and characters in a file.",
    )
    parser.add_argument("file", help='file to read, or "-" for standard input')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    c = count(read_text(args.file))
    print(f"{c['words']} words, {c['lines']} lines, {c['chars']} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
