"""Add admin user creation

Revision ID: a1b2c3d4e5f6
Revises: d90d2b562ea3
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import hashlib


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd90d2b562ea3'
branch_labels = None
depends_on = None


def upgrade():
    # 创建默认管理员账户
    create_admin_user()


def downgrade():
    # 删除管理员账户（可选）
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM users WHERE username = 'admin'")
    )


def create_admin_user():
    """在数据库迁移时创建默认管理员账户"""
    connection = op.get_bind()
    
    # 检查是否已存在管理员
    result = connection.execute(
        sa.text("SELECT id FROM users WHERE username = 'admin'")
    ).fetchone()
    
    if not result:
        # 创建管理员账户：用户名=admin, 密码=admin
        password_hash = hashlib.sha256('admin'.encode()).hexdigest()
        connection.execute(
            sa.text("""
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (:username, :email, :password_hash, :is_admin, NOW())
            """),
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password_hash': password_hash,
                'is_admin': True
            }
        )
        print('默认管理员账户已创建：用户名=admin, 密码=admin')
    else:
        print('管理员账户已存在')
