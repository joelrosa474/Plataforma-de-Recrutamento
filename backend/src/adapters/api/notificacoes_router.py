import asyncio
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.adapters.api.dependencies import get_current_user
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import NotificacaoModel
from src.infrastructure.security.jwt_service import JWTService
from src.infrastructure.notifications.broadcaster import notification_broadcaster

router = APIRouter(prefix="/api/notificacoes", tags=["Notificações"])


class NotificacaoResponse(BaseModel):
    id: int
    titulo: str
    mensagem: str
    lida: bool
    data_criacao: datetime


def serializar(item: NotificacaoModel) -> dict:
    return {
        "id": item.id,
        "titulo": item.titulo,
        "mensagem": item.mensagem,
        "lida": bool(item.lida),
        "data_criacao": item.data_criacao.isoformat() if hasattr(item.data_criacao, "isoformat") else str(item.data_criacao),
    }


def criar_notificacao(db: Session, usuario_id: int, titulo: str, mensagem: str) -> NotificacaoModel:
    """Cria e persiste uma notificação no banco e despacha evento SSE em tempo real se o usuário estiver conectado."""
    item = NotificacaoModel(usuario_id=usuario_id, titulo=titulo, mensagem=mensagem)
    db.add(item)
    db.flush()

    # Transmite em tempo real para os clientes conectados via SSE
    payload = serializar(item)
    notification_broadcaster.broadcast(usuario_id, payload)
    return item


@router.get("/", response_model=list[NotificacaoResponse])
def listar_notificacoes(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(NotificacaoModel)
        .filter(NotificacaoModel.usuario_id == current_user.id)
        .order_by(NotificacaoModel.data_criacao.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": item.id,
            "titulo": item.titulo,
            "mensagem": item.mensagem,
            "lida": bool(item.lida),
            "data_criacao": item.data_criacao
        }
        for item in items
    ]


@router.get("/stream")
async def stream_notificacoes(
    request: Request,
    token: Optional[str] = None
):
    """
    Endpoint SSE (Server-Sent Events) para entrega de notificações em tempo real.
    Autenticação suportada via:
    1. Query param: `?token=<JWT>` (padrão para EventSource do navegador)
    2. Header: `Authorization: Bearer <JWT>`
    3. Cookie: `rh_access_token`
    """
    auth_token = token
    if not auth_token:
        cookie_token = request.cookies.get("rh_access_token")
        if cookie_token:
            auth_token = cookie_token
        else:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                auth_token = auth_header.split(" ", 1)[1]

    if not auth_token:
        raise HTTPException(status_code=401, detail="Token de autenticação não fornecido.")

    try:
        payload = JWTService.decodificar_token(auth_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    async def event_generator():
        queue = notification_broadcaster.subscribe(user_id)
        try:
            # Evento inicial confirmando conexão SSE estabelecida
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'user_id': user_id})}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"event: notification\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat ping a cada 20 segundos para manter proxies e Cloudflare ativos
                    yield ": ping\n\n"
        finally:
            notification_broadcaster.unsubscribe(user_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.put("/{notificacao_id}/lida", response_model=NotificacaoResponse)
def marcar_como_lida(notificacao_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    item = (
        db.query(NotificacaoModel)
        .filter(NotificacaoModel.id == notificacao_id, NotificacaoModel.usuario_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    item.lida = 1
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "titulo": item.titulo,
        "mensagem": item.mensagem,
        "lida": bool(item.lida),
        "data_criacao": item.data_criacao
    }


@router.put("/ler-todas", status_code=204)
def marcar_todas_como_lidas(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(NotificacaoModel).filter(
        NotificacaoModel.usuario_id == current_user.id,
        NotificacaoModel.lida == 0
    ).update({NotificacaoModel.lida: 1})
    db.commit()
