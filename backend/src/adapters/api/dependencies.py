from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.infrastructure.security.jwt_service import SECRET_KEY, ALGORITHM
from src.infrastructure.database.config import get_db
from src.infrastructure.repositories.usuario_repository_sqlalchemy import UsuarioRepositorySQLAlchemy

# OAuth2 com a URL do endpoint de login para uso no Swagger (auto_error=False para permitir cookies)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou sessão expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1º Tenta extrair do cookie HttpOnly; 2º Tenta extrair do cabeçalho Bearer
    token = request.cookies.get("rh_access_token") or bearer_token

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario_repo = UsuarioRepositorySQLAlchemy(db)
    user = usuario_repo.buscar_por_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user


def get_current_empresa(current_user = Depends(get_current_user)):
    if current_user.tipo_perfil != "Empresa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas utilizadores do tipo Empresa podem realizar esta ação."
        )
    return current_user


def get_current_candidato(current_user = Depends(get_current_user)):
    if current_user.tipo_perfil != "Candidato":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas candidatos podem realizar esta ação.")
    return current_user


def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.tipo_perfil != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem realizar esta ação.")
    return current_user
