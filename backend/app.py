from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import hashlib
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 数据库配置 - 从环境变量获取
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/dance_analysis_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 文件上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
AVATAR_FOLDER = os.path.join(os.path.dirname(__file__), 'avatars')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB 最大文件大小
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB 最大头像大小

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def allowed_file(filename):
    """检查文件扩展名是否允许（视频）"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_image(filename):
    """检查文件扩展名是否允许（图片）"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


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
    
    # 实际项目中应该返回 JWT token
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin
    })


# ===== 用户管理 =====

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户信息"""
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
def update_avatar(user_id):
    """更新用户头像（支持 URL 或文件上传）"""
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
def change_password(user_id):
    """修改密码"""
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


# ===== 舞者管理 =====

@app.route('/api/dancers', methods=['GET'])
def get_dancers():
    """获取舞者列表 - 管理员可查看所有舞者，普通用户只看自己的"""
    user_id = request.args.get('user_id')
    is_admin = request.args.get('is_admin', 'false').lower() == 'true'
    
    if not user_id and not is_admin:
        return jsonify({'error': 'user_id is required for non-admin users'}), 400
    
    if is_admin:
        # 管理员可以查看所有舞者
        dancers = Dancer.query.all()
    else:
        # 普通用户只能查看自己的舞者
        dancers = Dancer.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'dancers': [{
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'avatar_url': d.avatar_url,
            'created_at': d.created_at.isoformat(),
            'video_count': len(d.videos),
            'owner_username': d.user.username  # 显示舞者所属用户名
        } for d in dancers]
    })


@app.route('/api/dancers', methods=['POST'])
def create_dancer():
    """创建新舞者 - 仅管理员可以创建（管理员创建舞者相当于创建一个可登录的用户）"""
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('name'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = data['user_id']
    
    # 检查是否为管理员
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    is_admin = user.is_admin
    
    # 只有管理员才能创建舞者
    if not is_admin:
        return jsonify({'error': '普通用户无法创建舞者，注册时已自动创建个人舞者档案'}), 403
    
    dancer = Dancer(
        user_id=user_id,
        name=data['name'],
        description=data.get('description', ''),
        avatar_url=data.get('avatar_url')
    )
    
    db.session.add(dancer)
    db.session.commit()
    
    return jsonify({
        'message': 'Dancer created successfully',
        'dancer_id': dancer.id
    }), 201


@app.route('/api/dancers/<int:dancer_id>', methods=['GET'])
def get_dancer(dancer_id):
    """获取单个舞者详情"""
    dancer = Dancer.query.get_or_404(dancer_id)
    
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
def upload_video_file():
    """上传视频文件"""
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 获取表单数据
    user_id = request.form.get('user_id')
    dancer_id = request.form.get('dancer_id')
    title = request.form.get('title')
    dance_style = request.form.get('dance_style', '')
    
    if not user_id or not dancer_id or not title:
        return jsonify({'error': 'Missing required fields (user_id, dancer_id, title)'}), 400
    
    # 生成唯一的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'mp4'
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 保存文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    # 创建视频记录
    video = Video(
        user_id=int(user_id),
        dancer_id=int(dancer_id),
        title=title,
        file_path=f'/uploads/{unique_filename}',
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
def upload_video():
    """上传视频（元数据方式，用于兼容旧接口）"""
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('dancer_id') or not data.get('title'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    video = Video(
        user_id=data['user_id'],
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
def get_videos():
    """获取视频列表"""
    user_id = request.args.get('user_id')
    dancer_id = request.args.get('dancer_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
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
def get_video(video_id):
    """获取单个视频详情"""
    video = Video.query.get_or_404(video_id)
    
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
def get_progress(dancer_id):
    """获取舞者的进步追踪数据"""
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


if __name__ == '__main__':
    # 生产环境使用 Gunicorn 启动，不需要 debug 模式
    # 开发环境下可以运行此脚本
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    if debug_mode:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print('Production mode: Use Gunicorn to start the application')
