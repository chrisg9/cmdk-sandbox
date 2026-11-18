import unittest

from tally import count


class CountTest(unittest.TestCase):
    def test_counts_a_simple_line(self):
        self.assertEqual(count("one two three\n"), {"words": 3, "lines": 1, "chars": 14})

    def test_empty(self):
        self.assertEqual(count(""), {"words": 0, "lines": 0, "chars": 0})


if __name__ == "__main__":
    unittest.main()
