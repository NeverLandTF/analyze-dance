"""
数据模型模块
定义所有数据库模型类
"""
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()

# 定义 CST 时区 (UTC+8)
CST = timezone(timedelta(hours=8))

def get_cst_now():
    """获取当前 CST 时间"""
    return datetime.now(CST)


class User(db.Model):
    """用户表 - 实现全数据隔离"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, comment='用户 ID')
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='邮箱地址')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希值')
    avatar_url = db.Column(db.String(255), comment='用户头像 URL')
    is_admin = db.Column(db.Boolean, default=False, comment='是否为管理员')
    created_at = db.Column(db.DateTime, default=get_cst_now, comment='创建时间 (CST/UTC+8)')
    
    dancers = db.relationship('Dancer', backref='user', lazy=True, cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='user', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class Dancer(db.Model):
    """舞者表 - 支持单个人标识"""
    __tablename__ = 'dancers'
    
    id = db.Column(db.Integer, primary_key=True, comment='舞者 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='所属用户 ID')
    name = db.Column(db.String(100), nullable=False, comment='舞者名称')
    description = db.Column(db.Text, comment='舞者描述')
    avatar_url = db.Column(db.String(255), comment='舞者头像 URL')
    created_at = db.Column(db.DateTime, default=get_cst_now, nullable=False, comment='创建时间 (CST/UTC+8)')
    updated_at = db.Column(db.DateTime, default=get_cst_now, onupdate=get_cst_now, nullable=False, comment='更新时间 (CST/UTC+8)')
    
    videos = db.relationship('Video', backref='dancer', lazy=True, cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', backref='dancer', lazy=True, cascade='all, delete-orphan')


class Video(db.Model):
    """视频表"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True, comment='视频 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='所属用户 ID')
    dancer_id = db.Column(db.Integer, db.ForeignKey('dancers.id'), nullable=False, comment='舞者 ID')
    title = db.Column(db.String(200), nullable=False, comment='视频标题')
    file_path = db.Column(db.String(500), nullable=False, comment='文件存储路径')
    file_format = db.Column(db.String(20), comment='文件格式（扩展名）')
    file_size = db.Column(db.BigInteger, comment='文件大小（字节）')
    video_type = db.Column(db.String(20), comment='视频类型：single(单人), multiple(多人)')
    subject_description = db.Column(db.Text, comment='人物主体描述（大模型生成）')
    thumbnail_url = db.Column(db.String(255), comment='缩略图 URL')
    frame_image_path = db.Column(db.String(500), comment='框选帧图片路径（多人视频使用）')
    duration = db.Column(db.Float, comment='视频时长（秒）')
    upload_date = db.Column(db.DateTime, default=get_cst_now, nullable=False, comment='上传时间 (CST/UTC+8)')
    dance_style = db.Column(db.String(50), comment='舞蹈风格：breaking, popping, locking 等')
    
    analyses = db.relationship('Analysis', backref='video', lazy=True, cascade='all, delete-orphan')


class Analysis(db.Model):
    """AI 分析结果表"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True, comment='分析记录 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='所属用户 ID')
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, comment='关联视频 ID')
    analysis_type = db.Column(db.String(50), nullable=False, comment='分析类型：pose_detection, movement_tracking, score_evaluation')
    result_data = db.Column(db.JSON, comment='AI 分析的详细结果数据（包含 token_usage）')
    confidence_score = db.Column(db.Float, comment='置信度分数')
    processed_at = db.Column(db.DateTime, default=get_cst_now, comment='处理时间 (CST/UTC+8)')
    model_version = db.Column(db.String(50), comment='使用的 AI 模型版本')


class ProgressRecord(db.Model):
    """进步追踪记录表"""
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True, comment='进步记录 ID')
    dancer_id = db.Column(db.Integer, db.ForeignKey('dancers.id'), nullable=False, comment='舞者 ID')
    skill_category = db.Column(db.String(100), nullable=False, comment='技能类别：rhythm, technique, creativity 等')
    score = db.Column(db.Float, nullable=False, comment='得分')
    improvement_rate = db.Column(db.Float, comment='进步率')
    feedback = db.Column(db.Text, comment='AI 生成的反馈建议')
    recorded_at = db.Column(db.DateTime, default=get_cst_now, nullable=False, comment='记录时间 (CST/UTC+8)')
    comparison_video_ids = db.Column(db.JSON, comment='用于对比的视频 ID 列表')
