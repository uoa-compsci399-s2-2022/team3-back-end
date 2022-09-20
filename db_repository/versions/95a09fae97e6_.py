"""empty message

Revision ID: 95a09fae97e6
Revises: 
Create Date: 2022-09-21 02:58:22.362999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95a09fae97e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'Test',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
    )


def downgrade() -> None:
    pass
