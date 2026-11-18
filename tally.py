"""Count words, lines and characters in a file."""
import sys


def count(text):
    return {"words": len(text.split()), "lines": text.count("\n"), "chars": len(text)}


def main(argv):
    if len(argv) != 2:
        print("usage: tally.py FILE")
        return 2
    with open(argv[1]) as f:
        c = count(f.read())
    print(f"{c['words']} words, {c['lines']} lines, {c['chars']} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
