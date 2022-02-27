"""add channel id to subscriptions

Revision ID: 376131864b2f
Revises: d12aff692425
Create Date: 2022-02-26 01:14:27.767430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "376131864b2f"
down_revision = "d12aff692425"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("subscriptions", sa.Column("channel_id", sa.String))


def downgrade():
    op.drop_column("subscriptions", "channel_id")
