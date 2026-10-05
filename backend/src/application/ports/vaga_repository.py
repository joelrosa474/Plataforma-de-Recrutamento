from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.vaga import Vaga

class VagaRepository(ABC):
    @abstractmethod
    def salvar(self, vaga: Vaga) -> Vaga:
        pass

    @abstractmethod
    def buscar_por_id(self, vaga_id: int) -> Optional[Vaga]:
        pass

    @abstractmethod
    def listar_todas(self) -> List[Vaga]:
        pass

    @abstractmethod
    def deletar(self, vaga_id: int) -> bool:
        pass
