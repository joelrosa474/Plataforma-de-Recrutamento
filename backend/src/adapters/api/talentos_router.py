from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.adapters.api.dependencies import get_current_empresa
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import UsuarioModel


router = APIRouter(prefix="/api/talentos", tags=["Banco de Talentos"])


class TalentoResponse(BaseModel):
    id: int
    nome: str
    email: str
    localizacao: Optional[str] = None
    experiencia: Optional[str] = None
    competencias: List[str] = []
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class TalentosPage(BaseModel):
    items: List[TalentoResponse]
    total: int
    pagina: int
    tamanho: int


@router.get("/", response_model=TalentosPage)
def pesquisar_talentos(
    termo: Optional[str] = Query(default=None, max_length=100),
    localizacao: Optional[str] = Query(default=None, max_length=100),
    pagina: int = Query(default=1, ge=1),
    tamanho: int = Query(default=20, ge=1, le=50),
    current_user=Depends(get_current_empresa),
    db: Session = Depends(get_db),
):
    """Lista apenas candidatos que autorizaram a divulgação no Banco de Talentos."""
    query = db.query(UsuarioModel).filter(
        UsuarioModel.tipo_perfil == "Candidato",
        UsuarioModel.perfil_publico_talentos == 1,
    )

    if termo and termo.strip():
        busca = f"%{termo.strip()}%"
        query = query.filter(or_(
            UsuarioModel.nome.ilike(busca),
            UsuarioModel.experiencia.ilike(busca),
            UsuarioModel.competencias.ilike(busca),
        ))
    if localizacao and localizacao.strip():
        query = query.filter(UsuarioModel.localizacao.ilike(f"%{localizacao.strip()}%"))

    total = query.count()
    candidatos = query.order_by(UsuarioModel.nome.asc()).offset((pagina - 1) * tamanho).limit(tamanho).all()
    return TalentosPage(
        items=[
            TalentoResponse(
                id=candidato.id,
                nome=candidato.nome,
                email=candidato.email,
                localizacao=candidato.localizacao,
                experiencia=candidato.experiencia,
                competencias=candidato.get_competencias_list(),
                linkedin_url=candidato.linkedin_url,
                github_url=candidato.github_url,
            )
            for candidato in candidatos
        ],
        total=total,
        pagina=pagina,
        tamanho=tamanho,
    )
