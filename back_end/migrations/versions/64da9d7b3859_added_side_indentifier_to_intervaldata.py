"""added side indentifier to intervaldata

Revision ID: 64da9d7b3859
Revises: 56eee91a1c31
Create Date: 2023-01-28 15:45:58.248749

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '64da9d7b3859'
down_revision = '56eee91a1c31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('association_interval_data', sa.Column('region_side', sa.String(length=64), nullable=True))
    op.add_column('average_interval_data', sa.Column('region_side', sa.String(length=64), nullable=True))
    op.add_column('embedding_interval_data', sa.Column('region_side', sa.String(length=64), nullable=True))
    op.add_column('individual_interval_data', sa.Column('region_side', sa.String(length=64), nullable=True))
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
    op.drop_column('individual_interval_data', 'region_side')
    op.drop_column('embedding_interval_data', 'region_side')
    op.drop_column('average_interval_data', 'region_side')
    op.drop_column('association_interval_data', 'region_side')
    # ### end Alembic commands ###