import io
from pypdf import PdfReader

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024


class PDFService:
    @staticmethod
    def validate_pdf_file(filename: str, content_type: str, file_bytes: bytes) -> bool:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("O currículo tem de ser um ficheiro PDF.")

        if content_type and "pdf" not in content_type.lower():
            raise ValueError("O currículo tem de ser um ficheiro PDF válido.")

        if not file_bytes or len(file_bytes) == 0:
            raise ValueError("O currículo enviado está vazio.")

        if len(file_bytes) > MAX_PDF_SIZE_BYTES:
            raise ValueError("O currículo é demasiado grande. O limite é 10 MB.")

        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            if len(reader.pages) == 0:
                raise ValueError("O PDF do currículo não parece válido.")
            return True
        except Exception as exc:
            raise ValueError("O PDF do currículo não é válido ou não pôde ser lido.") from exc

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """
        Recebe os bytes de um ficheiro PDF e retorna o texto extraído.
        """
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Não foi possível processar o PDF do currículo: {str(e)}")
