import os
import uuid
import re
from typing import Optional


class StorageService:
    """Serviço de abstração de armazenamento de ficheiros para produção."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.base_dir = os.path.join(root, "uploads", "curriculos")
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        name = os.path.basename(filename)
        clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
        return clean or "documento.pdf"

    def salvar_curriculo(self, file_bytes: bytes, original_filename: str, vaga_id: int, candidato_id: int) -> tuple[str, str]:
        """
        Salva o ficheiro em disco (ou bucket) de forma segura.
        Retorna (caminho_ou_chave, nome_original_sanitizado).
        """
        clean_name = self._sanitize_filename(original_filename)
        ext = os.path.splitext(clean_name)[1].lower() or ".pdf"
        unique_token = uuid.uuid4().hex[:12]
        safe_name = f"cv_vaga{vaga_id}_cand{candidato_id}_{unique_token}{ext}"
        target_path = os.path.join(self.base_dir, safe_name)

        # Evita traversal
        resolved = os.path.abspath(target_path)
        if not resolved.startswith(os.path.abspath(self.base_dir)):
            raise ValueError("Tentativa de gravação em diretório não autorizado.")

        with open(resolved, "wb") as f:
            f.write(file_bytes)

        return resolved, clean_name

    def arquivo_existe(self, path_or_key: Optional[str]) -> bool:
        if not path_or_key:
            return False
        return os.path.exists(path_or_key)

    def remover_arquivo(self, path_or_key: Optional[str]) -> bool:
        if path_or_key and os.path.exists(path_or_key):
            try:
                os.remove(path_or_key)
                return True
            except OSError:
                return False
        return False
