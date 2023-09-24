"""files

Revision ID: 5ffddb78c47e
Revises: 3ef4cd7b6f55
Create Date: 2023-09-24 14:07:45.295123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ffddb78c47e'
down_revision = '3ef4cd7b6f55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('FileStorage',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('FileMetadata',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('mime_type', sa.String(length=127), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.UUID(), nullable=False),
    sa.Column('storage_id', sa.UUID(), nullable=False),
    sa.Column('root_storage_id', sa.UUID(), nullable=True),
    sa.Column('atime_utc', sa.DateTime(), nullable=False),
    sa.Column('mtime_utc', sa.DateTime(), nullable=False),
    sa.Column('ctime_utc', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['FileMetadata.id'], ),
    sa.ForeignKeyConstraint(['root_storage_id'], ['FileStorage.id'], ),
    sa.ForeignKeyConstraint(['storage_id'], ['FileStorage.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('FileMetadata')
    op.drop_table('FileStorage')
    # ### end Alembic commands ###
