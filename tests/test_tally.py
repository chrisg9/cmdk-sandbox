import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from tally import count, main


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


if __name__ == "__main__":
    unittest.main()
