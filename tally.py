"""Count words, lines and characters in a file."""
import argparse
import sys
from collections import Counter


def count(text):
    lines = text.count("\n")
    if text and not text.endswith("\n"):
        lines += 1
    return {"words": len(text.split()), "lines": lines, "chars": len(text)}


def words(text):
    """Split text the same way count() does, lowercased for matching.

    Punctuation is kept, so "end." and "end" are different words.
    """
    return [w.lower() for w in text.split()]


def unique_words(text):
    return len(set(words(text)))


def top_words(text, n):
    """Return the n most frequent (word, count) pairs, ties broken alphabetically."""
    counts = Counter(words(text))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]


def positive_int(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a whole number: {value!r}")
    if n < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {n}")
    return n


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
    parser.add_argument(
        "--unique",
        action="store_true",
        help="also print the number of distinct words (case-insensitive)",
    )
    parser.add_argument(
        "--top",
        type=positive_int,
        metavar="N",
        help="also print the N most frequent words with their counts",
    )
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
    if args.unique:
        print(f"{unique_words(text)} unique words")
    if args.top is not None:
        for word, n in top_words(text, args.top):
            print(f"{n} {word}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
