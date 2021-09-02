"""Made dataset name longer

Revision ID: a664c3c6907c
Revises: 2de7150f9351
Create Date: 2021-09-02 20:14:47.062777

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a664c3c6907c'
down_revision = '2de7150f9351'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('dataset', 'dataset_name',
               existing_type=mysql.VARCHAR(length=64),
               type_=sa.String(length=512),
               existing_nullable=True)
    op.alter_column('session', 'session_object',
               existing_type=mysql.LONGTEXT(),
               type_=sa.Text(length=1000000000),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'session_object',
               existing_type=sa.Text(length=1000000000),
               type_=mysql.LONGTEXT(),
               existing_nullable=True)
    op.alter_column('dataset', 'dataset_name',
               existing_type=sa.String(length=512),
               type_=mysql.VARCHAR(length=64),
               existing_nullable=True)
    # ### end Alembic commands ###
