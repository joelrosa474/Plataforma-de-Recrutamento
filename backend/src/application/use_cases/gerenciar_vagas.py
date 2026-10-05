from typing import List, Optional
from src.domain.entities.vaga import Vaga
from src.application.ports.vaga_repository import VagaRepository

class GerenciarVagasUseCase:
    def __init__(self, repository: VagaRepository):
        self.repository = repository

    def criar_vaga(self, empresa_id: int, titulo: str, descricao: str, requisitos: List[str], localizacao: str | None = None, modalidade: str | None = None, area: str | None = None) -> Vaga:
        nova_vaga = Vaga(empresa_id=empresa_id, titulo=titulo, descricao=descricao, requisitos=requisitos, localizacao=localizacao, modalidade=modalidade, area=area)
        return self.repository.salvar(nova_vaga)

    def listar_vagas_abertas(self) -> List[Vaga]:
        vagas = self.repository.listar_todas()
        return [vaga for vaga in vagas if vaga.status == "Aberta"]

    def buscar_vaga(self, vaga_id: int) -> Optional[Vaga]:
        return self.repository.buscar_por_id(vaga_id)

    def listar_vagas_da_empresa(self, empresa_id: int) -> List[Vaga]:
        return [vaga for vaga in self.repository.listar_todas() if vaga.empresa_id == empresa_id]

    def fechar_vaga(self, vaga_id: int, empresa_id: int) -> Optional[Vaga]:
        vaga = self.repository.buscar_por_id(vaga_id)
        if vaga and vaga.empresa_id == empresa_id:
            vaga.fechar_vaga()
            return self.repository.salvar(vaga)
        return None

    def pausar_vaga(self, vaga_id: int, empresa_id: int) -> Optional[Vaga]:
        vaga = self.repository.buscar_por_id(vaga_id)
        if vaga and vaga.empresa_id == empresa_id and vaga.status == "Aberta":
            vaga.pausar_vaga()
            return self.repository.salvar(vaga)
        return None

    def atualizar_vaga(self, vaga_id: int, empresa_id: int, titulo: str, descricao: str, requisitos: List[str], localizacao: str | None = None, modalidade: str | None = None, area: str | None = None) -> Optional[Vaga]:
        vaga = self.repository.buscar_por_id(vaga_id)
        if not vaga or vaga.empresa_id != empresa_id:
            return None
        vaga.titulo, vaga.descricao, vaga.requisitos = titulo, descricao, requisitos
        vaga.localizacao, vaga.modalidade, vaga.area = localizacao, modalidade, area
        return self.repository.salvar(vaga)

    def deletar_vaga(self, vaga_id: int, empresa_id: int) -> bool:
        vaga = self.repository.buscar_por_id(vaga_id)
        return bool(vaga and vaga.empresa_id == empresa_id and self.repository.deletar(vaga_id))
