import os
import logging
from typing import List, Literal, Optional
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from src.domain.entities.usuario import Usuario
from src.application.use_cases.autenticacao import AutenticacaoUseCase
from src.infrastructure.repositories.usuario_repository_sqlalchemy import UsuarioRepositorySQLAlchemy
from src.infrastructure.database.config import get_db
from src.adapters.api.dependencies import get_current_user, get_current_empresa
from src.infrastructure.security.hasher import Hasher
from src.infrastructure.security.jwt_service import JWTService
from src.infrastructure.security.rate_limiter import AuthRateLimiter
from src.infrastructure.database.models import VagaModel, CandidaturaModel

logger = logging.getLogger("rh_api")
router = APIRouter(prefix="/api/auth", tags=["Autenticação"])
RATE_LIMITER = AuthRateLimiter(max_attempts=5, window_seconds=60)


def get_auth_use_case(db: Session = Depends(get_db)):
    repo = UsuarioRepositorySQLAlchemy(db)
    return AutenticacaoUseCase(usuario_repo=repo)


class RegistroRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    tipo_perfil: Literal["Candidato", "Empresa"]

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        nome = valor.strip()
        if not nome:
            raise ValueError("O nome é obrigatório.")
        return nome

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A palavra-passe não pode exceder 72 bytes.")
        return valor


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo_perfil: str
    localizacao: str | None = None
    experiencia: str | None = None
    competencias: List[str] = []
    linkedin_url: str | None = None
    github_url: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse


class AtualizarPerfilRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    localizacao: str | None = None
    experiencia: str | None = None
    competencias: List[str] = []
    linkedin_url: str | None = None
    github_url: str | None = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        nome = valor.strip()
        if not nome:
            raise ValueError("O nome é obrigatório")
        return nome


class AtualizarEmailRequest(BaseModel):
    email: EmailStr
    senha_atual: str = Field(min_length=1)


class AtualizarSenhaRequest(BaseModel):
    senha_atual: str = Field(min_length=1)
    nova_senha: str = Field(min_length=8, max_length=72)


class ExcluirContaRequest(BaseModel):
    senha_atual: str


class RecuperarSenhaRequest(BaseModel):
    email: EmailStr


class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8, max_length=72)


@router.post("/registrar", response_model=UsuarioResponse)
def registrar(request: RegistroRequest, use_case: AutenticacaoUseCase = Depends(get_auth_use_case)):
    try:
        usuario_criado = use_case.registrar(
            nome=request.nome,
            email=request.email,
            senha_plana=request.senha,
            tipo_perfil=request.tipo_perfil
        )
        return usuario_criado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AutenticacaoUseCase = Depends(get_auth_use_case)
):
    client_key = form_data.username or "unknown"
    if not RATE_LIMITER.allow(client_key):
        raise HTTPException(status_code=429, detail="Muitas tentativas de login. Tente novamente mais tarde.")

    try:
        token = use_case.login(email=form_data.username, senha_plana=form_data.password)
        usuario = use_case.usuario_repo.buscar_por_email(form_data.username)

        # Configura Cookie HttpOnly Seguro para Produção
        is_prod = os.getenv("APP_ENV", "development").lower() == "production"
        response.set_cookie(
            key="rh_access_token",
            value=token,
            httponly=True,
            secure=is_prod,
            samesite="lax",
            max_age=86400,
            path="/"
        )

        return {"access_token": token, "token_type": "bearer", "usuario": usuario}
    except ValueError:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")


@router.post("/logout")
def logout(response: Response):
    """Limpa o cookie de sessão HttpOnly."""
    response.delete_cookie(key="rh_access_token", path="/")
    return {"message": "Sessão terminada com sucesso"}


@router.post("/recuperar-senha")
def solicitar_recuperacao_senha(request: RecuperarSenhaRequest, db: Session = Depends(get_db)):
    """Gera token temporário e assinado para recuperação de palavra-passe."""
    repo = UsuarioRepositorySQLAlchemy(db)
    user = repo.buscar_por_email(request.email.strip().lower())
    
    # Prevenção contra enumeração de usuários: sempre responde com mensagem genérica positiva
    msg = "Se o endereço estiver registado na nossa plataforma, enviámos um link com instruções para redefinir a palavra-passe."
    
    if not user:
        return {"message": msg}

    token = JWTService.criar_token_recuperacao_senha(user.id, user.senha_hash or "")
    logger.info(f"Token de recuperação gerado para {user.email}")

    payload = {"message": msg}
    # Em ambiente de desenvolvimento disponibiliza o token para testes locais
    if os.getenv("APP_ENV", "development").lower() != "production":
        payload["debug_token"] = token
        payload["debug_reset_link"] = f"/auth?mode=reset&token={token}"

    return payload


@router.post("/redefinir-senha")
def redefinir_senha(request: RedefinirSenhaRequest, db: Session = Depends(get_db)):
    """Aplica nova senha a partir de token assinado e válido."""
    try:
        user_id, pwh_prefix = JWTService.verificar_token_recuperacao_senha(request.token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    repo = UsuarioRepositorySQLAlchemy(db)
    user = repo.buscar_por_id(user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Utilizador não encontrado.")

    import hashlib
    current_fp = hashlib.sha256((user.senha_hash or "").encode("utf-8")).hexdigest()[:16]
    if current_fp != pwh_prefix:
        raise HTTPException(status_code=400, detail="Este link de recuperação expirou ou já foi utilizado.")

    user.senha_hash = Hasher.gerar_hash(request.nova_senha)
    repo.salvar(user)
    return {"message": "Palavra-passe redefinida com sucesso. Pode agora iniciar sessão com as novas credenciais."}


@router.get("/me", response_model=UsuarioResponse)
def meu_perfil(current_user = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def atualizar_meu_perfil(request: AtualizarPerfilRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.nome = request.nome.strip()
    if not current_user.nome:
        raise HTTPException(status_code=400, detail="O nome é obrigatório")
    current_user.localizacao = request.localizacao
    current_user.experiencia = request.experiencia
    current_user.competencias = request.competencias
    current_user.linkedin_url = request.linkedin_url
    current_user.github_url = request.github_url
    return UsuarioRepositorySQLAlchemy(db).salvar(current_user)


@router.get("/candidatos/{candidato_id}", response_model=UsuarioResponse)
def perfil_candidato(candidato_id: int, current_user = Depends(get_current_empresa), db: Session = Depends(get_db)):
    candidato = UsuarioRepositorySQLAlchemy(db).buscar_por_id(candidato_id)
    if not candidato or candidato.tipo_perfil != "Candidato":
        raise HTTPException(status_code=404, detail="Candidato não encontrado")
    return candidato


@router.put("/me/email", response_model=UsuarioResponse)
def atualizar_email(request: AtualizarEmailRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = UsuarioRepositorySQLAlchemy(db)
    email = request.email.strip().lower()
    if not Hasher.verificar_senha(request.senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Palavra-passe atual incorreta")
    existente = repo.buscar_por_email(email)
    if existente and existente.id != current_user.id:
        raise HTTPException(status_code=400, detail="Este e-mail já está em uso")
    current_user.email = email
    return repo.salvar(current_user)


@router.put("/me/senha", status_code=204)
def atualizar_senha(request: AtualizarSenhaRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(request.nova_senha) < 8:
        raise HTTPException(status_code=400, detail="A nova palavra-passe deve ter pelo menos 8 caracteres")
    if not Hasher.verificar_senha(request.senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Palavra-passe atual incorreta")
    current_user.senha_hash = Hasher.gerar_hash(request.nova_senha)
    UsuarioRepositorySQLAlchemy(db).salvar(current_user)


@router.delete("/me", status_code=204)
def excluir_conta(request: ExcluirContaRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not Hasher.verificar_senha(request.senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Palavra-passe atual incorreta")
    if current_user.tipo_perfil == "Empresa" and db.query(VagaModel).filter(VagaModel.empresa_id == current_user.id).first():
        raise HTTPException(status_code=409, detail="Feche ou elimine as vagas da empresa antes de eliminar a conta")
    if current_user.tipo_perfil == "Candidato" and db.query(CandidaturaModel).filter(CandidaturaModel.candidato_id == current_user.id).first():
        raise HTTPException(status_code=409, detail="Não é possível eliminar uma conta com candidaturas registadas")
    UsuarioRepositorySQLAlchemy(db).deletar(current_user.id)
