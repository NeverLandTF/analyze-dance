"""
JWT 认证工具模块
提供 token 生成、验证和装饰器功能
"""
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from flask import request, jsonify

# JWT 配置
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'your-secret-key-here'))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))


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
