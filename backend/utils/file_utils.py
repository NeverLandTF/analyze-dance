"""
文件工具模块
提供文件上传相关的辅助功能
"""
import os
import subprocess
import tempfile


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


def extract_video_thumbnail(video_path, thumbnail_path, frame_time=1):
    """
    使用 ffmpeg 提取视频缩略图（默认取第 1 秒的帧）
    
    Args:
        video_path: 视频文件路径
        thumbnail_path: 缩略图保存路径
        frame_time: 提取第几秒的帧，默认 1 秒
    
    Returns:
        bool: 是否成功生成缩略图
    """
    try:
        # 使用 ffmpeg 提取指定时间的帧作为缩略图
        cmd = [
            'ffmpeg',
            '-ss', str(frame_time),  # 跳转到指定时间
            '-i', video_path,        # 输入文件
            '-vframes', '1',         # 只输出 1 帧
            '-vf', 'scale=320:-1',   # 缩放宽度为 320px，高度自动保持比例
            '-y',                    # 覆盖已存在的文件
            thumbnail_path           # 输出文件
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Thumbnail extraction timed out")
        return False
    except Exception as e:
        print(f"Error extracting thumbnail: {e}")
        return False


def extract_video_frames(video_path, output_dir, num_frames=8):
    """
    使用 ffmpeg 从视频中提取多帧图片，用于大模型视频分析
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出图片的目录
        num_frames: 提取的帧数，默认 8 帧
    
    Returns:
        list: 生成的图片文件路径列表，按时间顺序排列
    """
    try:
        # 首先获取视频时长
        duration = get_video_duration(video_path)
        if not duration or duration <= 0:
            print("无法获取视频时长")
            return []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 计算帧间隔时间，均匀分布在整个视频中
        # 从视频的 10% 处开始，到 90% 处结束，避免开头和结尾的黑屏
        start_time = duration * 0.1
        end_time = duration * 0.9
        interval = (end_time - start_time) / (num_frames - 1) if num_frames > 1 else 0
        
        frame_paths = []
        
        for i in range(num_frames):
            # 计算当前帧的时间点
            if num_frames == 1:
                frame_time = duration / 2
            else:
                frame_time = start_time + (i * interval)
            
            # 生成唯一的文件名
            frame_filename = f"frame_{i:03d}_{int(frame_time * 1000):06d}ms.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            
            # 使用 ffmpeg 提取指定时间的帧
            cmd = [
                'ffmpeg',
                '-ss', str(frame_time),
                '-i', video_path,
                '-vframes', '1',
                '-vf', 'scale=1280:-1',  # 较高的分辨率以便大模型分析
                '-y',
                frame_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(frame_path):
                frame_paths.append(frame_path)
            else:
                print(f"Failed to extract frame at {frame_time}s: {result.stderr}")
        
        return frame_paths
        
    except subprocess.TimeoutExpired:
        print("Frame extraction timed out")
        return []
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []


def get_video_duration(video_path):
    """
    使用 ffprobe 获取视频时长（秒）
    
    Args:
        video_path: 视频文件路径
    
    Returns:
        float: 视频时长（秒），失败返回 None
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
        else:
            print(f"FFprobe error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Duration check timed out")
        return None
    except ValueError as e:
        print(f"Error parsing duration: {e}")
        return None
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None
