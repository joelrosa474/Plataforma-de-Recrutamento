from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.domain.entities.vaga import Vaga
from src.application.use_cases.gerenciar_vagas import GerenciarVagasUseCase
from src.infrastructure.repositories.vaga_repository_sqlalchemy import VagaRepositorySQLAlchemy
from src.adapters.api.dependencies import get_current_empresa
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import UsuarioModel
from src.adapters.api.notificacoes_router import criar_notificacao

router = APIRouter(prefix="/api/vagas", tags=["Vagas"])

def get_vagas_use_case(db: Session = Depends(get_db)):
    repo = VagaRepositorySQLAlchemy(db)
    return GerenciarVagasUseCase(repository=repo)

class CriarVagaRequest(BaseModel):
    titulo: str
    descricao: str
    requisitos: List[str]
    localizacao: str | None = None
    modalidade: str | None = None
    area: str | None = None

class AtualizarVagaRequest(CriarVagaRequest):
    pass

class PaginaVagasResponse(BaseModel):
    items: List[Vaga]
    total: int
    pagina: int
    tamanho: int

@router.post("/", response_model=Vaga)
def criar_vaga(request: CriarVagaRequest, current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case), db: Session = Depends(get_db)):
    vaga = use_case.criar_vaga(
        empresa_id=current_user.id,
        titulo=request.titulo,
        descricao=request.descricao,
        requisitos=request.requisitos,
        localizacao=request.localizacao,
        modalidade=request.modalidade,
        area=request.area,
    )
    for candidato in db.query(UsuarioModel).filter(UsuarioModel.tipo_perfil == "Candidato").all():
        criar_notificacao(db, candidato.id, "Nova vaga disponível", f"{vaga.titulo} foi publicada por {current_user.nome}.")
    db.commit()
    return vaga

@router.get("/", response_model=List[Vaga])
def listar_vagas_abertas(use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    return use_case.listar_vagas_abertas()

@router.get("/minhas", response_model=List[Vaga])
def listar_minhas_vagas(current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    return use_case.listar_vagas_da_empresa(current_user.id)

@router.get("/busca", response_model=PaginaVagasResponse)
def buscar_vagas(
    termo: str = "",
    requisitos: List[str] = Query(default=[]),
    localizacao: str = "",
    modalidade: str = "",
    area: str = "",
    pagina: int = Query(default=1, ge=1),
    tamanho: int = Query(default=12, ge=1, le=50),
    use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case),
):
    termo_normalizado = termo.lower().strip()
    requisitos_normalizados = [item.lower().strip() for item in requisitos if item.strip()]
    localizacao_normalizada, modalidade_normalizada, area_normalizada = localizacao.lower().strip(), modalidade.lower().strip(), area.lower().strip()
    vagas = [vaga for vaga in use_case.listar_vagas_abertas() if (
        not termo_normalizado or termo_normalizado in f"{vaga.titulo} {vaga.descricao} {' '.join(vaga.requisitos)}".lower()
    ) and all(any(requisito in item.lower() for item in vaga.requisitos) for requisito in requisitos_normalizados)
        and (not localizacao_normalizada or localizacao_normalizada in (vaga.localizacao or "").lower())
        and (not modalidade_normalizada or modalidade_normalizada == (vaga.modalidade or "").lower())
        and (not area_normalizada or area_normalizada in (vaga.area or "").lower())]
    inicio = (pagina - 1) * tamanho
    return {"items": vagas[inicio:inicio + tamanho], "total": len(vagas), "pagina": pagina, "tamanho": tamanho}

@router.get("/{vaga_id}", response_model=Vaga)
def buscar_vaga(vaga_id: int, use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    vaga = use_case.buscar_vaga(vaga_id)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga

@router.put("/{vaga_id}/fechar", response_model=Vaga)
def fechar_vaga(vaga_id: int, current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    vaga = use_case.fechar_vaga(vaga_id, current_user.id)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga

@router.put("/{vaga_id}", response_model=Vaga)
def atualizar_vaga(vaga_id: int, request: AtualizarVagaRequest, current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    vaga = use_case.atualizar_vaga(vaga_id, current_user.id, request.titulo, request.descricao, request.requisitos, request.localizacao, request.modalidade, request.area)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga

@router.put("/{vaga_id}/pausar", response_model=Vaga)
def pausar_vaga(vaga_id: int, current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    vaga = use_case.pausar_vaga(vaga_id, current_user.id)
    if not vaga:
        raise HTTPException(status_code=400, detail="Não foi possível pausar esta vaga")
    return vaga

@router.delete("/{vaga_id}", status_code=204)
def deletar_vaga(vaga_id: int, current_user = Depends(get_current_empresa), use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case)):
    if not use_case.deletar_vaga(vaga_id, current_user.id):
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
