import os
import tempfile
import unittest
from unittest.mock import patch

from core.key_manager import generate_key_pair, load_private_key, is_key_encrypted


class TestKeyManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def test_generate_key_pair_creates_private_and_public_key(self):
        private_key, public_key = generate_key_pair("amisha")

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertTrue(os.path.exists("storage/keystores/amisha_private.pem"))
        self.assertTrue(os.path.exists("storage/keystores/amisha_public.pem"))

    def test_load_private_key_success(self):
        generate_key_pair("amisha")

        key = load_private_key("amisha")

        self.assertIsNotNone(key)

    def test_generate_encrypted_private_key(self):
        generate_key_pair("amisha", password="secret123")

        self.assertTrue(is_key_encrypted("amisha"))

    def test_load_encrypted_private_key_with_correct_password(self):
        generate_key_pair("amisha", password="secret123")

        key = load_private_key("amisha", password="secret123")

        self.assertIsNotNone(key)

    def test_load_encrypted_private_key_without_password_fails(self):
        generate_key_pair("amisha", password="secret123")

        with self.assertRaises(ValueError):
            load_private_key("amisha")

    def test_load_missing_private_key_fails(self):
        with self.assertRaises(FileNotFoundError):
            load_private_key("unknown")

    def test_is_key_encrypted_false_for_missing_user(self):
        self.assertFalse(is_key_encrypted("unknown"))


if __name__ == "__main__":
    unittest.main()