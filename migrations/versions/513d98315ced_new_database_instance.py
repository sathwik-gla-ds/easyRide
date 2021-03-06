"""new database instance

Revision ID: 513d98315ced
Revises: 
Create Date: 2021-02-09 04:59:48.685997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '513d98315ced'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bike_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bike_number', sa.Integer(), nullable=True),
    sa.Column('bike_pin', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('YES', 'NO', 'REPAIR', 'DISABLED', name='bikestatus'), nullable=True),
    sa.Column('last_location', sa.Enum('HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON', name='locationnames'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bike_info_bike_number'), 'bike_info', ['bike_number'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile_image', sa.String(length=64), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('country_code', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('city', sa.Enum('GLASGOW', name='cityname'), nullable=True),
    sa.Column('user_type', sa.Enum('NORMAL', 'OPERATOR', 'MANAGER', name='usertype'), nullable=True),
    sa.Column('wallet_balance', sa.Float(), nullable=True),
    sa.Column('session_var', sa.String(length=64), nullable=True),
    sa.Column('user_status', sa.Enum('NORMAL', 'BANNED', 'DELETED', name='userstatus'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('login_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('logged_at', sa.DateTime(), nullable=True),
    sa.Column('user_type', sa.Enum('NORMAL', 'OPERATOR', 'MANAGER', name='usertype'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('repairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('bike_number', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('urgency', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='repairurgency'), nullable=True),
    sa.Column('repair_status', sa.Enum('YES', 'NO', name='repairstatus'), nullable=True),
    sa.Column('operator_id', sa.Integer(), nullable=True),
    sa.Column('repaired_at', sa.DateTime(), nullable=True),
    sa.Column('level_of_repair', sa.Integer(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['bike_number'], ['bike_info.bike_number'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ride_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ride_id', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('bike_number', sa.Integer(), nullable=False),
    sa.Column('start_location', sa.Enum('HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON', name='locationnames'), nullable=True),
    sa.Column('end_location', sa.Enum('HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON', name='locationnames'), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('current', sa.Enum('YES', 'NO', name='currentstatus'), nullable=True),
    sa.ForeignKeyConstraint(['bike_number'], ['bike_info.bike_number'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ride_id')
    )
    op.create_table('topup_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_id', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('credit_card_number', sa.String(length=16), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_id')
    )
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ride_id', sa.String(length=64), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('review', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['ride_log.ride_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ride_id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_id', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('payment_type', sa.Enum('CARD', 'WALLET', name='paymenttype'), nullable=True),
    sa.Column('credit_card_number', sa.String(length=16), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('ride_id', sa.String(length=64), nullable=True),
    sa.Column('paid', sa.Enum('YES', 'NO', name='paidstatus'), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['ride_log.ride_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ride_id'),
    sa.UniqueConstraint('transaction_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('reviews')
    op.drop_table('topup_logs')
    op.drop_table('ride_log')
    op.drop_table('repairs')
    op.drop_table('login_logs')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_bike_info_bike_number'), table_name='bike_info')
    op.drop_table('bike_info')
    # ### end Alembic commands ###
