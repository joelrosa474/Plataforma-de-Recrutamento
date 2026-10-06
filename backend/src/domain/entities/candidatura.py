from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

VALID_FASES = {"Triagem", "Entrevista", "Contratado", "Reprovado"}
VALID_TRANSICOES = {
    "Triagem": {"Entrevista", "Reprovado"},
    "Entrevista": {"Contratado", "Reprovado"},
}


class Candidatura(BaseModel):
    id: Optional[int] = None
    vaga_id: int
    candidato_id: int
    fase_atual: str = "Triagem" # Triagem, Entrevista, Contratado, Reprovado
    match_score: Optional[float] = None
    feedback_ia: Optional[str] = None
    curriculo_path: Optional[str] = None
    curriculo_nome: Optional[str] = None
    data_aplicacao: datetime = Field(default_factory=datetime.now)

    def avancar_fase(self, nova_fase: str):
        if nova_fase not in VALID_FASES:
            raise ValueError(f"Fase inválida: {nova_fase}")
        fase_atual = self.fase_atual
        if fase_atual in {"Contratado", "Reprovado"}:
            raise ValueError("Transição de fase inválida: a candidatura já foi finalizada.")
        if nova_fase not in VALID_TRANSICOES.get(fase_atual, set()):
            raise ValueError("Transição de fase inválida.")
        self.fase_atual = nova_fase

    def registrar_score(self, score: float, feedback: Optional[str] = None):
        self.match_score = score
        if feedback is not None:
            self.feedback_ia = feedback
