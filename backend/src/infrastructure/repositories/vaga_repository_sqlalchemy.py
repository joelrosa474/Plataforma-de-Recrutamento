from typing import List, Optional
from sqlalchemy.orm import Session
from src.application.ports.vaga_repository import VagaRepository
from src.domain.entities.vaga import Vaga
from src.infrastructure.database.models import VagaModel

class VagaRepositorySQLAlchemy(VagaRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, vaga: Vaga) -> Vaga:
        if vaga.id is None:
            # Criar nova vaga
            db_vaga = VagaModel(
                empresa_id=vaga.empresa_id,
                titulo=vaga.titulo,
                descricao=vaga.descricao,
                status=vaga.status,
                localizacao=vaga.localizacao,
                modalidade=vaga.modalidade,
                area=vaga.area,
            )
            db_vaga.set_requisitos_list(vaga.requisitos)
            self.db.add(db_vaga)
        else:
            # Atualizar vaga existente
            db_vaga = self.db.query(VagaModel).filter(VagaModel.id == vaga.id).first()
            if db_vaga:
                db_vaga.empresa_id = vaga.empresa_id
                db_vaga.titulo = vaga.titulo
                db_vaga.descricao = vaga.descricao
                db_vaga.set_requisitos_list(vaga.requisitos)
                db_vaga.status = vaga.status
                db_vaga.localizacao = vaga.localizacao
                db_vaga.modalidade = vaga.modalidade
                db_vaga.area = vaga.area

        self.db.commit()
        self.db.refresh(db_vaga)
        return self._to_entity(db_vaga)

    def buscar_por_id(self, vaga_id: int) -> Optional[Vaga]:
        db_vaga = self.db.query(VagaModel).filter(VagaModel.id == vaga_id).first()
        if db_vaga:
            return self._to_entity(db_vaga)
        return None

    def listar_abertas(self) -> List[Vaga]:
        db_vagas = self.db.query(VagaModel).filter(VagaModel.status == "Aberta").all()
        return [self._to_entity(v) for v in db_vagas]

    def listar_todas(self) -> List[Vaga]:
        return [self._to_entity(v) for v in self.db.query(VagaModel).order_by(VagaModel.id.desc()).all()]

    def deletar(self, vaga_id: int) -> bool:
        vaga = self.db.query(VagaModel).filter(VagaModel.id == vaga_id).first()
        if not vaga:
            return False
        self.db.delete(vaga)
        self.db.commit()
        return True

    def _to_entity(self, model: VagaModel) -> Vaga:
        return Vaga(
            id=model.id,
            empresa_id=model.empresa_id,
            titulo=model.titulo,
            descricao=model.descricao,
            requisitos=model.get_requisitos_list(),
            status=model.status,
            localizacao=model.localizacao,
            modalidade=model.modalidade,
            area=model.area,
            data_criacao=model.data_criacao
        )
