"""create subscription table

Revision ID: d12aff692425
Revises: 6c08ed896611
Create Date: 2022-02-25 21:56:13.050550

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "d12aff692425"
down_revision = "6c08ed896611"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.String),
        sa.Column("active", sa.Boolean),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )

    op.create_table(
        "user_subscriptions",
        sa.Column("user_id", sa.Integer, sa.ForeignKey(("users.id"))),
        sa.Column("subscription_id", sa.Integer, sa.ForeignKey("subscriptions.id")),
    )


def downgrade():
    op.drop_table("subscriptions")
    op.drop_table("user_subscriptions")
