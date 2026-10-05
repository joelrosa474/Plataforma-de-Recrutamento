import os
import unittest
from unittest.mock import patch

from src.application.use_cases.autenticacao import AutenticacaoUseCase
from src.infrastructure.repositories.usuario_repository_memory import UsuarioRepositoryMemory


class TestAutenticacaoUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = UsuarioRepositoryMemory()
        self.use_case = AutenticacaoUseCase(self.repo)

    def test_registrar_cria_usuario_e_hash_valido(self):
        usuario = self.use_case.registrar("Ana Silva", "ana@teste.com", "senha123", "Candidato")

        self.assertEqual(usuario.email, "ana@teste.com")
        self.assertEqual(usuario.tipo_perfil, "Candidato")
        self.assertIsNotNone(usuario.senha_hash)
        self.assertNotEqual(usuario.senha_hash, "senha123")

    def test_registrar_rejeita_email_duplicado(self):
        self.use_case.registrar("Ana Silva", "ana@teste.com", "senha123", "Candidato")

        with self.assertRaisesRegex(ValueError, "Email já cadastrado"):
            self.use_case.registrar("Outra Pessoa", "ana@teste.com", "outraSenha123", "Candidato")

    def test_registrar_rejeita_senha_curta(self):
        with self.assertRaisesRegex(ValueError, "pelo menos 8"):
            self.use_case.registrar("Ana Silva", "ana@teste.com", "1234567", "Candidato")

    def test_registrar_rejeita_senha_longa(self):
        with self.assertRaisesRegex(ValueError, "72"):
            self.use_case.registrar("Ana Silva", "ana@teste.com", "a" * 73, "Candidato")

    def test_login_retorna_token_para_usuario_valido(self):
        self.use_case.registrar("Ana Silva", "ana@teste.com", "senha123", "Candidato")

        token = self.use_case.login("ana@teste.com", "senha123")

        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 20)

    def test_login_rejeita_senha_incorreta(self):
        self.use_case.registrar("Ana Silva", "ana@teste.com", "senha123", "Candidato")

        with self.assertRaisesRegex(ValueError, "Email ou senha incorretos"):
            self.use_case.login("ana@teste.com", "senha_errada")

    def test_login_promove_usuario_para_administrador(self):
        with patch.dict(os.environ, {"ADMIN_EMAILS": "admin@empresa.com"}, clear=False):
            self.use_case.registrar("Admin", "admin@empresa.com", "senha123", "Empresa")

            token = self.use_case.login("admin@empresa.com", "senha123")
            usuario = self.repo.buscar_por_email("admin@empresa.com")

            self.assertIsInstance(token, str)
            self.assertEqual(usuario.tipo_perfil, "Administrador")


if __name__ == "__main__":
    unittest.main()
