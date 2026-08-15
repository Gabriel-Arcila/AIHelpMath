"""translate to english

Revision ID: e427b0c9fd1a
Revises: f850706adbdc
Create Date: 2026-07-01 17:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e427b0c9fd1a'
down_revision: Union[str, Sequence[str], None] = 'f850706adbdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename tables
    op.rename_table('user_nivel', 'user_level')
    op.rename_table('user_tema_interes', 'user_topic')
    op.rename_table('user_perfil_ia', 'user_ai_profile')
    op.rename_table('user_rol', 'user_role')

    # 2. Rename columns in user_level
    op.alter_column('user_level', 'nombre', new_column_name='name')
    op.alter_column('user_level', 'cuantificador', new_column_name='quantifier')
    op.alter_column('user_level', 'descripcion', new_column_name='description')
    op.execute("ALTER INDEX ix_user_nivel_nombre RENAME TO ix_user_level_name")

    # 3. Rename columns in user_topic
    op.alter_column('user_topic', 'nombre', new_column_name='name')
    op.alter_column('user_topic', 'descripcion', new_column_name='description')
    op.execute("ALTER INDEX ix_user_tema_interes_nombre RENAME TO ix_user_topic_name")

    # 4. Rename columns in user_role
    op.alter_column('user_role', 'nombre', new_column_name='name')
    op.alter_column('user_role', 'descripcion', new_column_name='description')
    op.execute("ALTER INDEX ix_user_rol_nombre RENAME TO ix_user_role_name")

    # 5. Rename columns in user
    op.alter_column('user', 'id_rol', new_column_name='id_role')
    op.alter_column('user', 'nombre', new_column_name='first_name')
    op.alter_column('user', 'apellido', new_column_name='last_name')

    # 6. Rename columns in user_ai_profile
    op.alter_column('user_ai_profile', 'id_user_nivel', new_column_name='id_user_level')
    op.alter_column('user_ai_profile', 'id_user_tema_interes', new_column_name='id_user_topic')
    op.alter_column('user_ai_profile', 'descripcion', new_column_name='description')
    op.execute("ALTER TABLE user_ai_profile RENAME CONSTRAINT unique_user_tema TO unique_user_topic")


def downgrade() -> None:
    # 1. Rename columns and constraints back in user_ai_profile
    op.execute("ALTER TABLE user_ai_profile RENAME CONSTRAINT unique_user_topic TO unique_user_tema")
    op.alter_column('user_ai_profile', 'description', new_column_name='descripcion')
    op.alter_column('user_ai_profile', 'id_user_topic', new_column_name='id_user_tema_interes')
    op.alter_column('user_ai_profile', 'id_user_level', new_column_name='id_user_nivel')

    # 2. Rename columns back in user
    op.alter_column('user', 'last_name', new_column_name='apellido')
    op.alter_column('user', 'first_name', new_column_name='nombre')
    op.alter_column('user', 'id_role', new_column_name='id_rol')

    # 3. Rename columns and indexes back in user_role
    op.execute("ALTER INDEX ix_user_role_name RENAME TO ix_user_rol_nombre")
    op.alter_column('user_role', 'description', new_column_name='descripcion')
    op.alter_column('user_role', 'name', new_column_name='nombre')

    # 4. Rename columns and indexes back in user_topic
    op.execute("ALTER INDEX ix_user_topic_name RENAME TO ix_user_tema_interes_nombre")
    op.alter_column('user_topic', 'description', new_column_name='descripcion')
    op.alter_column('user_topic', 'name', new_column_name='nombre')

    # 5. Rename columns and indexes back in user_level
    op.execute("ALTER INDEX ix_user_level_name RENAME TO ix_user_nivel_nombre")
    op.alter_column('user_level', 'description', new_column_name='descripcion')
    op.alter_column('user_level', 'quantifier', new_column_name='cuantificador')
    op.alter_column('user_level', 'name', new_column_name='nombre')

    # 6. Rename tables back
    op.rename_table('user_role', 'user_rol')
    op.rename_table('user_ai_profile', 'user_perfil_ia')
    op.rename_table('user_topic', 'user_tema_interes')
    op.rename_table('user_level', 'user_nivel')
