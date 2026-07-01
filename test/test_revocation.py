import os
import tempfile
import unittest
from unittest.mock import patch

from core import revocation


class TestRevocation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.revoked_file = os.path.join(self.temp_dir.name, "revoked.txt")

        self.patcher = patch.object(revocation, "REVOCATION_FILE", self.revoked_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_revoke_user(self):
        self.assertTrue(revocation.revoke_user("amisha"))
        self.assertTrue(revocation.is_revoked("amisha"))

    def test_duplicate_revoke(self):
        revocation.revoke_user("amisha")
        revocation.revoke_user("amisha")

        users = revocation._read_revoked_users()
        self.assertEqual(len(users), 1)

    def test_unrevoke_user(self):
        revocation.revoke_user("amisha")
        self.assertTrue(revocation.unrevoke_user("amisha"))
        self.assertFalse(revocation.is_revoked("amisha"))

    def test_unrevoke_non_existing_user(self):
        self.assertFalse(revocation.unrevoke_user("unknown"))

    def test_empty_username(self):
        self.assertFalse(revocation.revoke_user(""))
        self.assertFalse(revocation.is_revoked(""))

    def test_case_insensitive_lookup(self):
        revocation.revoke_user("Amisha")

        self.assertTrue(revocation.is_revoked("amisha"))
        self.assertTrue(revocation.is_revoked("AMISHA"))


if __name__ == "__main__":
    unittest.main()