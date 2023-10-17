"""files-access

Revision ID: ee4f269d4d73
Revises: e0a104ff38a6
Create Date: 2023-10-17 20:09:58.542276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee4f269d4d73'
down_revision = 'e0a104ff38a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('FileMetadata', sa.Column('access', sa.Enum('SERVICE', 'HIDDEN', 'SECURE', 'PRIVATE', 'PUBLIC_READABLE', 'PUBLIC_WRITABLE', name='accesslevel'), nullable=False))
    op.execute("UPDATE FileMetadata SET access = 'PRIVATE';")


def downgrade() -> None:
    op.drop_column('FileMetadata', 'access')
