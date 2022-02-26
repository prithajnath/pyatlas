"""create user table

Revision ID: 6c08ed896611
Revises: 930b4eb7010a
Create Date: 2022-02-26 02:54:26.866987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6c08ed896611"
down_revision = "930b4eb7010a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, unique=True),
        sa.Column("username", sa.String),
    )


def downgrade():
    op.drop_table("users")
