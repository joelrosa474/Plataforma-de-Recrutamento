from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.adapters.api.dependencies import get_current_user
from src.infrastructure.database.config import get_db
from src.infrastructure.database.models import NotificacaoModel

router = APIRouter(prefix="/api/notificacoes", tags=["Notificações"])

class NotificacaoResponse(BaseModel):
    id: int
    titulo: str
    mensagem: str
    lida: bool
    data_criacao: datetime

def criar_notificacao(db: Session, usuario_id: int, titulo: str, mensagem: str) -> None:
    db.add(NotificacaoModel(usuario_id=usuario_id, titulo=titulo, mensagem=mensagem))

def serializar(item: NotificacaoModel) -> dict:
    return {"id": item.id, "titulo": item.titulo, "mensagem": item.mensagem, "lida": bool(item.lida), "data_criacao": item.data_criacao}

@router.get("/", response_model=list[NotificacaoResponse])
def listar_notificacoes(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(NotificacaoModel).filter(NotificacaoModel.usuario_id == current_user.id).order_by(NotificacaoModel.data_criacao.desc()).limit(50).all()
    return [serializar(item) for item in items]

@router.put("/{notificacao_id}/lida", response_model=NotificacaoResponse)
def marcar_como_lida(notificacao_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(NotificacaoModel).filter(NotificacaoModel.id == notificacao_id, NotificacaoModel.usuario_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    item.lida = 1
    db.commit()
    db.refresh(item)
    return serializar(item)

@router.put("/ler-todas", status_code=204)
def marcar_todas_como_lidas(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(NotificacaoModel).filter(NotificacaoModel.usuario_id == current_user.id, NotificacaoModel.lida == 0).update({NotificacaoModel.lida: 1})
    db.commit()
