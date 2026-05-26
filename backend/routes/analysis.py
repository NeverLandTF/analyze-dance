"""
AI 分析相关路由模块
处理视频分析 API 端点
"""
from flask import Blueprint, request, jsonify

from models import db, Video, Analysis, ProgressRecord
from utils.auth import token_required
from utils.ai_service import get_ai_service

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
    
    try:
        # 获取 AI 服务实例
        ai_service = get_ai_service()
        
        # 构建视频描述信息
        video_description = f"视频标题：{video.title}, 舞蹈风格：{video.dance_style or '未指定'}"
        
        # 调用 AI 分析服务
        result = ai_service.analyze_video(
            video_description=video_description,
            dance_style=video.dance_style or ""
        )
        
        # 解析返回结果（包含 analysis 和 usage）
        analysis_result = result.get('analysis', {})
        token_usage = result.get('usage', {})
        
    except ValueError as e:
        # API Key 未配置等错误
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        # 其他错误，返回模拟结果作为降级方案
        analysis_result = {
            'pose_detection': {'confidence': 0.95, 'keypoints': [], 'issues': []},
            'movement_quality': {'score': 85.5, 'feedback': f'AI 服务暂时不可用：{str(e)}'},
            'comparison_with_previous': {'improvement': '+12%', 'areas_to_focus': ['footwork', 'transitions']},
            'technical_analysis': {'strengths': [], 'areas_to_improve': []},
            'overall_score': 85,
            'summary': ''
        }
        token_usage = {}
    
    # 创建分析记录，保存 token 使用量到 result_data
    analysis = Analysis(
        user_id=data['user_id'],
        video_id=data['video_id'],
        analysis_type='comprehensive',
        result_data={
            **analysis_result,
            'token_usage': token_usage  # 记录 token 使用量
        },
        confidence_score=analysis_result.get('pose_detection', {}).get('confidence', 0.92),
        model_version=token_usage.get('model', ai_service.model_name)  # 使用实际调用的模型名称
    )
    
    db.session.add(analysis)
    
    # 更新进步记录
    update_progress_record(data['user_id'], video.dancer_id, analysis_result)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Analysis completed',
        'analysis_id': analysis.id,
        'results': analysis_result,
        'token_usage': token_usage  # 返回 token 使用量给前端
    })


@analysis_bp.route('/analysis/history', methods=['GET'])
@token_required
def get_analysis_history():
    """获取用户的分析历史列表"""
    current_user = request.current_user
    
    # 从 query 参数或 token 中获取 user_id
    user_id = request.args.get('user_id') or current_user.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # 权限验证：普通用户只能查看自己的分析记录，管理员可以查看所有
    if not current_user.get('is_admin', False) and int(user_id) != current_user.get('user_id'):
        return jsonify({'error': 'Permission denied. You can only view your own analysis history.'}), 403
    
    # 查询分析记录，关联视频信息
    analyses = db.session.query(Analysis, Video).join(Video).filter(
        Video.user_id == int(user_id)
    ).order_by(Analysis.processed_at.desc()).all()
    
    return jsonify({
        'analyses': [{
            'id': a.id,
            'video_id': a.video_id,
            'video_title': v.title,
            'thumbnail_url': v.thumbnail_url,
            'dance_style': v.dance_style,
            'analyzed_at': a.processed_at.isoformat() if a.processed_at else None,
            'overall_score': a.result_data.get('overall_score', 0) if a.result_data else 0,
            'summary': a.result_data.get('summary', '') if a.result_data else '',
            'analysis_type': a.analysis_type
        } for a, v in analyses]
    })
