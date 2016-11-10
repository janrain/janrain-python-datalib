import unittest
from janrain_datalib.utils import to_csv

class TestUtils(unittest.TestCase):

    def test_to_csv_with_no_delimiter(self):
        # setup
        input = ['first', '2nd,with,commas', 'lasty']
        expected = 'first,"2nd,with,commas",lasty\r\n'
        # call
        result = to_csv(input)
        # test
        self.assertEqual(result, expected)

    def test_to_csv_with_None_as_delimiter(self):
        # setup
        input = ['first', '2nd,with,commas', 'lasty']
        expected = 'first,"2nd,with,commas",lasty\r\n'
        delimiter = None
        # call
        result = to_csv(input, delimiter=delimiter)
        # test
        self.assertEqual(result, expected)

    def test_to_csv_with_bar_delimiter(self):
        # setup
        input = ['first', '2nd,with,commas', 'lasty']
        expected = 'first|2nd,with,commas|lasty\r\n'
        delimiter = '|'
        # call
        result = to_csv(input, delimiter=delimiter)
        # test
        self.assertEqual(result, expected)

    def test_to_csv_with_semicolon_delimiter(self):
        # setup
        input = ['first', '2nd,with,commas', 'lasty']
        expected = 'first;2nd,with,commas;lasty\r\n'
        delimiter = ';'
        # call
        result = to_csv(input, delimiter=delimiter)
        # test
        self.assertEqual(result, expected)
