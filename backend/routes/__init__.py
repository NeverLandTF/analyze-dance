"""
路由模块初始化
"""
from .users import user_bp
from .videos import video_bp
from .analysis import analysis_bp
from .progress import progress_bp
from .files import file_bp

__all__ = [
    'user_bp',
    'video_bp',
    'analysis_bp',
    'progress_bp',
    'file_bp'
]
