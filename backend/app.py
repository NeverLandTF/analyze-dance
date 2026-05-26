from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import hashlib
import os
import uuid
import jwt
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
CORS(app)

# 数据库配置 - 从环境变量获取
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/dance_analysis_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# JWT 配置
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

# 文件上传配置 - 从环境变量获取
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')  # 头像放在 uploads/avatars 子目录下
ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'mp4,avi,mov,mkv,webm').split(',')
ALLOWED_IMAGE_EXTENSIONS = os.environ.get('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,webp').split(',')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1024 * 1024 * 1024))  # 默认 1GB
MAX_AVATAR_SIZE = int(os.environ.get('MAX_AVATAR_SIZE', 5 * 1024 * 1024))  # 默认 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录及其子目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)  # 视频子目录
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)  # 图片子目录

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ==================== JWT 认证相关 ====================

def generate_token(user_id, username, is_admin=False):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token):
    """验证 JWT token，返回解码后的 payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """装饰器：要求请求必须携带有效的 JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从 Authorization header 中获取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if payload is None:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # 将用户信息添加到 request 中
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """装饰器：要求用户必须是管理员"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not request.current_user.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated


def allowed_file(filename):
    """检查文件扩展名是否允许（视频）"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext.strip() for ext in ALLOWED_EXTENSIONS]


def allowed_image(filename):
    """检查文件扩展名是否允许（图片）"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext.strip() for ext in ALLOWED_IMAGE_EXTENSIONS]


# ==================== 数据模型 ====================

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
    result_data = db.Column(db.JSON)  # 存储AI分析的详细结果
    confidence_score = db.Column(db.Float)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50))  # 使用的AI模型版本


class ProgressRecord(db.Model):
    """进步追踪记录表"""
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True)
    dancer_id = db.Column(db.Integer, db.ForeignKey('dancers.id'), nullable=False)
    skill_category = db.Column(db.String(100), nullable=False)  # 技能类别：rhythm, technique, creativity等
    score = db.Column(db.Float, nullable=False)
    improvement_rate = db.Column(db.Float)  # 进步率
    feedback = db.Column(db.Text)  # AI生成的反馈建议
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    comparison_video_ids = db.Column(db.JSON)  # 用于对比的视频ID列表


# ==================== API 路由 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'Dance Analysis API is running'})


# ===== 用户认证相关 =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册 - 注册时自动创建一个同名舞者"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    user = User(
        username=data['username'], 
        email=data['email'],
        avatar_url=data.get('avatar_url')  # 可选的头像 URL
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()  # 获取 user.id 但不提交
    
    # 自动创建一个同名舞者（普通用户只能有一个舞者，就是自己）
    dancer = Dancer(
        user_id=user.id,
        name=data['username'],  # 使用用户名作为舞者名称
        description='个人舞者档案',
        avatar_url=data.get('avatar_url')  # 同步舞者头像
    )
    db.session.add(dancer)
    
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.id,
        'dancer_id': dancer.id
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 生成 JWT token
    token = generate_token(user.id, user.username, user.is_admin)
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
        'token': token
    })


# ===== 用户管理 =====

@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """获取用户信息"""
    current_user = request.current_user
    
    # 权限验证：普通用户只能查看自己的信息，管理员可以查看任何用户信息
    if not current_user.get('is_admin', False) and user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own information.'}), 403
    
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })


@app.route('/api/users/<int:user_id>/avatar', methods=['PUT'])
@token_required
def update_avatar(user_id):
    """更新用户头像（支持 URL 或文件上传）"""
    current_user = request.current_user
    
    # 权限验证：普通用户只能修改自己的头像，管理员可以修改任何用户头像
    if not current_user.get('is_admin', False) and user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only modify your own avatar.'}), 403
    
    # 检查是否是文件上传
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_image(file.filename):
            return jsonify({'error': 'File type not allowed. Allowed types: jpg, jpeg, png, gif, bmp, webp'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_AVATAR_SIZE:
            return jsonify({'error': 'File size exceeds 5MB limit'}), 400
        
        # 生成唯一的文件名
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 保存文件
        file_path = os.path.join(app.config['AVATAR_FOLDER'], unique_filename)
        file.save(file_path)
        
        # 生成访问 URL
        avatar_url = f'/api/avatars/{unique_filename}'
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.avatar_url = avatar_url
        
        # 同步更新该用户的默认舞者头像
        default_dancer = Dancer.query.filter_by(user_id=user_id).first()
        if default_dancer:
            default_dancer.avatar_url = avatar_url
        
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'avatar_url': user.avatar_url
        })
    else:
        # JSON 方式更新头像 URL
        data = request.get_json()
        
        if not data or not data.get('avatar_url'):
            return jsonify({'error': 'Missing avatar_url'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.avatar_url = data['avatar_url']
        
        # 同步更新该用户的默认舞者头像
        default_dancer = Dancer.query.filter_by(user_id=user_id).first()
        if default_dancer:
            default_dancer.avatar_url = data['avatar_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar updated successfully',
            'avatar_url': user.avatar_url
        })


@app.route('/api/users/<int:user_id>/change-password', methods=['POST'])
@token_required
def change_password(user_id):
    """修改密码"""
    current_user = request.current_user
    
    # 权限验证：普通用户只能修改自己的密码，管理员可以修改任何用户密码
    if not current_user.get('is_admin', False) and user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only change your own password.'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 验证旧密码
    if not user.check_password(data['old_password']):
        return jsonify({'error': '旧密码错误'}), 401
    
    # 设置新密码
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})


# ===== 用户管理 =====

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    """获取用户列表 - 仅管理员可访问，普通用户无法查看"""
    current_user = request.current_user
    
    # 只有管理员才能查看所有用户列表
    if not current_user.get('is_admin', False):
        return jsonify({'error': '普通用户无法查看用户列表'}), 403
    
    # 管理员可以查看所有用户
    users = User.query.all()
    
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'avatar_url': u.avatar_url,
            'is_admin': u.is_admin,
            'created_at': u.created_at.isoformat(),
            'video_count': len(u.videos)
        } for u in users]
    })


@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """创建新用户 - 仅管理员可以创建"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields (username, email, password)'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    # 自动创建一个同名舞者
    dancer = Dancer(
        user_id=user.id,
        name=data['username'],
        description=data.get('description', '个人舞者档案'),
        avatar_url=data.get('avatar_url')
    )
    db.session.add(dancer)
    
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': user.id,
        'dancer_id': dancer.id
    }), 201


@app.route('/api/dancers', methods=['GET'])
@token_required
def get_dancers():
    """获取舞者列表（已废弃，请使用 /api/users）"""
    # 重定向到用户接口，保持向后兼容
    return get_users()


@app.route('/api/dancers', methods=['POST'])
@admin_required
def create_dancer():
    """创建舞者（已废弃，请使用 /api/users）"""
    # 重定向到用户创建接口
    return create_user()


@app.route('/api/dancers/<int:dancer_id>', methods=['GET'])
@token_required
def get_dancer(dancer_id):
    """获取单个用户详情"""
    current_user = request.current_user
    
    dancer = Dancer.query.get_or_404(dancer_id)
    
    # 权限验证：普通用户只能查看自己的舞者信息，管理员可以查看任何舞者信息
    if not current_user.get('is_admin', False) and dancer.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own dancer information.'}), 403
    
    return jsonify({
        'id': dancer.id,
        'name': dancer.name,
        'description': dancer.description,
        'avatar_url': dancer.avatar_url,
        'created_at': dancer.created_at.isoformat(),
        'videos': [{
            'id': v.id,
            'title': v.title,
            'upload_date': v.upload_date.isoformat(),
            'dance_style': v.dance_style
        } for v in dancer.videos],
        'progress_summary': get_progress_summary(dancer.id)
    })


# ===== 视频管理 =====

@app.route('/api/videos/upload', methods=['POST'])
@token_required
def upload_video_file():
    """上传视频文件（需要 JWT 认证）"""
    # 从 token 中获取当前用户信息
    current_user = request.current_user
    
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 获取表单数据（user_id 和 dancer_id 现在可以从 token 中获取，但为了兼容性仍支持表单传递）
    user_id = request.form.get('user_id') or current_user.get('user_id')
    dancer_id = request.form.get('dancer_id')
    if dancer_id:
        dancer_id = int(dancer_id)  # 转换为整数
    title = request.form.get('title')
    dance_style = request.form.get('dance_style', '')
    
    if not title:
        return jsonify({'error': 'Missing required field (title)'}), 400
    
    # 如果没有提供 dancer_id，尝试获取用户的默认舞者（即 user_id 对应的第一个舞者）
    if not dancer_id:
        default_dancer = Dancer.query.filter_by(user_id=int(user_id)).first()
        if default_dancer:
            dancer_id = default_dancer.id
        else:
            return jsonify({'error': 'No dancer found for this user. Please create a dancer profile first.'}), 400
    
    # 权限验证：普通用户只能给自己上传视频，管理员可以给任何人上传
    if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only upload videos for yourself.'}), 403
    
    # 生成唯一的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'mp4'
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 保存到 videos 子目录
    video_subfolder = os.environ.get('VIDEO_SUBFOLDER', 'videos')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], video_subfolder, unique_filename)
    file.save(file_path)
    
    # 创建视频记录
    video = Video(
        user_id=int(user_id),
        dancer_id=dancer_id,  # dancer_id 已经是整数了
        title=title,
        file_path=f'/uploads/{video_subfolder}/{unique_filename}',
        thumbnail_url=None,
        duration=None,
        dance_style=dance_style
    )
    
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'message': 'Video uploaded successfully',
        'video_id': video.id,
        'file_path': video.file_path
    }), 201


@app.route('/api/videos', methods=['POST'])
@token_required
def upload_video():
    """上传视频（元数据方式，用于兼容旧接口）"""
    current_user = request.current_user
    data = request.get_json()
    
    if not data or not data.get('dancer_id') or not data.get('title'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 从 token 中获取 user_id，除非是管理员可以指定其他用户
    user_id = data.get('user_id')
    if not user_id:
        user_id = current_user.get('user_id')
    else:
        # 如果不是管理员，只能给自己上传视频
        if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
            return jsonify({'error': 'Permission denied. You can only upload videos for yourself.'}), 403
    
    video = Video(
        user_id=user_id,
        dancer_id=data['dancer_id'],
        title=data['title'],
        file_path=data['file_path'],
        thumbnail_url=data.get('thumbnail_url'),
        duration=data.get('duration'),
        dance_style=data.get('dance_style')
    )
    
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'message': 'Video uploaded successfully',
        'video_id': video.id
    }), 201


@app.route('/api/videos', methods=['GET'])
@token_required
def get_videos():
    """获取视频列表（需要 JWT 认证）"""
    current_user = request.current_user
    
    # 从 query 参数或 token 中获取 user_id
    user_id = request.args.get('user_id') or current_user.get('user_id')
    dancer_id = request.args.get('dancer_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # 权限验证：普通用户只能查看自己的视频，管理员可以查看所有视频
    if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own videos.'}), 403
    
    query = Video.query.filter_by(user_id=int(user_id))
    
    if dancer_id:
        query = query.filter_by(dancer_id=int(dancer_id))
    
    videos = query.order_by(Video.upload_date.desc()).all()
    
    return jsonify({
        'videos': [{
            'id': v.id,
            'title': v.title,
            'file_path': v.file_path,
            'thumbnail_url': v.thumbnail_url,
            'duration': v.duration,
            'upload_date': v.upload_date.isoformat() if v.upload_date else None,
            'dance_style': v.dance_style,
            'dancer_id': v.dancer_id
        } for v in videos]
    })


@app.route('/api/videos/<int:video_id>', methods=['GET'])
@token_required
def get_video(video_id):
    """获取单个视频详情（需要 JWT 认证）"""
    current_user = request.current_user
    
    video = Video.query.get_or_404(video_id)
    
    # 权限验证：普通用户只能查看自己的视频，管理员可以查看所有视频
    if not current_user.get('is_admin', False) and video.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own videos.'}), 403
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'file_path': video.file_path,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'upload_date': video.upload_date.isoformat() if video.upload_date else None,
        'dance_style': video.dance_style,
        'dancer_id': video.dancer_id,
        'analyses': [{
            'id': a.id,
            'analysis_type': a.analysis_type,
            'result_data': a.result_data,
            'confidence_score': a.confidence_score,
            'processed_at': a.processed_at.isoformat() if a.processed_at else None
        } for a in video.analyses]
    })


# ===== AI 分析 =====

@app.route('/api/analyze', methods=['POST'])
@token_required
def analyze_video():
    """触发AI视频分析"""
    data = request.get_json()
    
    if not data or not data.get('video_id') or not data.get('user_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    video = Video.query.get(data['video_id'])
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # 模拟AI分析结果 - 实际项目中应调用大模型API
    analysis_result = {
        'pose_detection': {'confidence': 0.95, 'keypoints': []},
        'movement_quality': {'score': 85.5, 'feedback': 'Good rhythm, improve flexibility'},
        'comparison_with_previous': {'improvement': '+12%', 'areas_to_focus': ['footwork', 'transitions']}
    }
    
    analysis = Analysis(
        user_id=data['user_id'],
        video_id=data['video_id'],
        analysis_type='comprehensive',
        result_data=analysis_result,
        confidence_score=0.92,
        model_version='v2.1'
    )
    
    db.session.add(analysis)
    
    # 更新进步记录
    update_progress_record(data['user_id'], video.dancer_id, analysis_result)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Analysis completed',
        'analysis_id': analysis.id,
        'results': analysis_result
    })


def update_progress_record(user_id, dancer_id, analysis_result):
    """更新舞者进步记录"""
    movement_quality = analysis_result.get('movement_quality', {})
    
    progress = ProgressRecord(
        dancer_id=dancer_id,
        skill_category='overall',
        score=movement_quality.get('score', 0),
        improvement_rate=12.0,  # 从对比结果中提取
        feedback=movement_quality.get('feedback', ''),
        comparison_video_ids=[]
    )
    
    db.session.add(progress)


def get_progress_summary(dancer_id):
    """获取舞者进步摘要"""
    records = ProgressRecord.query.filter_by(dancer_id=dancer_id).order_by(ProgressRecord.recorded_at.desc()).limit(10).all()
    
    if not records:
        return {'total_records': 0, 'trend': 'no_data'}
    
    scores = [r.score for r in records]
    avg_score = sum(scores) / len(scores)
    
    # 计算趋势
    if len(scores) >= 2:
        trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
    else:
        trend = 'insufficient_data'
    
    return {
        'total_records': len(records),
        'average_score': round(avg_score, 2),
        'latest_score': scores[0],
        'trend': trend,
        'recent_records': [{
            'skill_category': r.skill_category,
            'score': r.score,
            'improvement_rate': r.improvement_rate,
            'recorded_at': r.recorded_at.isoformat()
        } for r in records[:5]]
    }


# ===== 进步追踪 =====

@app.route('/api/progress/<int:dancer_id>', methods=['GET'])
@token_required
def get_progress(dancer_id):
    """获取舞者的进步追踪数据"""
    current_user = request.current_user
    
    # 查找舞者并验证权限
    dancer = Dancer.query.get_or_404(dancer_id)
    
    # 权限验证：普通用户只能查看自己的进步记录，管理员可以查看任何记录
    if not current_user.get('is_admin', False) and dancer.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own progress.'}), 403
    
    summary = get_progress_summary(dancer_id)
    
    records = ProgressRecord.query.filter_by(dancer_id=dancer_id).order_by(ProgressRecord.recorded_at.desc()).all()
    
    return jsonify({
        'dancer_id': dancer_id,
        'summary': summary,
        'records': [{
            'id': r.id,
            'skill_category': r.skill_category,
            'score': r.score,
            'improvement_rate': r.improvement_rate,
            'feedback': r.feedback,
            'recorded_at': r.recorded_at.isoformat()
        } for r in records]
    })


# ==================== 初始化数据库 ====================

# Flask-Migrate 已自动处理数据库迁移
# 使用命令:
#   flask db init    - 初始化迁移仓库 (仅需一次)
#   flask db migrate -m "描述"  - 创建新的迁移文件
#   flask db upgrade - 应用迁移到数据库 (会自动创建管理员账户)


# 静态文件服务 - 提供上传的视频文件和头像访问
@app.route('/api/uploads/<filename>')
def serve_upload(filename):
    """提供上传的视频文件访问"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/avatars/<filename>')
def serve_avatar(filename):
    """提供头像文件访问"""
    from flask import send_from_directory
    return send_from_directory(app.config['AVATAR_FOLDER'], filename)


@app.route('/api/upload/temp-avatar', methods=['POST'])
def upload_temp_avatar():
    """临时头像上传接口 - 用于注册时上传头像
    返回一个临时的 avatar_url，注册成功后会关联到用户
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_image(file.filename):
        return jsonify({'error': 'File type not allowed. Allowed types: jpg, jpeg, png, gif, bmp, webp'}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_AVATAR_SIZE:
        return jsonify({'error': 'File size exceeds 5MB limit'}), 400
    
    # 生成唯一的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_filename = f"temp_{uuid.uuid4().hex}.{ext}"
    
    # 保存文件
    file_path = os.path.join(app.config['AVATAR_FOLDER'], unique_filename)
    file.save(file_path)
    
    # 生成访问 URL
    avatar_url = f'/api/avatars/{unique_filename}'
    
    return jsonify({
        'message': 'Avatar uploaded successfully',
        'avatar_url': avatar_url
    }), 201


if __name__ == '__main__':
    # 生产环境使用 Gunicorn 启动，不需要 debug 模式
    # 开发环境下可以运行此脚本
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    if debug_mode:
        app.run(debug=True, host=host, port=port)
    else:
        print('Production mode: Use Gunicorn to start the application')
