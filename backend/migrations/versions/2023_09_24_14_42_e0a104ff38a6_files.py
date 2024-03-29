"""files

Revision ID: e0a104ff38a6
Revises: 3ef4cd7b6f55
Create Date: 2023-09-24 14:42:02.007474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0a104ff38a6'
down_revision = '3ef4cd7b6f55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('FileStorage',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('slug', sa.String(length=41), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('FileMetadata',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('mime_type', sa.String(length=127), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('storage_id', sa.UUID(), nullable=False),
    sa.Column('root_storage_id', sa.UUID(), nullable=True),
    sa.Column('atime_utc', sa.DateTime(), nullable=False),
    sa.Column('mtime_utc', sa.DateTime(), nullable=False),
    sa.Column('ctime_utc', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['FileMetadata.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['root_storage_id'], ['FileStorage.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['storage_id'], ['FileStorage.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('FileMetadata')
    op.drop_table('FileStorage')
