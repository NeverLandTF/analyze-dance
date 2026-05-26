"""
AI 分析相关路由模块
处理视频分析 API 端点
"""
from flask import Blueprint, request, jsonify

from models import db, Video, Analysis, ProgressRecord
from utils.auth import token_required

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')


def update_progress_record(user_id, dancer_id, analysis_result):
    """更新舞者进步记录"""
    movement_quality = analysis_result.get('movement_quality', {})
    
    progress = ProgressRecord(
        dancer_id=dancer_id,
        skill_category='overall',
        score=movement_quality.get('score', 0),
        improvement_rate=12.0,  # 从对比结果中提取
        feedback=movement_quality.get('feedback', ''),
        comparison_video_ids=[]
    )
    
    db.session.add(progress)


@analysis_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_video():
    """触发 AI 视频分析"""
    data = request.get_json()
    
    if not data or not data.get('video_id') or not data.get('user_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    video = Video.query.get(data['video_id'])
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # 模拟 AI 分析结果 - 实际项目中应调用大模型 API
    analysis_result = {
        'pose_detection': {'confidence': 0.95, 'keypoints': []},
        'movement_quality': {'score': 85.5, 'feedback': 'Good rhythm, improve flexibility'},
        'comparison_with_previous': {'improvement': '+12%', 'areas_to_focus': ['footwork', 'transitions']}
    }
    
    analysis = Analysis(
        user_id=data['user_id'],
        video_id=data['video_id'],
        analysis_type='comprehensive',
        result_data=analysis_result,
        confidence_score=0.92,
        model_version='v2.1'
    )
    
    db.session.add(analysis)
    
    # 更新进步记录
    update_progress_record(data['user_id'], video.dancer_id, analysis_result)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Analysis completed',
        'analysis_id': analysis.id,
        'results': analysis_result
    })
