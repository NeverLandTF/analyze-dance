"""
视频相关路由模块
处理视频上传、查询等 API 端点
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os

from models import db, Video, Dancer
from utils.auth import token_required
from utils.file_utils import allowed_file, extract_video_thumbnail, get_video_duration

video_bp = Blueprint('videos', __name__, url_prefix='/api')


@video_bp.route('/videos/upload', methods=['POST'])
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
    
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', ['mp4', 'avi', 'mov', 'mkv', 'webm'])
    if not allowed_file(file.filename, allowed_extensions):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 获取表单数据（user_id 和 dancer_id 现在可以从 token 中获取，但为了兼容性仍支持表单传递）
    user_id = request.form.get('user_id') or current_user.get('user_id')
    dancer_id = request.form.get('dancer_id')
    if dancer_id:
        dancer_id = int(dancer_id)  # 转换为整数
        # 验证 dancer_id 是否存在于 dancers 表中
        dancer = Dancer.query.get(dancer_id)
        if not dancer:
            return jsonify({'error': f'Dancer with id {dancer_id} not found'}), 400
    title = request.form.get('title')
    dance_style = request.form.get('dance_style', '')
    video_type = request.form.get('video_type', 'single')  # 视频类型：single（单人）或 multiple（多人）
    
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
    
    # 处理 frame_image（仅当视频类型为多人视频时需要）
    frame_image_path = None
    if video_type == 'multiple' and 'frame_image' in request.files:
        frame_image_file = request.files['frame_image']
        if frame_image_file.filename != '':
            allowed_image_extensions = ['jpg', 'jpeg', 'png', 'webp']
            if allowed_file(frame_image_file.filename, allowed_image_extensions):
                original_frame_filename = secure_filename(frame_image_file.filename)
                frame_ext = original_frame_filename.rsplit('.', 1)[1].lower() if '.' in original_frame_filename else 'jpg'
                frame_unique_filename = f"{uuid.uuid4().hex}.{frame_ext}"
                
                # 保存到 images 子目录
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
                frame_file_path = os.path.join(upload_folder, 'images', frame_unique_filename)
                frame_image_file.save(frame_file_path)
                
                frame_image_path = f'/uploads/images/{frame_unique_filename}'
    
    # 生成唯一的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'mp4'
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 获取文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    # 保存到 videos 子目录
    video_subfolder = os.environ.get('VIDEO_SUBFOLDER', 'videos')
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, video_subfolder, unique_filename)
    file.save(file_path)
    
    # 提取视频封面图（取第 1 秒的帧）
    thumbnail_filename = f"{uuid.uuid4().hex}.jpg"
    thumbnail_path = os.path.join(upload_folder, 'images', thumbnail_filename)
    # 确保 images 目录存在
    os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
    
    thumbnail_generated = extract_video_thumbnail(file_path, thumbnail_path, frame_time=1)
    thumbnail_url = f'/uploads/images/{thumbnail_filename}' if thumbnail_generated else None
    
    # 获取视频时长
    duration = get_video_duration(file_path)
    
    # 创建视频记录
    video = Video(
        user_id=int(user_id),
        dancer_id=dancer_id,  # dancer_id 已经是整数了
        title=title,
        file_path=f'/uploads/{video_subfolder}/{unique_filename}',
        file_format=ext,
        file_size=file_size,
        thumbnail_url=thumbnail_url,
        duration=duration,
        dance_style=dance_style,
        video_type=video_type,
        frame_image_path=frame_image_path
    )
    
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'message': 'Video uploaded successfully',
        'id': video.id,
        'file_path': video.file_path,
        'file_format': video.file_format,
        'file_size': video.file_size,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'title': video.title,
        'dance_style': video.dance_style
    }), 201


@video_bp.route('/videos', methods=['POST'])
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
        'id': video.id,
        'file_path': video.file_path,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'title': video.title,
        'dance_style': video.dance_style
    }), 201


@video_bp.route('/videos', methods=['GET'])
@token_required
def get_videos():
    """获取视频列表（需要 JWT 认证）- 仅返回基本信息和封面，支持时间过滤和分页"""
    current_user = request.current_user
    
    # 从 query 参数或 token 中获取 user_id
    user_id = request.args.get('user_id') or current_user.get('user_id')
    dancer_id = request.args.get('dancer_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # 权限验证：普通用户只能查看自己的视频，管理员可以查看所有视频
    if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own videos.'}), 403
    
    # 时间过滤参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 如果是管理员且没有指定 dancer_id，则查询所有视频（不限制 user_id）
    # 否则按 user_id 查询
    if current_user.get('is_admin', False) and not dancer_id:
        # 管理员选择"全部舞者"时，查询所有视频
        query = Video.query
    else:
        # 普通用户或管理员选择了特定舞者
        query = Video.query.filter_by(user_id=int(user_id))
    
    if dancer_id:
        query = query.filter_by(dancer_id=int(dancer_id))
    
    # 应用时间过滤
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(Video.upload_date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            # 包含结束日期的整天
            end = datetime.fromisoformat(end_date)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Video.upload_date <= end)
        except ValueError:
            pass
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    # 限制每页最大数量
    per_page = min(per_page, 50)
    
    # 执行分页查询
    pagination = query.order_by(Video.upload_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    videos = pagination.items
    
    # 构建响应
    response = {
        'videos': [{
            'id': v.id,
            'title': v.title,
            'file_path': v.file_path,
            'file_format': v.file_format,
            'file_size': v.file_size,
            'thumbnail_url': v.thumbnail_url,
            'duration': v.duration,
            'upload_date': v.upload_date.isoformat() if v.upload_date else None,
            'dance_style': v.dance_style,
            'dancer_id': v.dancer_id
        } for v in videos],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    return jsonify(response)


@video_bp.route('/videos/summary', methods=['GET'])
@token_required
def get_videos_summary():
    """获取视频列表摘要（仅封面和基本信息，性能更优）"""
    current_user = request.current_user
    
    # 从 query 参数或 token 中获取 user_id
    user_id = request.args.get('user_id') or current_user.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # 权限验证
    if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # 使用更高效的方式查询，只选择需要的字段
    videos = db.session.query(
        Video.id,
        Video.title,
        Video.file_path,
        Video.file_format,
        Video.file_size,
        Video.thumbnail_url,
        Video.duration,
        Video.upload_date,
        Video.dance_style,
        Video.dancer_id
    ).filter_by(user_id=int(user_id)).order_by(Video.upload_date.desc()).all()
    
    return jsonify({
        'videos': [{
            'id': v.id,
            'title': v.title,
            'file_path': v.file_path,
            'file_format': v.file_format,
            'file_size': v.file_size,
            'thumbnail_url': v.thumbnail_url,
            'duration': v.duration,
            'upload_date': v.upload_date.isoformat() if v.upload_date else None,
            'dance_style': v.dance_style,
            'dancer_id': v.dancer_id
        } for v in videos]
    })


@video_bp.route('/videos/<int:video_id>', methods=['GET'])
@token_required
def get_video(video_id):
    """获取单个视频详情（需要 JWT 认证）- 不再包含 analyses 字段"""
    current_user = request.current_user
    
    video = Video.query.get_or_404(video_id)
    
    # 权限验证：普通用户只能查看自己的视频，管理员可以查看所有视频
    if not current_user.get('is_admin', False) and video.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own videos.'}), 403
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'file_path': video.file_path,
        'file_format': video.file_format,
        'file_size': video.file_size,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'upload_date': video.upload_date.isoformat() if video.upload_date else None,
        'dance_style': video.dance_style,
        'dancer_id': video.dancer_id,
        'video_url': video.file_path  # 添加 video_url 字段用于前端预览
    })


@video_bp.route('/videos/<int:video_id>/analyses', methods=['GET'])
@token_required
def get_video_analyses(video_id):
    """获取单个视频的分析结果列表（需要 JWT 认证）"""
    current_user = request.current_user
    
    video = Video.query.get_or_404(video_id)
    
    # 权限验证：普通用户只能查看自己的视频，管理员可以查看所有视频
    if not current_user.get('is_admin', False) and video.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own videos.'}), 403
    
    return jsonify({
        'analyses': [{
            'id': a.id,
            'analysis_type': a.analysis_type,
            'result_data': a.result_data,
            'confidence_score': a.confidence_score,
            'processed_at': a.processed_at.isoformat() if a.processed_at else None
        } for a in video.analyses]
    })


@video_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@token_required
def delete_video(video_id):
    """删除视频及其关联的分析记录（需要 JWT 认证）"""
    current_user = request.current_user
    
    video = Video.query.get_or_404(video_id)
    
    # 权限验证：普通用户只能删除自己的视频，管理员可以删除任何视频
    if not current_user.get('is_admin', False) and video.user_id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only delete your own videos.'}), 403
    
    # 删除视频文件（可选，如果需要物理删除文件）
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, video.file_path.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除封面图
        if video.thumbnail_url:
            thumbnail_path = os.path.join(upload_folder, video.thumbnail_url.lstrip('/'))
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
    except Exception as e:
        print(f'删除文件失败：{e}')
    
    # 删除数据库记录（由于 cascade='all, delete-orphan'，关联的 Analysis 记录会自动删除）
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'message': 'Video deleted successfully'})
