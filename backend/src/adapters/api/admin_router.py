from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.adapters.api.dependencies import get_current_admin
from src.adapters.api.auth_router import UsuarioResponse
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import UsuarioModel, VagaModel, CandidaturaModel, NotificacaoModel
from src.infrastructure.repositories.usuario_repository_sqlalchemy import UsuarioRepositorySQLAlchemy
from src.infrastructure.repositories.vaga_repository_sqlalchemy import VagaRepositorySQLAlchemy

router = APIRouter(prefix="/api/admin", tags=["Administração"])


class MetricItem(BaseModel):
    label: str
    total: int


class ResumoAdmin(BaseModel):
    usuarios: int
    empresas: int
    candidatos: int
    vagas: int
    candidaturas: int
    # Métricas de IA (Gemini Screener)
    triagens_ia_total: int = 0
    media_match_score: float = 0.0
    taxa_triagem_ia: float = 0.0
    compatibilidade_alta: int = 0
    compatibilidade_media: int = 0
    compatibilidade_baixa: int = 0
    # Distribuição de vagas
    vagas_abertas: int = 0
    vagas_pausadas: int = 0
    vagas_fechadas: int = 0
    vagas_por_modalidade: list[MetricItem] = []
    top_areas: list[MetricItem] = []
    # Candidaturas por fase
    candidaturas_por_fase: list[MetricItem] = []
    # Atividade recente (7 dias)
    novas_vagas_7d: int = 0
    novas_candidaturas_7d: int = 0


class AtualizarStatusVagaRequest(BaseModel):
    status: str


class AtualizarPerfilUsuarioRequest(BaseModel):
    tipo_perfil: str


class AdminVagaResponse(BaseModel):
    id: int
    empresa_id: Optional[int] = None
    empresa_nome: Optional[str] = None
    empresa_email: Optional[str] = None
    titulo: str
    descricao: str
    status: str
    requisitos: list[str] = []
    localizacao: Optional[str] = None
    modalidade: Optional[str] = None
    area: Optional[str] = None
    data_criacao: Optional[datetime] = None
    total_candidaturas: int = 0


@router.get("/resumo", response_model=ResumoAdmin)
def resumo(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    sete_dias_atras = datetime.now(timezone.utc) - timedelta(days=7)

    # Contagens gerais
    total_usuarios = db.query(UsuarioModel).count()
    total_empresas = db.query(UsuarioModel).filter(UsuarioModel.tipo_perfil == "Empresa").count()
    total_candidatos = db.query(UsuarioModel).filter(UsuarioModel.tipo_perfil == "Candidato").count()
    total_vagas = db.query(VagaModel).count()
    total_candidaturas = db.query(CandidaturaModel).count()

    # Métricas da IA (Gemini Screener)
    candidaturas_com_score = db.query(CandidaturaModel).filter(CandidaturaModel.match_score.isnot(None)).all()
    triagens_ia_total = len(candidaturas_com_score)
    media_match_score = (
        round(sum(c.match_score for c in candidaturas_com_score) / triagens_ia_total, 1)
        if triagens_ia_total > 0
        else 0.0
    )
    taxa_triagem_ia = (
        round((triagens_ia_total / total_candidaturas * 100), 1)
        if total_candidaturas > 0
        else 0.0
    )

    comp_alta = sum(1 for c in candidaturas_com_score if (c.match_score or 0) >= 70)
    comp_media = sum(1 for c in candidaturas_com_score if 40 <= (c.match_score or 0) < 70)
    comp_baixa = sum(1 for c in candidaturas_com_score if (c.match_score or 0) < 40)

    # Distribuição de Vagas por status
    vagas_abertas = db.query(VagaModel).filter(VagaModel.status == "Aberta").count()
    vagas_pausadas = db.query(VagaModel).filter(VagaModel.status == "Pausada").count()
    vagas_fechadas = db.query(VagaModel).filter(VagaModel.status == "Fechada").count()

    # Distribuição por Modalidade
    mod_results = (
        db.query(VagaModel.modalidade, func.count(VagaModel.id))
        .filter(VagaModel.modalidade.isnot(None))
        .group_by(VagaModel.modalidade)
        .all()
    )
    vagas_por_modalidade = [
        MetricItem(label=m or "Não especificado", total=count)
        for m, count in mod_results if count > 0
    ]

    # Top Áreas Profissionais
    area_results = (
        db.query(VagaModel.area, func.count(VagaModel.id))
        .filter(VagaModel.area.isnot(None))
        .group_by(VagaModel.area)
        .order_by(func.count(VagaModel.id).desc())
        .limit(5)
        .all()
    )
    top_areas = [
        MetricItem(label=a or "Geral", total=count)
        for a, count in area_results if count > 0
    ]

    # Candidaturas por Fase do ATS
    fase_results = (
        db.query(CandidaturaModel.fase_atual, func.count(CandidaturaModel.id))
        .group_by(CandidaturaModel.fase_atual)
        .all()
    )
    candidaturas_por_fase = [
        MetricItem(label=f or "Triagem", total=count)
        for f, count in fase_results if count > 0
    ]

    # Atividade nos últimos 7 dias
    novas_vagas_7d = db.query(VagaModel).filter(VagaModel.data_criacao >= sete_dias_atras).count()
    novas_candidaturas_7d = db.query(CandidaturaModel).filter(CandidaturaModel.data_aplicacao >= sete_dias_atras).count()

    return {
        "usuarios": total_usuarios,
        "empresas": total_empresas,
        "candidatos": total_candidatos,
        "vagas": total_vagas,
        "candidaturas": total_candidaturas,
        "triagens_ia_total": triagens_ia_total,
        "media_match_score": media_match_score,
        "taxa_triagem_ia": taxa_triagem_ia,
        "compatibilidade_alta": comp_alta,
        "compatibilidade_media": comp_media,
        "compatibilidade_baixa": comp_baixa,
        "vagas_abertas": vagas_abertas,
        "vagas_pausadas": vagas_pausadas,
        "vagas_fechadas": vagas_fechadas,
        "vagas_por_modalidade": vagas_por_modalidade,
        "top_areas": top_areas,
        "candidaturas_por_fase": candidaturas_por_fase,
        "novas_vagas_7d": novas_vagas_7d,
        "novas_candidaturas_7d": novas_candidaturas_7d,
    }


@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    repo = UsuarioRepositorySQLAlchemy(db)
    return [repo._to_entity(item) for item in db.query(UsuarioModel).order_by(UsuarioModel.id.desc()).all()]


@router.put("/usuarios/{usuario_id}/perfil", response_model=UsuarioResponse)
def atualizar_perfil_usuario(
    usuario_id: int,
    request: AtualizarPerfilUsuarioRequest,
    current_admin: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if request.tipo_perfil not in {"Candidato", "Empresa", "Administrador"}:
        raise HTTPException(status_code=400, detail="Tipo de perfil inválido.")
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
    usuario.tipo_perfil = request.tipo_perfil
    db.commit()
    db.refresh(usuario)
    return UsuarioRepositorySQLAlchemy(db)._to_entity(usuario)


@router.delete("/usuarios/{usuario_id}", status_code=204)
def deletar_usuario(
    usuario_id: int,
    current_admin: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    admin_id = getattr(current_admin, "id", None)
    if admin_id and admin_id == usuario_id:
        raise HTTPException(status_code=400, detail="Não é permitido excluir a própria conta de administrador.")
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")

    # Remove notificações e candidaturas do usuário
    db.query(NotificacaoModel).filter(NotificacaoModel.usuario_id == usuario_id).delete()
    db.query(CandidaturaModel).filter(CandidaturaModel.candidato_id == usuario_id).delete()

    # Se for empresa, remove as candidaturas e vagas da empresa
    vagas_da_empresa = db.query(VagaModel.id).filter(VagaModel.empresa_id == usuario_id).all()
    vaga_ids = [v[0] for v in vagas_da_empresa]
    if vaga_ids:
        db.query(CandidaturaModel).filter(CandidaturaModel.vaga_id.in_(vaga_ids)).delete(synchronize_session=False)
        db.query(VagaModel).filter(VagaModel.empresa_id == usuario_id).delete(synchronize_session=False)

    db.delete(usuario)
    db.commit()


@router.get("/vagas", response_model=list[AdminVagaResponse])
def listar_vagas(_: object = Depends(get_current_admin), db: Session = Depends(get_db)):
    results = (
        db.query(
            VagaModel,
            UsuarioModel.nome.label("empresa_nome"),
            UsuarioModel.email.label("empresa_email"),
            func.count(CandidaturaModel.id).label("total_candidaturas"),
        )
        .outerjoin(UsuarioModel, VagaModel.empresa_id == UsuarioModel.id)
        .outerjoin(CandidaturaModel, VagaModel.id == CandidaturaModel.vaga_id)
        .group_by(VagaModel.id, UsuarioModel.nome, UsuarioModel.email)
        .order_by(VagaModel.id.desc())
        .all()
    )

    items = []
    for vaga, emp_nome, emp_email, total_cand in results:
        items.append(
            AdminVagaResponse(
                id=vaga.id,
                empresa_id=vaga.empresa_id,
                empresa_nome=emp_nome or (f"Empresa #{vaga.empresa_id}" if vaga.empresa_id else "Empresa não atribuída"),
                empresa_email=emp_email,
                titulo=vaga.titulo,
                descricao=vaga.descricao,
                status=vaga.status,
                requisitos=vaga.get_requisitos_list(),
                localizacao=vaga.localizacao,
                modalidade=vaga.modalidade,
                area=vaga.area,
                data_criacao=vaga.data_criacao,
                total_candidaturas=total_cand or 0,
            )
        )
    return items


@router.put("/vagas/{vaga_id}/status", response_model=AdminVagaResponse)
def atualizar_status_vaga(
    vaga_id: int,
    request: AtualizarStatusVagaRequest,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if request.status not in {"Aberta", "Pausada", "Fechada"}:
        raise HTTPException(status_code=400, detail="Estado de vaga inválido")
    vaga = db.query(VagaModel).filter(VagaModel.id == vaga_id).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    vaga.status = request.status
    db.commit()
    db.refresh(vaga)

    empresa = db.query(UsuarioModel).filter(UsuarioModel.id == vaga.empresa_id).first() if vaga.empresa_id else None
    total_cand = db.query(CandidaturaModel).filter(CandidaturaModel.vaga_id == vaga.id).count()

    return AdminVagaResponse(
        id=vaga.id,
        empresa_id=vaga.empresa_id,
        empresa_nome=empresa.nome if empresa else (f"Empresa #{vaga.empresa_id}" if vaga.empresa_id else "Empresa não atribuída"),
        empresa_email=empresa.email if empresa else None,
        titulo=vaga.titulo,
        descricao=vaga.descricao,
        status=vaga.status,
        requisitos=vaga.get_requisitos_list(),
        localizacao=vaga.localizacao,
        modalidade=vaga.modalidade,
        area=vaga.area,
        data_criacao=vaga.data_criacao,
        total_candidaturas=total_cand,
    )


@router.delete("/vagas/{vaga_id}", status_code=204)
def deletar_vaga_admin(
    vaga_id: int,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    vaga = db.query(VagaModel).filter(VagaModel.id == vaga_id).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    # Remove candidaturas atreladas à vaga antes
    db.query(CandidaturaModel).filter(CandidaturaModel.vaga_id == vaga_id).delete()
    db.delete(vaga)
    db.commit()
