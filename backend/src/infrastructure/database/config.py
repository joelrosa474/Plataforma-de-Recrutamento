import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# A URL pode vir do .env. Se não existir, usamos o SQLite por defeito.
# Exemplo PostgreSQL: "postgresql://usuario:senha@localhost:5432/recrutamento"
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./recrutamento.db")

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Configurações de Connection Pooling para PostgreSQL / MySQL em Produção
    engine_kwargs["pool_size"] = int(os.environ.get("DB_POOL_SIZE", "10"))
    engine_kwargs["max_overflow"] = int(os.environ.get("DB_MAX_OVERFLOW", "20"))
    engine_kwargs["pool_recycle"] = int(os.environ.get("DB_POOL_RECYCLE", "1800"))

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def check_db_health() -> bool:
    """Verifica conectividade ativa com a base de dados."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def migrate_sqlite_schema():
    """Fallback para adicionar colunas em SQLite de desenvolvimento se necessário."""
    if not is_sqlite:
        return
    existing = {column["name"] for column in inspect(engine).get_columns("vagas")}
    with engine.begin() as connection:
        if "empresa_id" not in existing:
            connection.execute(text("ALTER TABLE vagas ADD COLUMN empresa_id INTEGER"))
        if "data_criacao" not in existing:
            connection.execute(text("ALTER TABLE vagas ADD COLUMN data_criacao DATETIME"))
        for name in ("localizacao", "modalidade", "area"):
            if name not in existing:
                connection.execute(text(f"ALTER TABLE vagas ADD COLUMN {name} TEXT"))
    users = {column["name"] for column in inspect(engine).get_columns("usuarios")}
    user_columns = {
        "localizacao": "TEXT",
        "experiencia": "TEXT",
        "competencias": "TEXT DEFAULT '[]'",
        "linkedin_url": "TEXT",
        "github_url": "TEXT",
    }
    with engine.begin() as connection:
        for name, definition in user_columns.items():
            if name not in users:
                connection.execute(text(f"ALTER TABLE usuarios ADD COLUMN {name} {definition}"))

    cand_columns = {column["name"] for column in inspect(engine).get_columns("candidaturas")}
    with engine.begin() as connection:
        if "curriculo_path" not in cand_columns:
            connection.execute(text("ALTER TABLE candidaturas ADD COLUMN curriculo_path TEXT"))
        if "curriculo_nome" not in cand_columns:
            connection.execute(text("ALTER TABLE candidaturas ADD COLUMN curriculo_nome TEXT"))


# Dependência do FastAPI para injetar a sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
