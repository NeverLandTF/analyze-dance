"""
用户相关路由模块
处理用户认证、用户管理等 API 端点
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import uuid
import os

from models import db, User, Dancer, Video
from utils.auth import token_required, admin_required, generate_token
from utils.file_utils import allowed_file

user_bp = Blueprint('users', __name__, url_prefix='/api')


@user_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'Dance Analysis API is running'})


# ===== 用户认证相关 =====

@user_bp.route('/auth/register', methods=['POST'])
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


@user_bp.route('/auth/login', methods=['POST'])
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

@user_bp.route('/users/<int:user_id>', methods=['GET'])
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


@user_bp.route('/users/<int:user_id>/avatar', methods=['PUT'])
@token_required
def update_avatar(user_id):
    """更新用户头像（支持 URL 或文件上传）"""
    current_user = request.current_user
    app = request.app
    
    # 权限验证：普通用户只能修改自己的头像，管理员可以修改任何用户头像
    if not current_user.get('is_admin', False) and user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only modify your own avatar.'}), 403
    
    # 检查是否是文件上传
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        allowed_image_extensions = app.config.get('ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'])
        if not allowed_file(file.filename, allowed_image_extensions):
            return jsonify({'error': 'File type not allowed. Allowed types: jpg, jpeg, png, gif, bmp, webp'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_avatar_size = app.config.get('MAX_AVATAR_SIZE', 5 * 1024 * 1024)
        if file_size > max_avatar_size:
            return jsonify({'error': 'File size exceeds 5MB limit'}), 400
        
        # 生成唯一的文件名
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 保存文件
        avatar_folder = app.config.get('AVATAR_FOLDER', 'uploads/avatars')
        file_path = os.path.join(avatar_folder, unique_filename)
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


@user_bp.route('/users/<int:user_id>/change-password', methods=['POST'])
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


@user_bp.route('/users', methods=['GET'])
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


@user_bp.route('/users', methods=['POST'])
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


@user_bp.route('/dancers', methods=['GET'])
@token_required
def get_dancers():
    """获取舞者列表（已废弃，请使用 /api/users）"""
    # 重定向到用户接口，保持向后兼容
    return get_users()


@user_bp.route('/dancers', methods=['POST'])
@admin_required
def create_dancer():
    """创建舞者（已废弃，请使用 /api/users）"""
    # 重定向到用户创建接口
    return create_user()


@user_bp.route('/dancers/<int:dancer_id>', methods=['GET'])
@token_required
def get_dancer(dancer_id):
    """获取单个用户详情"""
    current_user = request.current_user
    
    dancer = Dancer.query.get_or_404(dancer_id)
    
    # 权限验证：普通用户只能查看自己的舞者信息，管理员可以查看任何舞者信息
    if not current_user.get('is_admin', False) and dancer.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own dancer information.'}), 403
    
    from routes.progress import get_progress_summary
    
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


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户信息（包括角色） - 仅管理员可访问"""
    current_user = request.current_user
    
    # 防止修改自己
    if user_id == current_user.get('user_id'):
        return jsonify({'error': 'Cannot modify yourself'}), 400
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新用户名
    if 'username' in data:
        # 检查新用户名是否已被其他用户使用
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username already exists'}), 409
        user.username = data['username']
        
        # 同步更新同名舞者名称
        default_dancer = Dancer.query.filter_by(user_id=user_id).first()
        if default_dancer:
            default_dancer.name = data['username']
    
    # 更新邮箱
    if 'email' in data:
        # 检查新邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already exists'}), 409
        user.email = data['email']
    
    # 更新角色（is_admin）
    if 'is_admin' in data:
        user.is_admin = bool(data['is_admin'])
    
    # 更新描述（同步到舞者）
    if 'description' in data:
        default_dancer = Dancer.query.filter_by(user_id=user_id).first()
        if default_dancer:
            default_dancer.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        }
    })


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户 - 仅管理员可访问，删除时清理所有关联数据和文件"""
    from flask import current_app
    
    current_user = request.current_user
    
    # 防止删除自己
    if user_id == current_user.get('user_id'):
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # 获取用户上传目录配置
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    try:
        # 1. 收集并删除该用户的所有视频文件
        videos = Video.query.filter_by(user_id=user_id).all()
        for video in videos:
            # 删除视频文件
            video_file_path = os.path.join(upload_folder, video.file_path.lstrip('/'))
            if os.path.exists(video_file_path):
                try:
                    os.remove(video_file_path)
                except Exception as e:
                    print(f"Error deleting video file {video_file_path}: {e}")
            
            # 删除视频缩略图
            if video.thumbnail_url:
                thumbnail_path = os.path.join(upload_folder, video.thumbnail_url.lstrip('/'))
                if os.path.exists(thumbnail_path):
                    try:
                        os.remove(thumbnail_path)
                    except Exception as e:
                        print(f"Error deleting thumbnail {thumbnail_path}: {e}")
        
        # 2. 删除该用户的头像文件
        if user.avatar_url:
            avatar_path = os.path.join(upload_folder, user.avatar_url.lstrip('/'))
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    print(f"Error deleting avatar {avatar_path}: {e}")
        
        # 3. 删除数据库记录
        # 由于模型中设置了 cascade='all, delete-orphan'，删除用户时会自动删除：
        # - 所有 Dancer 记录
        # - 所有 Video 记录（以及关联的 Analysis 记录）
        # - 所有 Analysis 记录
        # ProgressRecord 通过 dancer_id 关联，需要在删除 Dancer 前处理
        
        # 先删除所有进步记录（通过舞者关联）
        dancers = Dancer.query.filter_by(user_id=user_id).all()
        for dancer in dancers:
            # ProgressRecord 会通过 cascade 自动删除
            pass
        
        # 删除用户（会自动级联删除所有关联数据）
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User and all associated data deleted successfully',
            'deleted_user_id': user_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user {user_id}: {e}")
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500
