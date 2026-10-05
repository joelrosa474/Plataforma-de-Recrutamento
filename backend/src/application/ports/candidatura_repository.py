from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.candidatura import Candidatura

class CandidaturaRepository(ABC):
    @abstractmethod
    def salvar(self, candidatura: Candidatura) -> Candidatura:
        pass

    @abstractmethod
    def buscar_por_vaga(self, vaga_id: int) -> List[Candidatura]:
        pass

    @abstractmethod
    def buscar_por_candidato(self, candidato_id: int) -> List[Candidatura]:
        pass

    @abstractmethod
    def buscar_por_id(self, candidatura_id: int) -> Candidatura | None:
        pass
