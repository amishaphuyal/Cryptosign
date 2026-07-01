import os
import tempfile
import unittest

from cryptography import x509

from core.ca_engine import create_root_ca, load_ca_private_key
from core.key_manager import generate_key_pair
from core.cert_manager import issue_certificate


class TestCertManager(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp.name)

        create_root_ca()
        self.ca_private = load_ca_private_key()

        _, self.public_key = generate_key_pair("amisha")

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp.cleanup()

    def test_issue_certificate_success(self):
        cert_path = issue_certificate(
            self.ca_private,
            self.public_key,
            "amisha"
        )

        self.assertTrue(os.path.exists(cert_path))

    def test_certificate_subject(self):
        cert_path = issue_certificate(
            self.ca_private,
            self.public_key,
            "amisha"
        )

        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())

        self.assertIn("CN=amisha", cert.subject.rfc4514_string())

    def test_certificate_issuer(self):
        cert_path = issue_certificate(
            self.ca_private,
            self.public_key,
            "amisha"
        )

        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())

        self.assertEqual(cert.issuer, cert.issuer)

    def test_missing_ca_certificate(self):
        os.remove("storage/ca/ca_cert.pem")

        with self.assertRaises(FileNotFoundError):
            issue_certificate(
                self.ca_private,
                self.public_key,
                "amisha"
            )


if __name__ == "__main__":
    unittest.main()