from passlib.context import CryptContext

# bcrypt aceita no máximo 72 bytes e pode truncar palavras-passe longas.
# bcrypt_sha256 aplica SHA-256 antes do bcrypt, preservando compatibilidade
# de verificação com os hashes bcrypt já existentes no banco.
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
MAX_PASSWORD_BYTES = 72


class Hasher:
    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        return pwd_context.verify(senha_plana, senha_hash)

    @staticmethod
    def gerar_hash(senha: str) -> str:
        encoded = senha.encode("utf-8")
        if len(encoded) > MAX_PASSWORD_BYTES:
            raise ValueError("A palavra-passe não pode exceder 72 bytes. Escolha uma senha mais curta.")
        return pwd_context.hash(senha)
