import os
import tempfile
import unittest

from core.key_manager import generate_key_pair
from core.ca_engine import create_root_ca, load_ca_private_key
from core.cert_manager import issue_certificate
from core.sign_engine import sign_document
from core.verify_engine import verify_document


class TestVerifyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        create_root_ca()
        private_key, public_key = generate_key_pair("amisha")
        issue_certificate(load_ca_private_key(), public_key, "amisha")

        self.test_file = "sample.txt"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Hello CryptoSign")

        self.private_key_path = "storage/keystores/amisha_private.pem"
        self.public_key_path = "storage/keystores/amisha_public.pem"

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp_dir.cleanup()

    def test_verify_valid_external_signature(self):
        sign_document(self.test_file, self.private_key_path, "amisha")

        result = verify_document(self.test_file, self.public_key_path, "amisha")

        self.assertEqual(result, "VALID")

    def test_verify_unsigned_file(self):
        result = verify_document(self.test_file, self.public_key_path, "amisha")

        self.assertEqual(result, "NOT_SIGNED")

    def test_verify_missing_file(self):
        result = verify_document("missing.txt", self.public_key_path, "amisha")

        self.assertEqual(result, "ERROR")

    def test_verify_tampered_file_invalid(self):
        sign_document(self.test_file, self.private_key_path, "amisha")

        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Tampered content")

        result = verify_document(self.test_file, self.public_key_path, "amisha")

        self.assertEqual(result, "INVALID")


if __name__ == "__main__":
    unittest.main()