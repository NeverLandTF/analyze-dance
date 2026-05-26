"""Add Chinese comments to table columns and token usage tracking

Revision ID: add369282557
Revises: b2c3d4e5f6g7
Create Date: 2026-05-26 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add369282557'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # ### 为 users 表添加中文注释 ###
    # 注意：主键列必须保持 NOT NULL
    op.alter_column('users', 'id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='用户 ID')
    op.alter_column('users', 'username',
               existing_type=sa.String(length=80),
               existing_nullable=False,
               comment='用户名')
    op.alter_column('users', 'email',
               existing_type=sa.String(length=120),
               existing_nullable=False,
               comment='邮箱地址')
    op.alter_column('users', 'password_hash',
               existing_type=sa.String(length=256),
               existing_nullable=False,
               comment='密码哈希值')
    op.alter_column('users', 'avatar_url',
               existing_type=sa.String(length=255),
               comment='用户头像 URL')
    op.alter_column('users', 'is_admin',
               existing_type=sa.Boolean(),
               comment='是否为管理员')
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(),
               comment='创建时间')

    # ### 为 dancers 表添加中文注释 ###
    op.alter_column('dancers', 'id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='舞者 ID')
    op.alter_column('dancers', 'user_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='所属用户 ID')
    op.alter_column('dancers', 'name',
               existing_type=sa.String(length=100),
               existing_nullable=False,
               comment='舞者名称')
    op.alter_column('dancers', 'description',
               existing_type=sa.Text(),
               comment='舞者描述')
    op.alter_column('dancers', 'avatar_url',
               existing_type=sa.String(length=255),
               comment='舞者头像 URL')
    op.alter_column('dancers', 'created_at',
               existing_type=sa.DateTime(),
               comment='创建时间')
    op.alter_column('dancers', 'updated_at',
               existing_type=sa.DateTime(),
               comment='更新时间')

    # ### 为 videos 表添加中文注释 ###
    op.alter_column('videos', 'id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='视频 ID')
    op.alter_column('videos', 'user_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='所属用户 ID')
    op.alter_column('videos', 'dancer_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='舞者 ID')
    op.alter_column('videos', 'title',
               existing_type=sa.String(length=200),
               existing_nullable=False,
               comment='视频标题')
    op.alter_column('videos', 'file_path',
               existing_type=sa.String(length=500),
               existing_nullable=False,
               comment='文件存储路径')
    op.alter_column('videos', 'thumbnail_url',
               existing_type=sa.String(length=255),
               comment='缩略图 URL')
    op.alter_column('videos', 'duration',
               existing_type=sa.Float(),
               comment='视频时长（秒）')
    op.alter_column('videos', 'upload_date',
               existing_type=sa.DateTime(),
               comment='上传时间')
    op.alter_column('videos', 'dance_style',
               existing_type=sa.String(length=50),
               comment='舞蹈风格：breaking, popping, locking 等')

    # ### 为 analyses 表添加中文注释 ###
    op.alter_column('analyses', 'id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='分析记录 ID')
    op.alter_column('analyses', 'user_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='所属用户 ID')
    op.alter_column('analyses', 'video_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='关联视频 ID')
    op.alter_column('analyses', 'analysis_type',
               existing_type=sa.String(length=50),
               existing_nullable=False,
               comment='分析类型：pose_detection, movement_tracking, score_evaluation')
    op.alter_column('analyses', 'result_data',
               existing_type=sa.JSON(),
               comment='AI 分析的详细结果数据（包含 token_usage）')
    op.alter_column('analyses', 'confidence_score',
               existing_type=sa.Float(),
               comment='置信度分数')
    op.alter_column('analyses', 'processed_at',
               existing_type=sa.DateTime(),
               comment='处理时间')
    op.alter_column('analyses', 'model_version',
               existing_type=sa.String(length=50),
               comment='使用的 AI 模型版本')

    # ### 为 progress_records 表添加中文注释 ###
    op.alter_column('progress_records', 'id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='进步记录 ID')
    op.alter_column('progress_records', 'dancer_id',
               existing_type=sa.Integer(),
               existing_nullable=False,
               comment='舞者 ID')
    op.alter_column('progress_records', 'skill_category',
               existing_type=sa.String(length=100),
               existing_nullable=False,
               comment='技能类别：rhythm, technique, creativity 等')
    op.alter_column('progress_records', 'score',
               existing_type=sa.Float(),
               existing_nullable=False,
               comment='得分')
    op.alter_column('progress_records', 'improvement_rate',
               existing_type=sa.Float(),
               comment='进步率')
    op.alter_column('progress_records', 'feedback',
               existing_type=sa.Text(),
               comment='AI 生成的反馈建议')
    op.alter_column('progress_records', 'recorded_at',
               existing_type=sa.DateTime(),
               comment='记录时间')
    op.alter_column('progress_records', 'comparison_video_ids',
               existing_type=sa.JSON(),
               comment='用于对比的视频 ID 列表')


def downgrade():
    # ### 移除所有中文注释 ###
    op.alter_column('progress_records', 'comparison_video_ids',
               existing_type=sa.JSON(),
               comment=None)
    op.alter_column('progress_records', 'recorded_at',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('progress_records', 'feedback',
               existing_type=sa.Text(),
               comment=None)
    op.alter_column('progress_records', 'improvement_rate',
               existing_type=sa.Float(),
               comment=None)
    op.alter_column('progress_records', 'score',
               existing_type=sa.Float(),
               comment=None)
    op.alter_column('progress_records', 'skill_category',
               existing_type=sa.String(length=100),
               comment=None)
    op.alter_column('progress_records', 'dancer_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('progress_records', 'id',
               existing_type=sa.Integer(),
               comment=None)
    
    op.alter_column('analyses', 'model_version',
               existing_type=sa.String(length=50),
               comment=None)
    op.alter_column('analyses', 'processed_at',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('analyses', 'confidence_score',
               existing_type=sa.Float(),
               comment=None)
    op.alter_column('analyses', 'result_data',
               existing_type=sa.JSON(),
               comment=None)
    op.alter_column('analyses', 'analysis_type',
               existing_type=sa.String(length=50),
               comment=None)
    op.alter_column('analyses', 'video_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('analyses', 'user_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('analyses', 'id',
               existing_type=sa.Integer(),
               comment=None)
    
    op.alter_column('videos', 'dance_style',
               existing_type=sa.String(length=50),
               comment=None)
    op.alter_column('videos', 'upload_date',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('videos', 'duration',
               existing_type=sa.Float(),
               comment=None)
    op.alter_column('videos', 'thumbnail_url',
               existing_type=sa.String(length=255),
               comment=None)
    op.alter_column('videos', 'file_path',
               existing_type=sa.String(length=500),
               comment=None)
    op.alter_column('videos', 'title',
               existing_type=sa.String(length=200),
               comment=None)
    op.alter_column('videos', 'dancer_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('videos', 'user_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('videos', 'id',
               existing_type=sa.Integer(),
               comment=None)
    
    op.alter_column('dancers', 'updated_at',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('dancers', 'created_at',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('dancers', 'avatar_url',
               existing_type=sa.String(length=255),
               comment=None)
    op.alter_column('dancers', 'description',
               existing_type=sa.Text(),
               comment=None)
    op.alter_column('dancers', 'name',
               existing_type=sa.String(length=100),
               comment=None)
    op.alter_column('dancers', 'user_id',
               existing_type=sa.Integer(),
               comment=None)
    op.alter_column('dancers', 'id',
               existing_type=sa.Integer(),
               comment=None)
    
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(),
               comment=None)
    op.alter_column('users', 'is_admin',
               existing_type=sa.Boolean(),
               comment=None)
    op.alter_column('users', 'avatar_url',
               existing_type=sa.String(length=255),
               comment=None)
    op.alter_column('users', 'password_hash',
               existing_type=sa.String(length=256),
               comment=None)
    op.alter_column('users', 'email',
               existing_type=sa.String(length=120),
               comment=None)
    op.alter_column('users', 'username',
               existing_type=sa.String(length=80),
               comment=None)
    op.alter_column('users', 'id',
               existing_type=sa.Integer(),
               comment=None)
    # ### end Alembic commands ###
