"""
进步追踪相关路由模块
处理舞者进步记录查询等 API 端点
"""
from flask import Blueprint, request, jsonify

from models import db, Dancer, ProgressRecord, Video, User
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


@progress_bp.route('/progress/<int:user_id>', methods=['GET'])
@token_required
def get_progress(user_id):
    """获取用户的进步追踪数据 - 仅返回前端必要字段"""
    current_user = request.current_user
    
    # 查找用户并验证权限
    user = User.query.get_or_404(user_id)
    
    # 权限验证：普通用户只能查看自己的进步记录，管理员可以查看任何记录
    if not current_user.get('is_admin', False) and user.id != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own progress.'}), 403
    
    # 获取该用户的所有视频及其分析结果
    videos = Video.query.filter_by(user_id=user_id).order_by(Video.upload_date.desc()).all()
    
    # 构建精简的视频列表，只包含前端必要字段
    videos_data = []
    for v in videos:
        video_data = {
            'id': v.id,
            'title': v.title,
            'upload_date': v.upload_date.isoformat() if v.upload_date else None,
            'dance_style': v.dance_style,
            'overall_score': None
        }
        
        # 提取分析结果中的关键分数
        if v.analyses and len(v.analyses) > 0 and v.analyses[0].result_data:
            result_data = v.analyses[0].result_data
            video_data['overall_score'] = result_data.get('overall_score', 0)
            # 提取各项能力分数供雷达图使用
            video_data['technique_score'] = result_data.get('technique_score', 0)
            video_data['rhythm_score'] = result_data.get('rhythm_score', 0)
            video_data['expression_score'] = result_data.get('expression_score', 0)
            video_data['completeness_score'] = result_data.get('completeness_score', 0)
        
        videos_data.append(video_data)
    
    # 计算已分析视频数量和最新分数
    analyzed_videos = [v for v in videos_data if v['overall_score'] is not None]
    analyzed_count = len(analyzed_videos)
    latest_score = analyzed_videos[-1]['overall_score'] if analyzed_videos else 0
    
    # 计算进步幅度（计算最新两次的分数差）
    improvement = 0
    if len(analyzed_videos) >= 2:
        latest_score = analyzed_videos[0]['overall_score'] or 0
        previous_score = analyzed_videos[1]['overall_score'] or 0
        improvement = round(latest_score - previous_score, 1)

    return jsonify({
        'videos': videos_data,
        'analyzedCount': analyzed_count,
        'latestScore': latest_score,
        'improvement': improvement
    })
