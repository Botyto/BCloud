"""notes

Revision ID: cddd57819c72
Revises: ee4f269d4d73
Create Date: 2023-11-25 15:05:19.110820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cddd57819c72'
down_revision = 'ee4f269d4d73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('NotesCollection',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('slug', sa.String(length=41), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('view', sa.Enum('NOTES', 'BOOKMARKS', 'CHAT', name='notescollectionview'), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.Column('access', sa.Enum('SERVICE', 'HIDDEN', 'SECURE', 'PRIVATE', 'PUBLIC_READABLE', 'PUBLIC_WRITABLE', name='accesslevel'), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['NotesCollection.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('NotesNote',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('collection_id', sa.UUID(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('slug', sa.String(length=41), nullable=False),
    sa.Column('sort_key', sa.Float(), nullable=False),
    sa.Column('title', sa.String(length=4096), nullable=False),
    sa.Column('content', sa.String(length=4095), nullable=False),
    sa.Column('favorite', sa.Boolean(), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.Column('color', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['collection_id'], ['NotesCollection.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('NotesFile',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('note_id', sa.UUID(), nullable=False),
    sa.Column('kind', sa.Enum('ATTACHMENT', 'PREVIEW', 'CACHE', name='notesfilekind'), nullable=False),
    sa.Column('file_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['FileMetadata.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['note_id'], ['NotesNote.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('NotesTag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('note_id', sa.UUID(), nullable=False),
    sa.Column('tag', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['note_id'], ['NotesNote.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('NotesTag')
    op.drop_table('NotesFile')
    op.drop_table('NotesNote')
    op.drop_table('NotesCollection')
    # ### end Alembic commands ###
