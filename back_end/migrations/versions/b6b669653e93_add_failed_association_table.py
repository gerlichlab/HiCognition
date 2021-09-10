"""add failed association table

Revision ID: b6b669653e93
Revises: 99a8595a8557
Create Date: 2021-09-10 10:58:49.065153

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6b669653e93'
down_revision = '99a8595a8557'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset_failed_table',
    sa.Column('dataset_region', sa.Integer(), nullable=True),
    sa.Column('dataset_feature', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_feature'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['dataset_region'], ['dataset.id'], )
    )
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
    op.drop_table('dataset_failed_table')
    # ### end Alembic commands ###
