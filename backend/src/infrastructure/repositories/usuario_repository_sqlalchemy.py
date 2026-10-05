from typing import Optional
from sqlalchemy.orm import Session
from src.application.ports.usuario_repository import UsuarioRepository
from src.domain.entities.usuario import Usuario
from src.infrastructure.database.models import UsuarioModel

class UsuarioRepositorySQLAlchemy(UsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        db_usuario = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first() if usuario.id else None
        if db_usuario:
            db_usuario.nome = usuario.nome
            db_usuario.email = usuario.email
            db_usuario.senha_hash = usuario.senha_hash
            db_usuario.tipo_perfil = usuario.tipo_perfil
            db_usuario.localizacao = usuario.localizacao
            db_usuario.experiencia = usuario.experiencia
            db_usuario.set_competencias_list(usuario.competencias)
            db_usuario.linkedin_url = usuario.linkedin_url
            db_usuario.github_url = usuario.github_url
        else:
            db_usuario = UsuarioModel(nome=usuario.nome, email=usuario.email, senha_hash=usuario.senha_hash, tipo_perfil=usuario.tipo_perfil, localizacao=usuario.localizacao, experiencia=usuario.experiencia, linkedin_url=usuario.linkedin_url, github_url=usuario.github_url)
            db_usuario.set_competencias_list(usuario.competencias)
            self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)
        
        return self._to_entity(db_usuario)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        db_usuario = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        if db_usuario:
            return self._to_entity(db_usuario)
        return None

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        db_usuario = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if db_usuario:
            return self._to_entity(db_usuario)
        return None

    def deletar(self, usuario_id: int) -> bool:
        usuario = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if not usuario:
            return False
        self.db.delete(usuario)
        self.db.commit()
        return True
        
    def _to_entity(self, model: UsuarioModel) -> Usuario:
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            tipo_perfil=model.tipo_perfil,
            localizacao=model.localizacao,
            experiencia=model.experiencia,
            competencias=model.get_competencias_list(),
            linkedin_url=model.linkedin_url,
            github_url=model.github_url
        )
