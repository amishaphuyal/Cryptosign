import os
import tempfile
import unittest
from unittest.mock import patch

from core.hash_engine import generate_hash


class TestHashEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "sample.txt")

        with open(self.test_file, "wb") as f:
            f.write(b"hello world")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_hash_success(self):
        result = generate_hash(self.test_file)

        expected ="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        self.assertEqual(result, expected)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            generate_hash("missing_file.txt")

    @patch("core.revocation.is_revoked", return_value=False)
    def test_generate_hash_with_non_revoked_user(self, mock_revoked):
        result = generate_hash(self.test_file, username="amisha")

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)

    @patch("core.revocation.is_revoked", return_value=True)
    def test_revoked_user_blocked(self, mock_revoked):
        with self.assertRaises(PermissionError):
            generate_hash(self.test_file, username="amisha")


if __name__ == "__main__":
    unittest.main()