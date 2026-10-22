import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Garante que o diretório raiz do backend esteja no sys.path
sys.path.insert(0, os.path.abspath("."))

# Carrega variáveis do .env
load_dotenv()

# Alembic Config
config = context.config

# Configuração de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Configura dinamicamente a URL da base de dados a partir do ambiente (.env)
database_url = os.getenv("DATABASE_URL", "sqlite:///./recrutamento.db")
# Alembic precisa de % escapado em senhas ou strings se aplicável
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Importação dos modelos para suportar --autogenerate
from src.infrastructure.database.config import Base
import src.infrastructure.database.models  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline' sem precisar de conexão ativa."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True if url.startswith("sqlite") else False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo 'online' associando um Engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    is_sqlite = str(connectable.url).startswith("sqlite")

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,  # render_as_batch é essencial para SQLite suportar ALTER TABLE
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
