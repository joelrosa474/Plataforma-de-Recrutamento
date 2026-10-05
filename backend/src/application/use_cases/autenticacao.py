import os
import re
from src.domain.entities.usuario import Usuario
from src.application.ports.usuario_repository import UsuarioRepository
from src.infrastructure.security.hasher import Hasher
from src.infrastructure.security.jwt_service import JWTService

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class AutenticacaoUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def registrar(self, nome: str, email: str, senha_plana: str, tipo_perfil: str) -> Usuario:
        nome = nome.strip()
        email = email.strip().lower()
        if not nome:
            raise ValueError("O nome é obrigatório.")
        if not self._email_valido(email):
            raise ValueError("E-mail inválido.")
        if len(senha_plana) < 8:
            raise ValueError("A palavra-passe deve ter pelo menos 8 caracteres.")
        perfis_publicos = {"Candidato", "Empresa"}
        if tipo_perfil not in perfis_publicos:
            raise ValueError("Tipo de perfil inválido.")
        admins = self._admin_emails()
        if email in admins:
            tipo_perfil = "Administrador"
        usuario_existente = self.usuario_repo.buscar_por_email(email)
        if usuario_existente:
            raise ValueError("Email já cadastrado.")

        senha_hash = Hasher.gerar_hash(senha_plana)
        novo_usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, tipo_perfil=tipo_perfil)
        return self.usuario_repo.salvar(novo_usuario)

    def login(self, email: str, senha_plana: str) -> str:
        email = email.strip().lower()
        usuario = self.usuario_repo.buscar_por_email(email)
        if not usuario or not Hasher.verificar_senha(senha_plana, usuario.senha_hash):
            raise ValueError("Email ou senha incorretos.")
        if email in self._admin_emails() and usuario.tipo_perfil != "Administrador":
            usuario.tipo_perfil = "Administrador"
            usuario = self.usuario_repo.salvar(usuario)

        token_data = {"sub": str(usuario.id), "tipo_perfil": usuario.tipo_perfil}
        return JWTService.criar_token_acesso(token_data)

    @staticmethod
    def _email_valido(email: str) -> bool:
        return bool(EMAIL_REGEX.fullmatch(email))

    @staticmethod
    def _admin_emails() -> set[str]:
        return {item.strip().lower() for item in os.environ.get("ADMIN_EMAILS", "").split(",") if item.strip()}
