# cmdk-sandbox

A throwaway repository for trying cmd+k end to end. Nothing here matters.

`tally` is a tiny command-line word counter: one file, `tally.py`, using only
the Python standard library.

## Usage

```sh
python3 tally.py [--unique] [--top N] FILE
```

`FILE` is a path, or `-` to read standard input. Input is read as UTF-8.

```sh
$ python3 tally.py notes.txt
42 words, 7 lines, 251 characters

$ printf 'the cat The dog the cat\n' | python3 tally.py - --unique --top 2
6 words, 1 lines, 24 characters
3 unique words
3 the
2 cat
```

The first line is always `N words, N lines, N characters`.

- **Words** are runs of non-whitespace, the same as Python's `str.split()`.
- **Lines** count newline-terminated lines. A last line without a trailing
  newline also counts, so `a\nb` is 2 lines, `a\n` is 1 and an empty file is 0.
- **Characters** are Unicode characters, not bytes.

## Options

| Option | Effect |
|---|---|
| `--unique` | Also print `N unique words`, the number of distinct words. |
| `--top N` | Also print the `N` most frequent words, one per line as `<count> <word>`. The most frequent come first, and ties are broken alphabetically. If there are fewer than `N` distinct words, all of them are printed. `N` must be a whole number of at least 1. |
| `-h`, `--help` | Show help and exit. |

When both options are given, output is the default line, then the unique count,
then the top list.

### How words are matched

`--unique` and `--top` split words exactly as the word count does, then
**lowercase** them. Matching is therefore case-insensitive: `The` and `the` are
the same word. Punctuation is **not** stripped, so `end`, `end.` and `end,` are
three different words. This keeps the numbers consistent with the word count.

## Exit status and errors

| Status | Meaning |
|---|---|
| 0 | Success. |
| 1 | The input could not be read. One line goes to stderr, for example `tally: no such file: foo.txt`, `tally: permission denied: foo.txt`, `tally: is a directory: foo`, `tally: not valid UTF-8 text: foo.txt`. |
| 2 | Bad usage: a missing or extra argument, or a bad value for `--top`. |

## Tests

```sh
python3 -m unittest
```
