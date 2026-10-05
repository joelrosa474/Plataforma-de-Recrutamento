import unittest
from fastapi.testclient import TestClient

from src.main import app
from src.infrastructure.database.config import SessionLocal
from src.infrastructure.database.models import UsuarioModel
from src.infrastructure.security.hasher import Hasher


class TestPasswordRecovery(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        # Limpa usuário de teste se existir
        self.db.query(UsuarioModel).filter(UsuarioModel.email == "recovery_test@empresa.com").delete()
        self.db.commit()

        # Cria usuário para teste
        self.usuario = UsuarioModel(
            nome="Recovery Test User",
            email="recovery_test@empresa.com",
            senha_hash=Hasher.gerar_hash("senhaAntiga123"),
            tipo_perfil="Candidato"
        )
        self.db.add(self.usuario)
        self.db.commit()
        self.db.refresh(self.usuario)

    def tearDown(self):
        self.db.query(UsuarioModel).filter(UsuarioModel.email == "recovery_test@empresa.com").delete()
        self.db.commit()
        self.db.close()

    def test_solicitar_e_redefinir_senha_com_sucesso(self):
        # 1. Solicita recuperação de senha
        res = self.client.post("/api/auth/recuperar-senha", json={"email": "recovery_test@empresa.com"})
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertIn("message", payload)
        self.assertIn("debug_token", payload)
        token = payload["debug_token"]

        # 2. Redefine a senha com o token recebido
        res_reset = self.client.post("/api/auth/redefinir-senha", json={
            "token": token,
            "nova_senha": "novaSenhaSuperSegura456"
        })
        self.assertEqual(res_reset.status_code, 200)
        self.assertIn("redefinida com sucesso", res_reset.json()["message"])

        # 3. Testa login com a nova senha
        res_login = self.client.post(
            "/api/auth/login",
            data={"username": "recovery_test@empresa.com", "password": "novaSenhaSuperSegura456"}
        )
        self.assertEqual(res_login.status_code, 200)
        # Verifica se o cookie HttpOnly foi enviado
        self.assertIn("rh_access_token", res_login.cookies)

        # 4. Tenta reutilizar o mesmo token (deve ser rejeitado)
        res_reuse = self.client.post("/api/auth/redefinir-senha", json={
            "token": token,
            "nova_senha": "outraSenhaInvalida789"
        })
        self.assertEqual(res_reuse.status_code, 400)


if __name__ == "__main__":
    unittest.main()
