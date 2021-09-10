"""added completed_features association

Revision ID: 35ec45407a76
Revises: b6b669653e93
Create Date: 2021-09-10 14:32:10.004544

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '35ec45407a76'
down_revision = 'b6b669653e93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset_completed_table',
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
    op.drop_table('dataset_completed_table')
    # ### end Alembic commands ###
