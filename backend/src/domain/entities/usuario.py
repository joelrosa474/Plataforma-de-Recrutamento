from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    id: Optional[int] = None
    nome: str
    email: str
    senha_hash: str
    tipo_perfil: str # 'Candidato', 'Recrutador', 'Admin'
    localizacao: Optional[str] = None
    experiencia: Optional[str] = None
    competencias: list[str] = []
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
