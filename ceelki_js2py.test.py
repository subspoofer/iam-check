import unittest
from ceelki_js2py import read_lines, split_blocks, sort_blocks, extract_accounts, remove_duplicates

class TestCeelkiJS2Py(unittest.TestCase):

    def test_read_lines(self):
        # Test reading a file with one line
        self.assertEqual(read_lines("test_files/one_line.txt"), ["This is a test file with one line."])
        
        # Test reading a file with multiple lines
        self.assertEqual(read_lines("test_files/multiple_lines.txt"), ["This is the first line.", "This is the second line.", "This is the third line."])

    def test_split_blocks(self):
        # Test splitting a file with one block
        content = read_lines("test_files/one_block.txt")
        expected_blocks = [["exemption: {", "  account: 1234567890", "}"]]
        self.assertEqual(split_blocks(content), expected_blocks)

        # Test splitting a file with multiple blocks
        content = read_lines("test_files/multiple_blocks.txt")
        expected_blocks = [["exemption: {", "  account: 1234567890", "}", "exemption: {", "  account: 0987654321", "}"]]
        self.assertEqual(split_blocks(content), expected_blocks)

    def test_sort_blocks(self):
        # Test sorting blocks in alphabetical order
        blocks = [["exemption: {", "  account: 1234567890", "}"], ["exemption: {", "  account: 0987654321", "}"]]
        expected_blocks = [["exemption: {", "  account: 0987654321", "}"], ["exemption: {", "  account: 1234567890", "}"]]
        self.assertEqual(sort_blocks(blocks), expected_blocks)

        # Test sorting blocks in reverse alphabetical order
        blocks = [["exemption: {", "  account: 0987654321", "}"], ["exemption: {", "  account: 1234567890", "}"]]
        expected_blocks = [["exemption: {", "  account: 1234567890", "}"], ["exemption: {", "  account: 0987654321", "}"]]
        self.assertEqual(sort_blocks(blocks), expected_blocks)

    def test_extract_accounts(self):
        # Test extracting accounts from one block
        blocks = [["exemption: {", "  account: 1234567890", "}"]]
        expected_accounts = ["1234567890"]
        self.assertEqual(extract_accounts(blocks), expected_accounts)

        # Test extracting accounts from multiple blocks
        blocks = [["exemption: {", "  account: 1234567890", "}", "exemption: {", "  account: 0987654321", "}"]]
        expected_accounts = ["1234567890", "0987654321"]
        self.assertEqual(extract_accounts(blocks), expected_accounts)

    def test_remove_duplicates(self):
        # Test removing duplicate blocks
        blocks = [["exemption: {", "  account: 1234567890", "}"], ["exemption: {", "  account: 1234567890", "}"]]
        expected_blocks = [["exemption: {", "  account: 1234567890", "}"]]
        self.assertEqual(remove_duplicates(blocks), expected_blocks)

        # Test not removing unique blocks
        blocks = [["exemption: {", "  account: 1234567890", "}"], ["exemption: {", "  account: 0987654321", "}"]]
        expected_blocks = [["exemption: {", "  account: 1234567890", "}"], ["exemption: {", "  account: 0987654321", "}"]]
        self.assertEqual(remove_duplicates(blocks), expected_blocks)

if __name__ == '__main__':
    unittest.main()