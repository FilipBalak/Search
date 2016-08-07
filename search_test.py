"""Unit test for search.py"""

import sys
from StringIO import StringIO
import unittest
import search


class SearchBadArguments(unittest.TestCase):

    def test_too_few_arguments(self):
        """search should fail with bad amount of arguments"""
        self.assertRaises(
            SystemExit,
            search.get_arguments,
            ['-u', '-m', '-c'])

    def test_unrecognized_arguments(self):
        """search should fail with unrecognized arguments"""
        self.assertRaises(
            SystemExit,
            search.get_arguments,
            ['-k', '-m', '-c', 'a', '-'])


class SearchBadValues(unittest.TestCase):

    def test_get_color(self):
        """search should fail with incorectly added colors to input"""

        pattern = 'a'
        string = 'a'
        self.search = search.Search('-', pattern, False, False, False)
        self.search.get_match_indexes(string)
        self.assertEqual(
            '\033[1;33m'+pattern+'\033[0m',
            self.search.add_color(string))

    def test_get_underscore(self):
        """search should fail with improperly created underscore line"""

        pattern = 'a'
        string = '   a '
        self.search = search.Search('-', pattern, False, False, False)
        self.search.get_match_indexes(string)
        self.assertEqual('   ^', self.search.get_underscore_line(string))

    def test_get_match_indexes(self):
        """Method get_match_indexes should configure list of tuples with right
        values as class attribute."""

        pattern = 'a'
        string = 'a     a  a '
        self.search = search.Search('-', pattern, False, False, False)
        self.search.get_match_indexes(string)
        self.assertEqual([(0, 1), (6, 7), (9, 10)], self.search.indexes)

    def test_print_results_basic(self):
        """Method print_results should print result in right format
        on standard output."""

        pattern = 'a'
        string = 'a a'
        self.search = search.Search('-', pattern, False, False, False)
        self.search.get_match_indexes(string)

        out = StringIO()
        sys.stdout = out
        self.search.print_result('-', 1, string)
        output = out.getvalue().strip()
        self.assertEqual('- 1 ' + string, output)

    def test_print_results_with_underscore_and_color(self):
        """Method print_results should print result in right format on
        standard output. If provided arguments for printing underscore
        and color highlighting it should be added to output too."""

        pattern = 'a'
        string = 'a a'
        self.search = search.Search('-', pattern, True, True, False)
        self.search.get_match_indexes(string)

        out = StringIO()
        sys.stdout = out
        self.search.print_result('-', 1, string)
        output = out.getvalue().strip()
        self.assertEqual(
            '- 1 \x1b[1;33ma\x1b[0m \x1b[1;33ma\x1b[0m\n    ^ ^',
            output)

    def test_print_results_with_machine_format(self):
        """Method print_results should print result in right format on
        standard output. If provided arguments for printing underscore
        and color highlighting it should be added to output too."""

        pattern = 'a'
        string = 'a a'
        self.search = search.Search('-', pattern, False, False, True)
        self.search.get_match_indexes(string)

        out = StringIO()
        sys.stdout = out
        self.search.print_result('-', 1, string)
        output = out.getvalue().strip()
        self.assertEqual('-:1:0:' + string, output)

if __name__ == "__main__":
    unittest.main()
