import os
import tempfile
import unittest

from core.key_manager import generate_key_pair
from core.encrypt_engine import encrypt_file


class TestEncryptEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        os.makedirs("storage/keystores", exist_ok=True)

        generate_key_pair("amisha")

        self.test_file = "sample.txt"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Hello CryptoSign")

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp_dir.cleanup()

    def test_encrypt_file_success(self):
        output = encrypt_file(
            self.test_file,
            "storage/keystores/amisha_public.pem",
            "amisha"
        )

        self.assertTrue(os.path.exists(output))
        self.assertTrue(output.endswith(".bin"))

    def test_encrypt_missing_input_file(self):
        with self.assertRaises(FileNotFoundError):
            encrypt_file(
                "missing.txt",
                "storage/keystores/amisha_public.pem",
                "amisha"
            )

    def test_encrypt_missing_public_key(self):
        with self.assertRaises(FileNotFoundError):
            encrypt_file(
                self.test_file,
                "storage/keystores/missing_public.pem",
                "amisha"
            )

    def test_output_file_created(self):
        output = encrypt_file(
            self.test_file,
            "storage/keystores/amisha_public.pem",
            "amisha"
        )

        self.assertGreater(os.path.getsize(output), 0)


if __name__ == "__main__":
    unittest.main()