"""add discord id column to user table

Revision ID: bf83f1d34764
Revises: 376131864b2f
Create Date: 2022-02-26 20:56:43.809513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bf83f1d34764"
down_revision = "376131864b2f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("discord_id", sa.String))


def downgrade():
    op.drop_column("users", "discord_id")
