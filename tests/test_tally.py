import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from tally import count, main, top_words, unique_words


class CountTest(unittest.TestCase):
    def test_counts_a_simple_line(self):
        self.assertEqual(count("one two three\n"), {"words": 3, "lines": 1, "chars": 14})

    def test_empty(self):
        self.assertEqual(count(""), {"words": 0, "lines": 0, "chars": 0})

    def test_last_line_without_newline_counts(self):
        self.assertEqual(count("a\nb")["lines"], 2)

    def test_trailing_newline_does_not_add_a_line(self):
        self.assertEqual(count("a\n")["lines"], 1)
        self.assertEqual(count("a\nb\n")["lines"], 2)

    def test_single_line_without_newline(self):
        self.assertEqual(count("a")["lines"], 1)

    def test_blank_lines_count(self):
        self.assertEqual(count("\n")["lines"], 1)
        self.assertEqual(count("a\n\nb")["lines"], 3)


def run(argv, stdin=b""):
    """Run main(argv) with stdin bytes; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    fake_stdin = io.TextIOWrapper(io.BytesIO(stdin), encoding="utf-8")
    with mock.patch("sys.stdin", fake_stdin), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = self._tmp.name

    def write(self, name, data):
        path = os.path.join(self.tmp, name)
        mode = "wb" if isinstance(data, bytes) else "w"
        kwargs = {} if isinstance(data, bytes) else {"encoding": "utf-8", "newline": ""}
        with open(path, mode, **kwargs) as f:
            f.write(data)
        return path


class MainTest(MainTestCase):
    def test_counts_a_file(self):
        path = self.write("a.txt", "one two three\nfour\n")
        self.assertEqual(run([path]), (0, "4 words, 2 lines, 19 characters\n", ""))

    def test_reads_utf8_file(self):
        path = self.write("u.txt", "café naïve\n")
        self.assertEqual(run([path]), (0, "2 words, 1 lines, 11 characters\n", ""))

    def test_dash_reads_stdin(self):
        code, out, err = run(["-"], stdin="héllo world\nbye".encode("utf-8"))
        self.assertEqual((code, out, err), (0, "3 words, 2 lines, 15 characters\n", ""))

    def test_empty_stdin(self):
        self.assertEqual(run(["-"]), (0, "0 words, 0 lines, 0 characters\n", ""))

    def test_no_arguments_is_a_usage_error(self):
        code, out, err = run([])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("usage: tally", err)

    def test_too_many_arguments_is_a_usage_error(self):
        code, out, err = run(["a", "b"])
        self.assertEqual(code, 2)
        self.assertIn("usage: tally", err)

    def test_help_exits_zero(self):
        code, out, _ = run(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage: tally", out)


class UniqueTest(MainTestCase):
    def test_unique_words_ignores_case(self):
        self.assertEqual(unique_words("The cat the CAT dog"), 3)

    def test_unique_words_keeps_punctuation(self):
        self.assertEqual(unique_words("end end. end,"), 3)

    def test_unique_words_empty(self):
        self.assertEqual(unique_words(""), 0)

    def test_unique_flag_prints_after_default_line(self):
        path = self.write("a.txt", "a b A\nb c\n")
        self.assertEqual(
            run(["--unique", path]),
            (0, "5 words, 2 lines, 10 characters\n3 unique words\n", ""),
        )

    def test_unique_flag_with_stdin(self):
        code, out, _ = run(["-", "--unique"], stdin=b"x X y")
        self.assertEqual((code, out), (0, "3 words, 1 lines, 5 characters\n2 unique words\n"))

    def test_default_output_has_no_unique_line(self):
        _, out, _ = run(["-"], stdin=b"x X y")
        self.assertNotIn("unique", out)


class TopTest(MainTestCase):
    def test_most_frequent_first(self):
        self.assertEqual(top_words("b a b c b a", 3), [("b", 3), ("a", 2), ("c", 1)])

    def test_ties_broken_alphabetically(self):
        self.assertEqual(top_words("pear apple fig pear fig apple", 3),
                         [("apple", 2), ("fig", 2), ("pear", 2)])

    def test_limits_to_n(self):
        self.assertEqual(top_words("c b a", 2), [("a", 1), ("b", 1)])

    def test_n_larger_than_distinct_words(self):
        self.assertEqual(top_words("a A b", 10), [("a", 2), ("b", 1)])

    def test_keeps_punctuation(self):
        self.assertEqual(top_words("end end.", 5), [("end", 1), ("end.", 1)])

    def test_empty_text(self):
        self.assertEqual(top_words("", 3), [])

    def test_top_flag_prints_one_per_line(self):
        code, out, err = run(["-", "--top", "2"], stdin=b"the cat The dog the cat\n")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, "6 words, 1 lines, 24 characters\n3 the\n2 cat\n")

    def test_unique_and_top_order(self):
        _, out, _ = run(["--top", "1", "--unique", "-"], stdin=b"b a b")
        self.assertEqual(out, "3 words, 1 lines, 5 characters\n2 unique words\n2 b\n")

    def test_top_on_empty_input_prints_only_default_line(self):
        self.assertEqual(run(["-", "--top", "3"]), (0, "0 words, 0 lines, 0 characters\n", ""))

    def test_rejects_zero(self):
        code, out, err = run(["-", "--top", "0"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("must be at least 1", err)

    def test_rejects_negative(self):
        code, _, err = run(["-", "--top=-3"])
        self.assertEqual(code, 2)
        self.assertIn("must be at least 1", err)

    def test_rejects_non_integer(self):
        code, _, err = run(["-", "--top", "two"])
        self.assertEqual(code, 2)
        self.assertIn("not a whole number", err)

    def test_requires_a_value(self):
        code, _, err = run(["-", "--top"])
        self.assertEqual(code, 2)
        self.assertIn("expected one argument", err)


class ErrorTest(MainTestCase):
    def assertFails(self, argv, message, stdin=b""):
        self.assertEqual(run(argv, stdin), (1, "", f"tally: {message}\n"))

    def test_missing_file(self):
        path = os.path.join(self.tmp, "nope.txt")
        self.assertFails([path], f"no such file: {path}")

    def test_directory(self):
        self.assertFails([self.tmp], f"is a directory: {self.tmp}")

    @unittest.skipIf(not hasattr(os, "geteuid") or os.geteuid() == 0,
                     "root can read files without permission")
    def test_unreadable_file(self):
        path = self.write("secret.txt", "hidden\n")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o600)
        self.assertFails([path], f"permission denied: {path}")

    def test_invalid_utf8_file(self):
        path = self.write("bad.txt", b"ok \xff\xfe\n")
        self.assertFails([path], f"not valid UTF-8 text: {path}")

    def test_invalid_utf8_stdin(self):
        self.assertFails(["-"], "not valid UTF-8 text: <stdin>", stdin=b"\xff")

    def test_other_os_error(self):
        err = OSError(5, "Input/output error")
        with mock.patch("tally.read_text", side_effect=err):
            self.assertFails(["x"], "cannot read x: Input/output error")


if __name__ == "__main__":
    unittest.main()
