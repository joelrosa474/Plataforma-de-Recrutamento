import unittest

from fastapi.testclient import TestClient

from src.main import app


class TestApiErrors(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_login_invalido_retorna_erro_padronizado(self):
        response = self.client.post(
            "/api/auth/login",
            data={"username": "naoexiste@teste.com", "password": "senhaerrada"},
        )

        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["detail"], "Email ou senha incorretos.")
        self.assertEqual(payload["error"]["code"], "invalid_credentials")

    def test_registro_com_dados_invalidos_retorna_erro_de_validacao(self):
        response = self.client.post(
            "/api/auth/registrar",
            json={"nome": "", "email": "email-invalido", "senha": "123", "tipo_perfil": "invalido"},
        )

        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertIn("detail", payload)
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["code"], "validation_error")


if __name__ == "__main__":
    unittest.main()
