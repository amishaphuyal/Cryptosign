import unittest
from unittest.mock import patch, MagicMock
from core import auto_convert


class TestAutoConvert(unittest.TestCase):

    def test_pdf_returns_same_file(self):
        self.assertEqual(auto_convert.convert_to_pdf("sample.pdf"), "sample.pdf")

    def test_unsupported_file_returns_none(self):
        self.assertIsNone(auto_convert.convert_to_pdf("sample.txt"))

    @patch("core.auto_convert.DOCX_AVAILABLE", False)
    def test_docx_without_converter_returns_none(self):
        self.assertIsNone(auto_convert.convert_to_pdf("sample.docx"))

    @patch("core.auto_convert.DOCX_AVAILABLE", True)
    def test_docx_conversion_success(self):
        auto_convert.convert = MagicMock()

        result = auto_convert.convert_to_pdf("sample.docx")

        auto_convert.convert.assert_called_once_with("sample.docx", "sample.pdf")
        self.assertEqual(result, "sample.pdf")

    @patch("core.auto_convert.DOCX_AVAILABLE", True)
    def test_docx_conversion_failure_returns_none(self):
        auto_convert.convert = MagicMock(side_effect=Exception("convert failed"))

        result = auto_convert.convert_to_pdf("sample.docx")

        auto_convert.convert.assert_called_once_with("sample.docx", "sample.pdf")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()