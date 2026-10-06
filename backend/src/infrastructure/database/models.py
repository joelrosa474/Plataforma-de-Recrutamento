import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from src.infrastructure.database.config import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    tipo_perfil = Column(String)
    localizacao = Column(String, nullable=True)
    experiencia = Column(Text, nullable=True)
    competencias = Column(Text, default="[]")
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)

    def get_competencias_list(self):
        try:
            return json.loads(self.competencias or "[]")
        except Exception:
            return []

    def set_competencias_list(self, competencias):
        self.competencias = json.dumps(competencias)

class VagaModel(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    titulo = Column(String, index=True)
    descricao = Column(Text)
    requisitos = Column(Text) # Guardamos como string JSON para simplificar
    status = Column(String, default="Aberta")
    localizacao = Column(String, nullable=True)
    modalidade = Column(String, nullable=True)
    area = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def get_requisitos_list(self):
        try:
            return json.loads(self.requisitos)
        except:
            return []

    def set_requisitos_list(self, req_list):
        self.requisitos = json.dumps(req_list)

class CandidaturaModel(Base):
    __tablename__ = "candidaturas"
    __table_args__ = (UniqueConstraint("vaga_id", "candidato_id", name="uq_candidatura_vaga_candidato"),)

    id = Column(Integer, primary_key=True, index=True)
    vaga_id = Column(Integer, ForeignKey("vagas.id"))
    candidato_id = Column(Integer, ForeignKey("usuarios.id"))
    fase_atual = Column(String, default="Triagem")
    match_score = Column(Float, nullable=True)
    feedback_ia = Column(Text, nullable=True)
    curriculo_path = Column(String, nullable=True)
    curriculo_nome = Column(String, nullable=True)
    data_aplicacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class NotificacaoModel(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=False)
    titulo = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    lida = Column(Integer, default=0, nullable=False)
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
