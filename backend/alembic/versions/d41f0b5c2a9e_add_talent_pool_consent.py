"""add talent pool consent

Revision ID: d41f0b5c2a9e
Revises: 8bd2a6cf1e8a
Create Date: 2026-10-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d41f0b5c2a9e"
down_revision: Union[str, None] = "8bd2a6cf1e8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("usuarios")}
    if "perfil_publico_talentos" not in columns:
        op.add_column("usuarios", sa.Column("perfil_publico_talentos", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("usuarios")}
    if "perfil_publico_talentos" in columns:
        op.drop_column("usuarios", "perfil_publico_talentos")
