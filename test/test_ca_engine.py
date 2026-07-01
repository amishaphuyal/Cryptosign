import os
import tempfile
import unittest

from core.ca_engine import create_root_ca, load_ca_private_key, load_ca_public_key


class TestCAEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.old_dir)
        self.temp_dir.cleanup()

    def test_create_root_ca_creates_files(self):
        create_root_ca()

        self.assertTrue(os.path.exists("storage/ca/ca_private.pem"))
        self.assertTrue(os.path.exists("storage/ca/ca_cert.pem"))

    def test_load_ca_private_key(self):
        create_root_ca()

        private_key = load_ca_private_key()

        self.assertIsNotNone(private_key)

    def test_load_ca_public_key(self):
        create_root_ca()

        public_key = load_ca_public_key()

        self.assertIsNotNone(public_key)

    def test_load_private_key_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_ca_private_key()

    def test_load_public_key_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_ca_public_key()


if __name__ == "__main__":
    unittest.main()