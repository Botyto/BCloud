"""initial

Revision ID: 3ef4cd7b6f55
Revises: 
Create Date: 2023-09-23 21:59:55.372408

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3ef4cd7b6f55'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('JobPromise',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('issuer', sa.String(length=64), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('valid_for', sa.Interval(), nullable=False),
    sa.Column('completed_at_utc', sa.DateTime(), nullable=True),
    sa.Column('error', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('MiniappEnable',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('MiniappVersion',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('password', mysql.LONGBLOB(length=4294967295), nullable=False),
    sa.Column('role', sa.Enum('NEW', 'USER', 'ADMIN', name='userrole'), nullable=False),
    sa.Column('display_name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('Activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('issuer', sa.String(length=64), nullable=False),
    sa.Column('type', sa.String(length=512), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Login',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at_utc', sa.DateTime(), nullable=False),
    sa.Column('expire_at_utc', sa.DateTime(), nullable=False),
    sa.Column('last_used_utc', sa.DateTime(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('Login')
    op.drop_table('Activity')
    op.drop_table('User')
    op.drop_table('MiniappVersion')
    op.drop_table('MiniappEnable')
    op.drop_table('JobPromise')
