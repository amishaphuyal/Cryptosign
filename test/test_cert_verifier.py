import os
import tempfile
import unittest

from core.ca_engine import create_root_ca, load_ca_private_key, load_ca_public_key
from core.key_manager import generate_key_pair
from core.cert_manager import issue_certificate
from core.cert_verifier import verify_certificate


class TestCertVerifier(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp.name)

        create_root_ca()
        self.ca_private = load_ca_private_key()
        self.ca_public = load_ca_public_key()

        _, public_key = generate_key_pair("amisha")
        self.cert_path = issue_certificate(self.ca_private, public_key, "amisha")

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp.cleanup()

    def test_verify_certificate_success(self):
        result = verify_certificate(self.cert_path, self.ca_public)

        self.assertTrue(result)

    def test_missing_certificate_file(self):
        result = verify_certificate("missing_cert.pem", self.ca_public)

        self.assertFalse(result)

    def test_invalid_certificate_file(self):
        with open("invalid_cert.pem", "w", encoding="utf-8") as f:
            f.write("not a real certificate")

        result = verify_certificate("invalid_cert.pem", self.ca_public)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()