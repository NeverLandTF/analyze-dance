"""
进步追踪相关路由模块
处理舞者进步记录查询等 API 端点
"""
from flask import Blueprint, request, jsonify

from models import db, Dancer, ProgressRecord
from utils.auth import token_required

progress_bp = Blueprint('progress', __name__, url_prefix='/api')


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


@progress_bp.route('/progress/<int:dancer_id>', methods=['GET'])
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
