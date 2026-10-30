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
        self.assertEqual(payload["error"]["status"], 401)
        self.assertEqual(payload["error"]["request_id"], response.headers["X-Request-Id"])

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
        self.assertEqual(payload["error"]["status"], 422)
        self.assertEqual(payload["error"]["request_id"], response.headers["X-Request-Id"])

    def test_origem_nao_autorizada_e_rejeitada_antes_da_operacao(self):
        response = self.client.post("/api/auth/logout", headers={"Origin": "https://site-malicioso.example"})

        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "csrf_origin_forbidden")
        self.assertEqual(payload["error"]["request_id"], response.headers["X-Request-Id"])

    def test_origem_configurada_nao_e_bloqueada_pela_protecao_csrf(self):
        response = self.client.post(
            "/api/auth/login",
            data={"username": "naoexiste@teste.com", "password": "senhaerrada"},
            headers={"Origin": "http://localhost:3000"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "invalid_credentials")


if __name__ == "__main__":
    unittest.main()
