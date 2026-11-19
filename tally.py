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


def read_error(path, exc):
    """Describe why path could not be read, in one line."""
    name = "<stdin>" if path == "-" else path
    if isinstance(exc, UnicodeDecodeError):
        return f"not valid UTF-8 text: {name}"
    if isinstance(exc, FileNotFoundError):
        return f"no such file: {name}"
    if isinstance(exc, PermissionError):
        return f"permission denied: {name}"
    if isinstance(exc, IsADirectoryError):
        return f"is a directory: {name}"
    return f"cannot read {name}: {exc.strerror or exc}"


def main(argv=None):
    args = parse_args(argv)
    try:
        text = read_text(args.file)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"tally: {read_error(args.file, exc)}", file=sys.stderr)
        return 1
    c = count(text)
    print(f"{c['words']} words, {c['lines']} lines, {c['chars']} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
