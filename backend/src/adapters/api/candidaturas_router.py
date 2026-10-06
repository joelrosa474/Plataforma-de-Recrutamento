import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, File, Form, UploadFile, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.domain.entities.candidatura import Candidatura
from src.application.use_cases.realizar_candidatura import RealizarCandidaturaUseCase
from src.infrastructure.repositories.candidatura_repository_sqlalchemy import CandidaturaRepositorySQLAlchemy
from src.infrastructure.repositories.vaga_repository_sqlalchemy import VagaRepositorySQLAlchemy
from src.infrastructure.ai.gemini_screener_adapter import GeminiScreenerAdapter
from src.application.services.pdf_service import PDFService
from src.application.services.storage_service import StorageService
from src.infrastructure.database.config import get_db, SessionLocal
from src.infrastructure.database.models import VagaModel, CandidaturaModel, UsuarioModel
from src.adapters.api.notificacoes_router import criar_notificacao
from src.adapters.api.dependencies import get_current_user, get_current_candidato, get_current_empresa

logger = logging.getLogger("rh_api")
router = APIRouter(prefix="/api/candidaturas", tags=["Candidaturas"])

storage_service = StorageService()
ai_screener = GeminiScreenerAdapter()


def get_candidaturas_use_case(db: Session = Depends(get_db)):
    candidatura_repo = CandidaturaRepositorySQLAlchemy(db)
    vaga_repo = VagaRepositorySQLAlchemy(db)
    return RealizarCandidaturaUseCase(candidatura_repo=candidatura_repo, vaga_repo=vaga_repo, ai_screener=ai_screener)


def executar_triagem_ia_background(candidatura_id: int, curriculo_texto: str, vaga_id: int, candidato_id: int):
    """Worker em background para executar a IA sem bloquear o candidato."""
    db = SessionLocal()
    try:
        candidatura_repo = CandidaturaRepositorySQLAlchemy(db)
        vaga_repo = VagaRepositorySQLAlchemy(db)
        use_case = RealizarCandidaturaUseCase(candidatura_repo=candidatura_repo, vaga_repo=vaga_repo, ai_screener=ai_screener)

        candidatura = use_case.processar_triagem_ia(candidatura_id=candidatura_id, curriculo_texto=curriculo_texto)
        if candidatura:
            db.commit()
            vaga = vaga_repo.buscar_por_id(vaga_id)
            if vaga:
                score_msg = f"{candidatura.match_score:.0f}%" if candidatura.match_score is not None else "N/A"
                criar_notificacao(
                    db,
                    vaga.empresa_id,
                    "Triagem de IA Concluída",
                    f"A IA concluiu a análise de uma candidatura para a vaga '{vaga.titulo}'. Match: {score_msg} (Fase atual: {candidatura.fase_atual})."
                )
                db.commit()

            if candidatura.fase_atual == "Entrevista":
                criar_notificacao(
                    db,
                    candidato_id,
                    "Parabéns! Sua candidatura avançou",
                    "Seu currículo obteve alta aderência aos requisitos e você foi selecionado para a fase de Entrevista!"
                )
                db.commit()
    except Exception as e:
        logger.error(f"Falha na execução em background da triagem de IA para candidatura {candidatura_id}: {e}")
        db.rollback()
    finally:
        db.close()


class CandidatoResumo(BaseModel):
    id: int
    nome: str
    email: str
    localizacao: Optional[str] = None
    competencias: List[str] = []
    experiencia: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class CandidaturaDetalhadaResponse(BaseModel):
    id: int
    vaga_id: int
    candidato_id: int
    fase_atual: str
    match_score: Optional[float] = None
    curriculo_nome: Optional[str] = None
    tem_curriculo: bool = False
    data_aplicacao: datetime
    candidato: Optional[CandidatoResumo] = None


@router.post("/", response_model=Candidatura)
async def aplicar_para_vaga(
    background_tasks: BackgroundTasks,
    vaga_id: int = Form(...),
    curriculo_pdf: UploadFile = File(...),
    current_user = Depends(get_current_candidato),
    use_case: RealizarCandidaturaUseCase = Depends(get_candidaturas_use_case)
):
    try:
        file_bytes = await curriculo_pdf.read()
        PDFService.validate_pdf_file(curriculo_pdf.filename or "", curriculo_pdf.content_type or "", file_bytes)
        curriculo_texto = PDFService.extract_text_from_pdf(file_bytes)

        # Salva o arquivo de forma segura através do StorageService
        saved_path, clean_name = storage_service.salvar_curriculo(
            file_bytes=file_bytes,
            original_filename=curriculo_pdf.filename or "curriculo.pdf",
            vaga_id=vaga_id,
            candidato_id=current_user.id
        )

        # Salva candidatura imediatamente sem aguardar o tempo de resposta da IA
        candidatura = use_case.aplicar_para_vaga(
            vaga_id=vaga_id,
            candidato_id=current_user.id,
            curriculo_texto=curriculo_texto,
            curriculo_path=saved_path,
            curriculo_nome=clean_name,
            processar_ia=False  # IA será processada em background
        )

        # Dispara a análise inteligente com Gemini em segundo plano
        background_tasks.add_task(
            executar_triagem_ia_background,
            candidatura.id,
            curriculo_texto,
            vaga_id,
            current_user.id
        )

        # Notifica imediatamente a empresa
        vaga = use_case.vaga_repo.buscar_por_id(vaga_id)
        if vaga and vaga.empresa_id:
            db = use_case.candidatura_repo.db
            criar_notificacao(db, vaga.empresa_id, "Nova candidatura recebida", f"{current_user.nome} candidatou-se à vaga {vaga.titulo}.")
            db.commit()

        return candidatura
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erro ao aplicar para vaga")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a candidatura: {str(e)}")


@router.get("/vaga/{vaga_id}", response_model=List[CandidaturaDetalhadaResponse])
def listar_candidatos_da_vaga(
    vaga_id: int,
    current_user = Depends(get_current_empresa),
    db: Session = Depends(get_db),
    use_case: RealizarCandidaturaUseCase = Depends(get_candidaturas_use_case)
):
    vaga = use_case.vaga_repo.buscar_por_id(vaga_id)
    if not vaga or vaga.empresa_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    candidaturas_model = db.query(CandidaturaModel).filter(CandidaturaModel.vaga_id == vaga_id).order_by(CandidaturaModel.id.desc()).all()

    # Otimização contra problema N+1: busca todos os candidatos em uma única query
    candidato_ids = list({c.candidato_id for c in candidaturas_model})
    usuarios_map = {}
    if candidato_ids:
        usuarios = db.query(UsuarioModel).filter(UsuarioModel.id.in_(candidato_ids)).all()
        usuarios_map = {u.id: u for u in usuarios}

    resultado: List[CandidaturaDetalhadaResponse] = []
    for c in candidaturas_model:
        user = usuarios_map.get(c.candidato_id)
        candidato_resumo = None
        if user:
            candidato_resumo = CandidatoResumo(
                id=user.id,
                nome=user.nome,
                email=user.email,
                localizacao=user.localizacao,
                competencias=user.get_competencias_list(),
                experiencia=user.experiencia,
                linkedin_url=user.linkedin_url,
                github_url=user.github_url
            )

        tem_curriculo = storage_service.arquivo_existe(c.curriculo_path)
        resultado.append(CandidaturaDetalhadaResponse(
            id=c.id,
            vaga_id=c.vaga_id,
            candidato_id=c.candidato_id,
            fase_atual=c.fase_atual,
            match_score=c.match_score,
            curriculo_nome=c.curriculo_nome,
            tem_curriculo=tem_curriculo,
            data_aplicacao=c.data_aplicacao,
            candidato=candidato_resumo
        ))

    return resultado


@router.get("/minhas", response_model=List[Candidatura])
def listar_minhas_candidaturas(current_user = Depends(get_current_candidato), use_case: RealizarCandidaturaUseCase = Depends(get_candidaturas_use_case)):
    return use_case.listar_candidaturas_do_candidato(current_user.id)


@router.get("/{candidatura_id}/curriculo")
def descarregar_curriculo(
    candidatura_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    candidatura = db.query(CandidaturaModel).filter(CandidaturaModel.id == candidatura_id).first()
    if not candidatura:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")

    vaga = db.query(VagaModel).filter(VagaModel.id == candidatura.vaga_id).first()

    # Validação de autorização: Candidato que se candidatou, Empresa dona da vaga ou Admin
    eh_candidato = (current_user.id == candidatura.candidato_id)
    eh_empresa_dona = (vaga and vaga.empresa_id == current_user.id)
    eh_admin = (current_user.tipo_perfil == "Administrador")

    if not (eh_candidato or eh_empresa_dona or eh_admin):
        raise HTTPException(status_code=403, detail="Não tem permissão para descarregar este currículo.")

    if not storage_service.arquivo_existe(candidatura.curriculo_path):
        raise HTTPException(status_code=404, detail="O ficheiro do currículo não se encontra disponível no servidor.")

    nome_ficheiro = candidatura.curriculo_nome or "curriculo.pdf"
    return FileResponse(
        path=candidatura.curriculo_path,
        filename=nome_ficheiro,
        media_type="application/pdf"
    )


class AtualizarFaseRequest(BaseModel):
    fase_atual: str


@router.put("/{candidatura_id}/fase", response_model=Candidatura)
def atualizar_fase(candidatura_id: int, request: AtualizarFaseRequest, current_user = Depends(get_current_empresa), use_case: RealizarCandidaturaUseCase = Depends(get_candidaturas_use_case)):
    candidatura = use_case.candidatura_repo.buscar_por_id(candidatura_id)
    vaga = use_case.vaga_repo.buscar_por_id(candidatura.vaga_id) if candidatura else None
    if not vaga or vaga.empresa_id != current_user.id:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    if request.fase_atual not in {"Triagem", "Entrevista", "Contratado", "Reprovado"}:
        raise HTTPException(status_code=400, detail="Fase inválida")
    atualizada = use_case.atualizar_fase(candidatura_id, request.fase_atual)
    if atualizada:
        db = use_case.candidatura_repo.db
        criar_notificacao(db, atualizada.candidato_id, "Atualização de candidatura", f"A sua candidatura avançou para: {request.fase_atual}.")
        db.commit()
    return atualizada
