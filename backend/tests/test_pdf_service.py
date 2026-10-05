import unittest
from io import BytesIO

from pypdf import PdfWriter

from src.application.services.pdf_service import PDFService


class TestPDFService(unittest.TestCase):
    def test_validate_pdf_file_accepts_valid_pdf(self):
        buffer = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.write(buffer)
        payload = buffer.getvalue()

        result = PDFService.validate_pdf_file("curriculo.pdf", "application/pdf", payload)

        self.assertTrue(result)

    def test_validate_pdf_file_rejeita_tipo_invalido(self):
        with self.assertRaisesRegex(ValueError, "PDF"):
            PDFService.validate_pdf_file("curriculo.txt", "text/plain", b"texto")

    def test_validate_pdf_file_rejeita_pdf_vazio_ou_invalido(self):
        with self.assertRaisesRegex(ValueError, "válido"):
            PDFService.validate_pdf_file("curriculo.pdf", "application/pdf", b"not-a-pdf")

    def test_validate_pdf_file_rejeita_arquivo_grande(self):
        large_bytes = b"%PDF-1.4\n" + b"A" * (10 * 1024 * 1024 + 1)

        with self.assertRaisesRegex(ValueError, "10 MB"):
            PDFService.validate_pdf_file("curriculo.pdf", "application/pdf", large_bytes)


if __name__ == "__main__":
    unittest.main()
