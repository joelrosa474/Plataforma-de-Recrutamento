import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY não configurada. Defina-a no ficheiro .env antes de iniciar a API.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia
RESET_TOKEN_EXPIRE_MINUTES = 15  # 15 minutos


class JWTService:
    @staticmethod
    def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def criar_token_recuperacao_senha(user_id: int, senha_hash: str) -> str:
        import hashlib
        expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        pwh = hashlib.sha256((senha_hash or "").encode("utf-8")).hexdigest()[:16]
        payload = {
            "sub": str(user_id),
            "pwh": pwh,
            "type": "password_reset",
            "exp": expire,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verificar_token_recuperacao_senha(token: str) -> tuple[int, str]:
        """Valida o token e retorna (user_id, pwh_fingerprint)."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "password_reset":
                raise ValueError("Tipo de token inválido para recuperação de senha.")
            user_id = payload.get("sub")
            pwh = payload.get("pwh")
            if not user_id or pwh is None:
                raise ValueError("Token malformado.")
            return int(user_id), str(pwh)
        except JWTError:
            raise ValueError("O token de recuperação é inválido ou já expirou.")
