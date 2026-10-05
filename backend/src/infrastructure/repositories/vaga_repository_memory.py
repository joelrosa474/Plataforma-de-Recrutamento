from typing import List, Optional
from src.domain.entities.vaga import Vaga
from src.application.ports.vaga_repository import VagaRepository

class VagaRepositoryMemory(VagaRepository):
    def __init__(self):
        self.vagas: List[Vaga] = []
        self._current_id = 1

    def salvar(self, vaga: Vaga) -> Vaga:
        if vaga.id is None:
            vaga.id = self._current_id
            self._current_id += 1
            self.vagas.append(vaga)
            return vaga

        for i, v in enumerate(self.vagas):
            if v.id == vaga.id:
                self.vagas[i] = vaga
                return vaga

        vaga.id = self._current_id
        self._current_id += 1
        self.vagas.append(vaga)
        return vaga

    def buscar_por_id(self, vaga_id: int) -> Optional[Vaga]:
        for vaga in self.vagas:
            if vaga.id == vaga_id:
                return vaga
        return None

    def listar_todas(self) -> List[Vaga]:
        return self.vagas

    def deletar(self, vaga_id: int) -> bool:
        vaga = self.buscar_por_id(vaga_id)
        if vaga:
            self.vagas.remove(vaga)
            return True
        return False
