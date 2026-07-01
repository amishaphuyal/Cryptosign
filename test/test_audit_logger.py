import os
import unittest
import tempfile

from core.audit_logger import AuditLogger


class TestAuditLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "audit_test.db")
        self.logger = AuditLogger(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_log_creates_audit_entry(self):
        self.logger.log(
            username="testuser",
            action="SIGN",
            result="SUCCESS",
            file_name="document.pdf",
            file_hash="abc123",
            details="Document signed"
        )

        history = self.logger.get_user_history("testuser")

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][1], "SIGN")
        self.assertEqual(history[0][2], "document.pdf")
        self.assertEqual(history[0][3], "SUCCESS")

    def test_add_user_file(self):
        self.logger.add_user_file(
            username="testuser",
            file_type="signed",
            file_path="storage/signatures/test.sig",
            original_name="test.pdf",
            file_size=1234
        )

        files = self.logger.get_user_files("testuser")

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][1], "signed")
        self.assertEqual(files[0][2], "storage/signatures/test.sig")
        self.assertEqual(files[0][3], "test.pdf")

    def test_get_user_files_by_type(self):
        self.logger.add_user_file("testuser", "signed", "file1.sig", "file1.pdf", 100)
        self.logger.add_user_file("testuser", "encrypted", "file2.bin", "file2.pdf", 200)

        signed_files = self.logger.get_user_files("testuser", file_type="signed")

        self.assertEqual(len(signed_files), 1)
        self.assertEqual(signed_files[0][1], "signed")

    def test_delete_user_file(self):
        self.logger.add_user_file("testuser", "signed", "file1.sig", "file1.pdf", 100)

        result = self.logger.delete_user_file("testuser", "file1.sig")
        files = self.logger.get_user_files("testuser")

        self.assertTrue(result)
        self.assertEqual(len(files), 0)

    def test_get_statistics(self):
        self.logger.log("testuser", "SIGN", "SUCCESS")
        self.logger.log("testuser", "SIGN", "FAILED")
        self.logger.log("testuser", "VERIFY", "VALID")

        stats = self.logger.get_statistics("testuser")
        stats_dict = {row[0]: (row[1], row[2]) for row in stats}

        self.assertEqual(stats_dict["SIGN"], (2, 1))
        self.assertEqual(stats_dict["VERIFY"], (1, 1))

    def test_export_to_csv(self):
        self.logger.log("testuser", "SIGN", "SUCCESS", file_name="doc.pdf")

        csv_path = os.path.join(self.temp_dir.name, "audit_export.csv")
        result = self.logger.export_to_csv(csv_path, username="testuser")

        self.assertEqual(result, csv_path)
        self.assertTrue(os.path.exists(csv_path))


if __name__ == "__main__":
    unittest.main()