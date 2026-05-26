"""
文件服务相关路由模块
处理上传文件、头像等静态文件访问
"""
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import os

from utils.file_utils import allowed_file

file_bp = Blueprint('files', __name__, url_prefix='/api')


@file_bp.route('/uploads/<subfolder>/<filename>')
def serve_upload_with_subfolder(subfolder, filename):
    """提供上传的视频文件访问（支持子目录）"""
    upload_folder = request.app.config.get('UPLOAD_FOLDER', 'uploads')
    folder_path = os.path.join(upload_folder, subfolder)
    return send_from_directory(folder_path, filename)


@file_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """提供上传的文件访问（根目录）"""
    upload_folder = request.app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)


@file_bp.route('/avatars/<filename>')
def serve_avatar(filename):
    """提供头像文件访问"""
    avatar_folder = request.app.config.get('AVATAR_FOLDER', 'uploads/avatars')
    return send_from_directory(avatar_folder, filename)


@file_bp.route('/upload/temp-avatar', methods=['POST'])
def upload_temp_avatar():
    """临时头像上传接口 - 用于注册时上传头像
    返回一个临时的 avatar_url，注册成功后会关联到用户
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    allowed_image_extensions = request.app.config.get('ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'])
    if not allowed_file(file.filename, allowed_image_extensions):
        return jsonify({'error': 'File type not allowed. Allowed types: jpg, jpeg, png, gif, bmp, webp'}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    max_avatar_size = request.app.config.get('MAX_AVATAR_SIZE', 5 * 1024 * 1024)
    if file_size > max_avatar_size:
        return jsonify({'error': 'File size exceeds 5MB limit'}), 400
    
    # 生成唯一的文件名
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_filename = f"temp_{uuid.uuid4().hex}.{ext}"
    
    # 保存文件
    avatar_folder = request.app.config.get('AVATAR_FOLDER', 'uploads/avatars')
    file_path = os.path.join(avatar_folder, unique_filename)
    file.save(file_path)
    
    # 生成访问 URL
    avatar_url = f'/api/avatars/{unique_filename}'
    
    return jsonify({
        'message': 'Avatar uploaded successfully',
        'avatar_url': avatar_url
    }), 201
