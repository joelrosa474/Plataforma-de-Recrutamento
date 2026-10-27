from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.domain.entities.vaga import Vaga
from src.application.use_cases.gerenciar_vagas import GerenciarVagasUseCase
from src.infrastructure.repositories.vaga_repository_sqlalchemy import VagaRepositorySQLAlchemy
from src.adapters.api.dependencies import get_current_empresa, get_current_candidato
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import CandidaturaModel, UsuarioModel
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


class VagaRecomendadaResponse(Vaga):
    match_score: float
    motivos: List[str]


def normalizar(texto: str | None) -> str:
    return (texto or "").lower().strip()


def recomendar_vaga(vaga: Vaga, competencias: List[str], experiencia: str | None, localizacao: str | None) -> tuple[float, List[str]]:
    """Calcula uma recomendação determinística e explicável, sem inferir dados sensíveis."""
    competencias_normalizadas = [normalizar(item) for item in competencias if normalizar(item)]
    experiencia_normalizada = normalizar(experiencia)
    requisitos = [normalizar(item) for item in vaga.requisitos if normalizar(item)]
    correspondentes = [
        requisito for requisito in requisitos
        if any(requisito in competencia or competencia in requisito for competencia in competencias_normalizadas)
    ]
    score = (70 * len(correspondentes) / len(requisitos)) if requisitos else 35
    motivos: List[str] = []
    if correspondentes:
        motivos.append(f"Competências alinhadas: {', '.join(vaga.requisitos[requisitos.index(item)] for item in correspondentes[:3])}.")

    if normalizar(vaga.area) and normalizar(vaga.area) in experiencia_normalizada:
        score += 10
        motivos.append(f"A sua experiência menciona a área de {vaga.area}.")

    mesma_localizacao = bool(normalizar(localizacao) and normalizar(vaga.localizacao) and normalizar(localizacao) in normalizar(vaga.localizacao))
    if normalizar(vaga.modalidade) == "remoto" or mesma_localizacao:
        score += 15
        motivos.append("A modalidade ou localização é compatível com o seu perfil.")

    if experiencia_normalizada:
        score += 5
    if not motivos:
        motivos.append("Recomendação baseada nas informações atualmente preenchidas no seu perfil.")
    return round(min(score, 100), 1), motivos

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


@router.get("/recomendadas", response_model=List[VagaRecomendadaResponse])
def listar_vagas_recomendadas(
    limite: int = Query(default=3, ge=1, le=10),
    current_user=Depends(get_current_candidato),
    use_case: GerenciarVagasUseCase = Depends(get_vagas_use_case),
    db: Session = Depends(get_db),
):
    """Sugere vagas abertas ainda não candidatas, com critérios que o candidato pode compreender."""
    vagas_candidatadas = {
        candidatura.vaga_id
        for candidatura in db.query(CandidaturaModel.vaga_id).filter(CandidaturaModel.candidato_id == current_user.id).all()
    }
    recomendacoes = []
    for vaga in use_case.listar_vagas_abertas():
        if vaga.id in vagas_candidatadas:
            continue
        score, motivos = recomendar_vaga(vaga, current_user.competencias, current_user.experiencia, current_user.localizacao)
        recomendacoes.append(VagaRecomendadaResponse(**vaga.model_dump(), match_score=score, motivos=motivos))
    return sorted(recomendacoes, key=lambda vaga: (-vaga.match_score, vaga.id or 0))[:limite]

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
