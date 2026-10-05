import os
import tempfile
import unittest

from src.application.services.storage_service import StorageService


class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageService(base_dir=self.temp_dir)

    def tearDown(self):
        # Limpa arquivos temporários
        for f in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, f))
            except OSError:
                pass
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    def test_salvar_curriculo_valido(self):
        content = b"%PDF-1.4 simulated pdf content"
        path, clean_name = self.storage.salvar_curriculo(
            file_bytes=content,
            original_filename="Meu Curriculo Final (2026).pdf",
            vaga_id=10,
            candidato_id=42
        )

        self.assertTrue(os.path.exists(path))
        self.assertTrue(self.storage.arquivo_existe(path))
        self.assertIn("cv_vaga10_cand42_", path)
        self.assertNotIn(" ", clean_name)
        self.assertTrue(clean_name.endswith(".pdf"))

        with open(path, "rb") as f:
            self.assertEqual(f.read(), content)

    def test_remover_arquivo(self):
        content = b"%PDF-1.4 test delete"
        path, _ = self.storage.salvar_curriculo(content, "teste.pdf", 1, 1)
        self.assertTrue(self.storage.arquivo_existe(path))

        removido = self.storage.remover_arquivo(path)
        self.assertTrue(removido)
        self.assertFalse(self.storage.arquivo_existe(path))


if __name__ == "__main__":
    unittest.main()
