import os
import tempfile
import unittest

from core.key_manager import generate_key_pair
from core.encrypt_engine import encrypt_file
from core.decrypt_engine import decrypt_file


class TestDecryptEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        generate_key_pair("amisha")

        self.original_file = "sample.txt"
        with open(self.original_file, "w", encoding="utf-8") as f:
            f.write("Hello CryptoSign")

        self.encrypted_file = encrypt_file(
            self.original_file,
            "storage/keystores/amisha_public.pem",
            "amisha"
        )

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp_dir.cleanup()

    def test_decrypt_file_success(self):
        output = decrypt_file("amisha", self.encrypted_file)

        self.assertTrue(os.path.exists(output))

        with open(output, "r", encoding="utf-8") as f:
            data = f.read()

        self.assertEqual(data, "Hello CryptoSign")

    def test_decrypt_missing_private_key(self):
        os.remove("storage/keystores/amisha_private.pem")

        with self.assertRaises(FileNotFoundError):
            decrypt_file("amisha", self.encrypted_file)

    def test_decrypt_missing_encrypted_file(self):
        with self.assertRaises(FileNotFoundError):
            decrypt_file("amisha", "missing.bin")

    def test_decrypt_with_wrong_user(self):
        with self.assertRaises(FileNotFoundError):
            decrypt_file("unknown", self.encrypted_file)


if __name__ == "__main__":
    unittest.main()