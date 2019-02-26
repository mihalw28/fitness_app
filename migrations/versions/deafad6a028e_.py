"""empty message

Revision ID: deafad6a028e
Revises: 1ec760107594
Create Date: 2019-02-25 13:18:39.032464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deafad6a028e'
down_revision = '1ec760107594'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_activity_timestamp', table_name='activity')
    op.drop_table('activity')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activity',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('activ_body', sa.VARCHAR(length=140), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_timestamp', 'activity', ['timestamp'], unique=False)
    # ### end Alembic commands ###
