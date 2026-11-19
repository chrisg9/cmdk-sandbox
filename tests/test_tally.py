import unittest

from tally import count


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


if __name__ == "__main__":
    unittest.main()
