"""add interview schedule

Revision ID: e7a3c9d6f1b2
Revises: d41f0b5c2a9e
Create Date: 2026-10-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7a3c9d6f1b2"
down_revision: Union[str, None] = "d41f0b5c2a9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    additions = {
        "entrevista_data": sa.Column("entrevista_data", sa.DateTime(), nullable=True),
        "entrevista_link": sa.Column("entrevista_link", sa.String(), nullable=True),
        "entrevista_notas": sa.Column("entrevista_notas", sa.Text(), nullable=True),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column("candidaturas", column)


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("candidaturas")}
    for name in ("entrevista_notas", "entrevista_link", "entrevista_data"):
        if name in columns:
            op.drop_column("candidaturas", name)
