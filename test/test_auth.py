import unittest
import tempfile
import os

from core.auth_system import AuthSystem


class TestAuthSystem(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "auth_test.db")
        self.auth = AuthSystem(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_user(self):
        success, msg = self.auth.register("alice", "password123")
        self.assertTrue(success)

    def test_duplicate_user(self):
        self.auth.register("alice", "password123")
        success, msg = self.auth.register("alice", "password123")
        self.assertFalse(success)

    def test_pending_user_login(self):
        self.auth.register("bob", "abc123")

        user, msg = self.auth.login("bob", "abc123")

        self.assertIsNone(user)
        self.assertIn("pending", msg.lower())

    def test_activate_user_login(self):
        self.auth.register("john", "123456")

        self.auth.set_status("john", "active")

        user, msg = self.auth.login("john", "123456")

        self.assertIsNotNone(user)
        self.assertEqual(msg, "Success")

    def test_invalid_password(self):
        self.auth.register("ram", "password")

        self.auth.set_status("ram", "active")

        user, msg = self.auth.login("ram", "wrongpassword")

        self.assertIsNone(user)
        self.assertEqual(msg, "Invalid credentials!")

    def test_change_password(self):
        self.auth.register("hari", "oldpass")

        self.auth.set_status("hari", "active")

        success, msg = self.auth.change_password("hari", "newpass")

        self.assertTrue(success)

        user, msg = self.auth.login("hari", "newpass")

        self.assertIsNotNone(user)

    def test_blocked_user(self):
        self.auth.register("sita", "abc123")

        self.auth.set_status("sita", "blocked")

        user, msg = self.auth.login("sita", "abc123")

        self.assertIsNone(user)
        self.assertIn("blocked", msg.lower())


if __name__ == "__main__":
    unittest.main()