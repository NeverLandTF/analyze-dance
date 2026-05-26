"""
数据模型模块
定义所有数据库模型类
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()


class User(db.Model):
    """用户表 - 实现全数据隔离"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url = db.Column(db.String(255))  # 用户头像 URL
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    videos = db.relationship('Video', backref='dancer', lazy=True, cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', backref='dancer', lazy=True, cascade='all, delete-orphan')


class Video(db.Model):
    """视频表"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dancer_id = db.Column(db.Integer, db.ForeignKey('dancers.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(255))
    duration = db.Column(db.Float)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    dance_style = db.Column(db.String(50))  # 街舞风格：breaking, popping, locking等
    
    analyses = db.relationship('Analysis', backref='video', lazy=True, cascade='all, delete-orphan')


class Analysis(db.Model):
    """AI分析结果表"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # pose_detection, movement_tracking, score_evaluation
    result_data = db.Column(db.JSON)  # 存储 AI 分析的详细结果
    confidence_score = db.Column(db.Float)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50))  # 使用的 AI 模型版本


class ProgressRecord(db.Model):
    """进步追踪记录表"""
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True)
    dancer_id = db.Column(db.Integer, db.ForeignKey('dancers.id'), nullable=False)
    skill_category = db.Column(db.String(100), nullable=False)  # 技能类别：rhythm, technique, creativity等
    score = db.Column(db.Float, nullable=False)
    improvement_rate = db.Column(db.Float)  # 进步率
    feedback = db.Column(db.Text)  # AI 生成的反馈建议
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    comparison_video_ids = db.Column(db.JSON)  # 用于对比的视频 ID 列表
