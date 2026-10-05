from typing import List
from src.domain.entities.candidatura import Candidatura
from src.application.ports.candidatura_repository import CandidaturaRepository

class CandidaturaRepositoryMemory(CandidaturaRepository):
    def __init__(self):
        self.candidaturas: List[Candidatura] = []
        self._current_id = 1

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        if candidatura.id is None:
            candidatura.id = self._current_id
            self._current_id += 1
            self.candidaturas.append(candidatura)
            return candidatura

        for i, c in enumerate(self.candidaturas):
            if c.id == candidatura.id:
                self.candidaturas[i] = candidatura
                return candidatura

        candidatura.id = self._current_id
        self._current_id += 1
        self.candidaturas.append(candidatura)
        return candidatura

    def buscar_por_vaga(self, vaga_id: int) -> List[Candidatura]:
        return [c for c in self.candidaturas if c.vaga_id == vaga_id]

    def buscar_por_candidato(self, candidato_id: int) -> List[Candidatura]:
        return [c for c in self.candidaturas if c.candidato_id == candidato_id]

    def buscar_por_id(self, candidatura_id: int) -> Candidatura | None:
        return next((c for c in self.candidaturas if c.id == candidatura_id), None)
