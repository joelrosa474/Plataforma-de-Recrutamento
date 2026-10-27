"""add explainable match analysis

Revision ID: 8bd2a6cf1e8a
Revises: 4e2d4fe0aa0c
Create Date: 2026-10-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8bd2a6cf1e8a"
down_revision: Union[str, None] = "4e2d4fe0aa0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Em SQLite de desenvolvimento, o fallback da aplicação pode ter criado
    # esta coluna antes de o Alembic registar a revisão.
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    if "analise_match_ia" not in columns:
        op.add_column("candidaturas", sa.Column("analise_match_ia", sa.Text(), nullable=True))


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    if "analise_match_ia" in columns:
        op.drop_column("candidaturas", "analise_match_ia")
