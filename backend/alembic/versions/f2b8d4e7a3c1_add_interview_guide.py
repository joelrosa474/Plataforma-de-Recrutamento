"""add interview guide

Revision ID: f2b8d4e7a3c1
Revises: e7a3c9d6f1b2
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f2b8d4e7a3c1"
down_revision: Union[str, None] = "e7a3c9d6f1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    if "roteiro_entrevista" not in columns:
        op.add_column("candidaturas", sa.Column("roteiro_entrevista", sa.Text(), nullable=True))

def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    if "roteiro_entrevista" in columns:
        op.drop_column("candidaturas", "roteiro_entrevista")
