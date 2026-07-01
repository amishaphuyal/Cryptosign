import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core.key_manager import generate_key_pair
from core.sign_engine import sign_document


class TestSignEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        generate_key_pair("amisha")

        self.test_file = "sample.txt"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Hello CryptoSign")

        self.private_key = "storage/keystores/amisha_private.pem"

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp_dir.cleanup()

    def test_sign_document_success(self):
        sig_path = sign_document(self.test_file, self.private_key, "amisha")

        self.assertTrue(os.path.exists(sig_path))
        self.assertTrue(sig_path.endswith(".sig"))

    def test_signature_contains_metadata(self):
        sig_path = sign_document(self.test_file, self.private_key, "amisha")

        with open(sig_path, "r") as f:
            data = json.load(f)

        self.assertEqual(data["signer"], "amisha")
        self.assertEqual(data["algorithm"], "SHA256_RSA_PSS")
        self.assertEqual(data["original_filename"], "sample.txt")
        self.assertIn("signature", data)
        self.assertIn("file_hash", data)

    def test_original_location_sig_created(self):
        sign_document(self.test_file, self.private_key, "amisha")

        self.assertTrue(os.path.exists("sample.sig"))

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            sign_document("missing.txt", self.private_key, "amisha")

    def test_missing_private_key_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            sign_document(self.test_file, "missing_private.pem", "amisha")

    @patch("core.sign_engine.is_revoked", return_value=True)
    def test_revoked_user_cannot_sign(self, mock_revoked):
        with self.assertRaises(PermissionError):
            sign_document(self.test_file, self.private_key, "amisha")

    def test_audit_logger_tracks_signed_file(self):
        mock_audit = MagicMock()

        sig_path = sign_document(
            self.test_file,
            self.private_key,
            "amisha",
            audit_logger=mock_audit
        )

        mock_audit.add_user_file.assert_called_once()
        self.assertTrue(os.path.exists(sig_path))


if __name__ == "__main__":
    unittest.main()