import os
import unittest
from unittest.mock import MagicMock, patch

from src.infrastructure.ai.gemini_screener_adapter import GeminiScreenerAdapter, MatchScoreSchema


class TestGeminiFailover(unittest.TestCase):
    def setUp(self):
        os.environ["GEMINI_API_KEY"] = "fake-key-for-test"
        os.environ["GEMINI_PRIMARY_MODEL"] = "gemini-3.8-flash"
        os.environ["GEMINI_BACKUP_MODEL"] = "gemini-3.5-flash-lite"

    def test_inicializacao_com_dois_modelos(self):
        adapter = GeminiScreenerAdapter()
        self.assertEqual(adapter.primary_model, "gemini-3.8-flash")
        self.assertEqual(adapter.backup_model, "gemini-3.5-flash-lite")
        self.assertIsNotNone(adapter.client)
        self.assertIsNotNone(adapter.backup_client)

    def test_sucesso_usa_modelo_principal(self):
        adapter = GeminiScreenerAdapter()
        mock_response = MagicMock()
        mock_response.text = '{"score": 85.0, "justificativa": "Boa aderencia", "competencias_alinhadas": ["Python"], "requisitos_em_falta": [], "evidencias_experiencia": [], "recomendacao": "Aprovar"}'

        adapter.client.models.generate_content = MagicMock(return_value=mock_response)

        resultado = adapter._generate_content_with_fallback("teste", MatchScoreSchema)
        self.assertEqual(resultado["score"], 85.0)

        # Garante que o modelo chamado foi o primário
        adapter.client.models.generate_content.assert_called_once()
        call_kwargs = adapter.client.models.generate_content.call_args[1]
        self.assertEqual(call_kwargs["model"], "gemini-3.8-flash")

    def test_falha_no_principal_aciona_secundario_com_cooldown(self):
        adapter = GeminiScreenerAdapter()

        # Modelo primário simula erro 429 (Resource Exhausted)
        mock_success = MagicMock()
        mock_success.text = '{"score": 90.0, "justificativa": "Backup ok", "competencias_alinhadas": [], "requisitos_em_falta": [], "evidencias_experiencia": [], "recomendacao": "Ok"}'

        def side_effect(*args, **kwargs):
            if kwargs.get("model") == "gemini-3.8-flash":
                raise RuntimeError("429 RESOURCE_EXHAUSTED Quota exceeded")
            return mock_success

        adapter.client.models.generate_content = MagicMock(side_effect=side_effect)

        resultado = adapter._generate_content_with_fallback("teste", MatchScoreSchema)
        self.assertEqual(resultado["score"], 90.0)

        # Verifica se o cooldown foi ativado
        self.assertGreater(adapter._primary_cooldown_until, 0)

        # Na chamada seguinte dentro do cooldown, deve tentar o backup primeiro
        adapter.client.models.generate_content.reset_mock()
        adapter._generate_content_with_fallback("teste2", MatchScoreSchema)
        primeira_chamada_modelo = adapter.client.models.generate_content.call_args_list[0][1]["model"]
        self.assertEqual(primeira_chamada_modelo, "gemini-3.5-flash-lite")


if __name__ == "__main__":
    unittest.main()
