import json
from typing import List
from sqlalchemy.orm import Session
from src.application.ports.candidatura_repository import CandidaturaRepository
from src.domain.entities.candidatura import Candidatura
from src.infrastructure.database.models import CandidaturaModel

class CandidaturaRepositorySQLAlchemy(CandidaturaRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        if candidatura.id is None:
            # Nova candidatura
            db_candidatura = CandidaturaModel(
                vaga_id=candidatura.vaga_id,
                candidato_id=candidatura.candidato_id,
                fase_atual=candidatura.fase_atual,
                match_score=candidatura.match_score,
                feedback_ia=candidatura.feedback_ia,
                analise_match_ia=json.dumps(candidatura.analise_match_ia, ensure_ascii=False) if candidatura.analise_match_ia else None,
                curriculo_path=candidatura.curriculo_path,
                curriculo_nome=candidatura.curriculo_nome,
                entrevista_data=candidatura.entrevista_data,
                entrevista_link=candidatura.entrevista_link,
                entrevista_notas=candidatura.entrevista_notas,
                data_aplicacao=candidatura.data_aplicacao
            )
            self.db.add(db_candidatura)
        else:
            # Atualizar
            db_candidatura = self.db.query(CandidaturaModel).filter(CandidaturaModel.id == candidatura.id).first()
            if db_candidatura:
                db_candidatura.fase_atual = candidatura.fase_atual
                db_candidatura.match_score = candidatura.match_score
                db_candidatura.feedback_ia = candidatura.feedback_ia
                db_candidatura.analise_match_ia = json.dumps(candidatura.analise_match_ia, ensure_ascii=False) if candidatura.analise_match_ia else None
                if candidatura.curriculo_path:
                    db_candidatura.curriculo_path = candidatura.curriculo_path
                if candidatura.curriculo_nome:
                    db_candidatura.curriculo_nome = candidatura.curriculo_nome
                db_candidatura.entrevista_data = candidatura.entrevista_data
                db_candidatura.entrevista_link = candidatura.entrevista_link
                db_candidatura.entrevista_notas = candidatura.entrevista_notas
        
        self.db.commit()
        self.db.refresh(db_candidatura)
        return self._to_entity(db_candidatura)

    def buscar_por_vaga(self, vaga_id: int) -> List[Candidatura]:
        db_candidaturas = self.db.query(CandidaturaModel).filter(CandidaturaModel.vaga_id == vaga_id).all()
        return [self._to_entity(c) for c in db_candidaturas]

    def buscar_por_candidato(self, candidato_id: int) -> List[Candidatura]:
        db_candidaturas = self.db.query(CandidaturaModel).filter(CandidaturaModel.candidato_id == candidato_id).all()
        return [self._to_entity(c) for c in db_candidaturas]

    def buscar_por_id(self, candidatura_id: int) -> Candidatura | None:
        candidatura = self.db.query(CandidaturaModel).filter(CandidaturaModel.id == candidatura_id).first()
        return self._to_entity(candidatura) if candidatura else None
        
    def _to_entity(self, model: CandidaturaModel) -> Candidatura:
        try:
            analise_match_ia = json.loads(model.analise_match_ia) if model.analise_match_ia else None
        except (TypeError, json.JSONDecodeError):
            analise_match_ia = None
        return Candidatura(
            id=model.id,
            vaga_id=model.vaga_id,
            candidato_id=model.candidato_id,
            fase_atual=model.fase_atual,
            match_score=model.match_score,
            feedback_ia=model.feedback_ia,
            analise_match_ia=analise_match_ia,
            curriculo_path=model.curriculo_path,
            curriculo_nome=model.curriculo_nome,
            entrevista_data=model.entrevista_data,
            entrevista_link=model.entrevista_link,
            entrevista_notas=model.entrevista_notas,
            data_aplicacao=model.data_aplicacao
        )
