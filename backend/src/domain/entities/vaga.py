from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Vaga(BaseModel):
    id: Optional[int] = None
    empresa_id: Optional[int] = None
    titulo: str
    descricao: str
    status: str = "Aberta"  # Aberta, Fechada, Pausada
    requisitos: List[str] = Field(default_factory=list)
    localizacao: Optional[str] = None
    modalidade: Optional[str] = None
    area: Optional[str] = None
    data_criacao: datetime = Field(default_factory=datetime.now)

    def fechar_vaga(self):
        self.status = "Fechada"

    def pausar_vaga(self):
        self.status = "Pausada"
