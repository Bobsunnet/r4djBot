"""user_id-BigInteger

Revision ID: 74d631e37563
Revises: 
Create Date: 2026-01-16 14:13:17.797245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74d631e37563'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Исходная миграция применялась к частично созданной БД (users и items
    уже существовали). Теперь эта миграция создаёт их с нуля, чтобы
    `alembic upgrade head` работал на чистой БД без предварительной ручной
    инициализации.

    Таблицы создаются в том состоянии, которое было актуально на момент
    этой ревизии — последующие миграции дополнят их до финального вида.
    """
    # Создаём таблицу users.
    # user_id изначально был INTEGER — ALTER ниже поменяет его на BigInteger,
    # сохраняя совместимость с оригинальной логикой этой миграции.
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('surname', sa.String(length=128), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=256), nullable=True),
        sa.Column('first_name', sa.String(length=256), nullable=True),
        sa.Column('last_name', sa.String(length=256), nullable=True),
        sa.Column('phone_number', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # Создаём таблицу items.
    # Колонка is_deleted будет добавлена позже миграцией 2531435c087c.
    op.create_table(
        'items',
        sa.Column('row_order', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=False),
        sa.Column('hash_code', sa.String(length=10), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('hash_code'),
    )
    op.create_index(op.f('ix_items_last_seen_at'), 'items', ['last_seen_at'], unique=False)

    # Оригинальная операция этой миграции: меняем тип user_id → BigInteger.
    op.alter_column('users', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'user_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    op.drop_index(op.f('ix_items_last_seen_at'), table_name='items')
    op.drop_table('items')
    op.drop_table('users')
