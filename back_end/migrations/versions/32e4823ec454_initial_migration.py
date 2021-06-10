"""initial migration

Revision ID: 32e4823ec454
Revises: 
Create Date: 2021-06-10 12:05:30.287384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32e4823ec454'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('dataset',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_name', sa.String(length=64), nullable=True),
    sa.Column('genotype', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=81), nullable=True),
    sa.Column('file_path', sa.String(length=128), nullable=True),
    sa.Column('public', sa.Boolean(), nullable=True),
    sa.Column('filetype', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('available_binsizes', sa.String(length=500), nullable=True),
    sa.Column('processing_state', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dataset_dataset_name'), 'dataset', ['dataset_name'], unique=False)
    op.create_index(op.f('ix_dataset_file_path'), 'dataset', ['file_path'], unique=False)
    op.create_index(op.f('ix_dataset_filetype'), 'dataset', ['filetype'], unique=False)
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('session_object', sa.String(length=10000), nullable=True),
    sa.Column('created_utc', sa.DateTime(), nullable=False),
    sa.Column('session_type', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bed_file_metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('file_path', sa.String(length=128), nullable=True),
    sa.Column('metadata_fields', sa.String(length=1024), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('intervals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('file_path', sa.String(length=128), nullable=True),
    sa.Column('file_path_sub_sample_index', sa.String(length=128), nullable=True),
    sa.Column('windowsize', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intervals_file_path'), 'intervals', ['file_path'], unique=False)
    op.create_index(op.f('ix_intervals_file_path_sub_sample_index'), 'intervals', ['file_path_sub_sample_index'], unique=False)
    op.create_index(op.f('ix_intervals_name'), 'intervals', ['name'], unique=False)
    op.create_index(op.f('ix_intervals_windowsize'), 'intervals', ['windowsize'], unique=False)
    op.create_table('session_dataset_assoc_table',
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], )
    )
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    op.create_table('average_interval_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('binsize', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('file_path', sa.String(length=128), nullable=True),
    sa.Column('value_type', sa.String(length=64), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('intervals_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['intervals_id'], ['intervals.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_average_interval_data_file_path'), 'average_interval_data', ['file_path'], unique=False)
    op.create_index(op.f('ix_average_interval_data_name'), 'average_interval_data', ['name'], unique=False)
    op.create_table('individual_interval_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('binsize', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('file_path', sa.String(length=128), nullable=True),
    sa.Column('file_path_small', sa.String(length=128), nullable=True),
    sa.Column('dataset_id', sa.Integer(), nullable=True),
    sa.Column('intervals_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['intervals_id'], ['intervals.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_individual_interval_data_file_path'), 'individual_interval_data', ['file_path'], unique=False)
    op.create_index(op.f('ix_individual_interval_data_file_path_small'), 'individual_interval_data', ['file_path_small'], unique=False)
    op.create_index(op.f('ix_individual_interval_data_name'), 'individual_interval_data', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_individual_interval_data_name'), table_name='individual_interval_data')
    op.drop_index(op.f('ix_individual_interval_data_file_path_small'), table_name='individual_interval_data')
    op.drop_index(op.f('ix_individual_interval_data_file_path'), table_name='individual_interval_data')
    op.drop_table('individual_interval_data')
    op.drop_index(op.f('ix_average_interval_data_name'), table_name='average_interval_data')
    op.drop_index(op.f('ix_average_interval_data_file_path'), table_name='average_interval_data')
    op.drop_table('average_interval_data')
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    op.drop_table('session_dataset_assoc_table')
    op.drop_index(op.f('ix_intervals_windowsize'), table_name='intervals')
    op.drop_index(op.f('ix_intervals_name'), table_name='intervals')
    op.drop_index(op.f('ix_intervals_file_path_sub_sample_index'), table_name='intervals')
    op.drop_index(op.f('ix_intervals_file_path'), table_name='intervals')
    op.drop_table('intervals')
    op.drop_table('bed_file_metadata')
    op.drop_table('session')
    op.drop_index(op.f('ix_dataset_filetype'), table_name='dataset')
    op.drop_index(op.f('ix_dataset_file_path'), table_name='dataset')
    op.drop_index(op.f('ix_dataset_dataset_name'), table_name='dataset')
    op.drop_table('dataset')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
