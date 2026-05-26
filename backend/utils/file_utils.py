"""
文件工具模块
提供文件上传相关的辅助功能
"""
import os


def get_upload_config(app):
    """从环境变量获取上传配置"""
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'mp4,avi,mov,mkv,webm').split(',')
    ALLOWED_IMAGE_EXTENSIONS = os.environ.get('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,webp').split(',')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1024 * 1024 * 1024))  # 默认 1GB
    MAX_AVATAR_SIZE = int(os.environ.get('MAX_AVATAR_SIZE', 5 * 1024 * 1024))  # 默认 5MB
    
    return {
        'UPLOAD_FOLDER': UPLOAD_FOLDER,
        'AVATAR_FOLDER': AVATAR_FOLDER,
        'ALLOWED_EXTENSIONS': [ext.strip() for ext in ALLOWED_EXTENSIONS],
        'ALLOWED_IMAGE_EXTENSIONS': [ext.strip() for ext in ALLOWED_IMAGE_EXTENSIONS],
        'MAX_CONTENT_LENGTH': MAX_CONTENT_LENGTH,
        'MAX_AVATAR_SIZE': MAX_AVATAR_SIZE
    }


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def ensure_upload_directories(upload_folder, avatar_folder):
    """确保上传目录及其子目录存在"""
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(avatar_folder, exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'videos'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
