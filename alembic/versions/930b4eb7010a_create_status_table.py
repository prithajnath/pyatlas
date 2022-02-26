"""create status table

Revision ID: 930b4eb7010a
Revises: 
Create Date: 2022-02-26 02:44:24.634966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "930b4eb7010a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "statuses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("twitter_id", sa.String),
    )


def downgrade():
    op.drop_table("statuses")
