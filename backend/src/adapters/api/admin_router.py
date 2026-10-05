from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.adapters.api.dependencies import get_current_admin
from src.adapters.api.auth_router import UsuarioResponse
from src.domain.entities.vaga import Vaga
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import UsuarioModel, VagaModel, CandidaturaModel
from src.infrastructure.repositories.usuario_repository_sqlalchemy import UsuarioRepositorySQLAlchemy
from src.infrastructure.repositories.vaga_repository_sqlalchemy import VagaRepositorySQLAlchemy

router = APIRouter(prefix="/api/admin", tags=["Administração"])

class ResumoAdmin(BaseModel):
    usuarios: int
    empresas: int
    candidatos: int
    vagas: int
    candidaturas: int

class AtualizarStatusVagaRequest(BaseModel):
    status: str

@router.get("/resumo", response_model=ResumoAdmin)
def resumo(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {
        "usuarios": db.query(UsuarioModel).count(),
        "empresas": db.query(UsuarioModel).filter(UsuarioModel.tipo_perfil == "Empresa").count(),
        "candidatos": db.query(UsuarioModel).filter(UsuarioModel.tipo_perfil == "Candidato").count(),
        "vagas": db.query(VagaModel).count(),
        "candidaturas": db.query(CandidaturaModel).count(),
    }

@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    repo = UsuarioRepositorySQLAlchemy(db)
    return [repo._to_entity(item) for item in db.query(UsuarioModel).order_by(UsuarioModel.id.desc()).all()]

@router.get("/vagas", response_model=list[Vaga])
def listar_vagas(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    repo = VagaRepositorySQLAlchemy(db)
    return [repo._to_entity(item) for item in db.query(VagaModel).order_by(VagaModel.id.desc()).all()]

@router.put("/vagas/{vaga_id}/status", response_model=Vaga)
def atualizar_status_vaga(vaga_id: int, request: AtualizarStatusVagaRequest, _: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    if request.status not in {"Aberta", "Pausada", "Fechada"}:
        raise HTTPException(status_code=400, detail="Estado de vaga inválido")
    vaga = db.query(VagaModel).filter(VagaModel.id == vaga_id).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    vaga.status = request.status
    db.commit()
    db.refresh(vaga)
    return VagaRepositorySQLAlchemy(db)._to_entity(vaga)
