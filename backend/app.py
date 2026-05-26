"""
Dance Analysis Backend Application
舞蹈分析后端应用 - 模块化版本
"""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os

from models import db
from utils import get_upload_config, ensure_upload_directories
from routes import user_bp, video_bp, analysis_bp, progress_bp, file_bp


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    CORS(app)
    
    # 获取上传配置
    upload_config = get_upload_config(app)
    
    # 数据库配置 - 从环境变量获取
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/dance_analysis_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 上传配置
    app.config['UPLOAD_FOLDER'] = upload_config['UPLOAD_FOLDER']
    app.config['AVATAR_FOLDER'] = upload_config['AVATAR_FOLDER']
    app.config['MAX_CONTENT_LENGTH'] = upload_config['MAX_CONTENT_LENGTH']
    app.config['ALLOWED_EXTENSIONS'] = upload_config['ALLOWED_EXTENSIONS']
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = upload_config['ALLOWED_IMAGE_EXTENSIONS']
    app.config['MAX_AVATAR_SIZE'] = upload_config['MAX_AVATAR_SIZE']
    
    # 确保上传目录及其子目录存在
    ensure_upload_directories(upload_config['UPLOAD_FOLDER'], upload_config['AVATAR_FOLDER'])
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(file_bp)
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 生产环境使用 Gunicorn 启动，不需要 debug 模式
    # 开发环境下可以运行此脚本
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    if debug_mode:
        app.run(debug=True, host=host, port=port)
    else:
        print('Production mode: Use Gunicorn to start the application')
