"""
AI 分析服务模块
使用 OpenAI 兼容 API 对接阿里云 DashScope 大模型
"""
import os
from typing import Dict, Any, Optional, Tuple, List
from flask import current_app
from openai import OpenAI


def get_ai_config(app=None):
    """从应用配置或环境变量获取 AI 服务配置（与 file_utils 风格一致）"""
    if app is not None:
        # 优先从 Flask 应用配置获取
        return {
            'AI_API_BASE_URL': app.config.get(
                'AI_API_BASE_URL',
                os.environ.get('AI_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
            ),
            'AI_API_KEY': app.config.get(
                'AI_API_KEY',
                os.environ.get('AI_API_KEY', '')
            ),
            'AI_MODEL_NAME': app.config.get(
                'AI_MODEL_NAME',
                os.environ.get('AI_MODEL_NAME', 'qwen-vl-max-latest')
            ),
            'AI_VIDEO_FRAMES_COUNT': app.config.get(
                'AI_VIDEO_FRAMES_COUNT',
                os.environ.get('AI_VIDEO_FRAMES_COUNT', '8')
            )
        }
    
    # 如果未传入 app，直接从环境变量获取
    return {
        'AI_API_BASE_URL': os.environ.get(
            'AI_API_BASE_URL',
            'https://dashscope.aliyuncs.com/compatible-mode/v1'
        ),
        'AI_API_KEY': os.environ.get('AI_API_KEY', ''),
        'AI_MODEL_NAME': os.environ.get('AI_MODEL_NAME', 'qwen-vl-max-latest'),
        'AI_VIDEO_FRAMES_COUNT': int(os.environ.get('AI_VIDEO_FRAMES_COUNT', '8'))
    }


class AIAnalysisService:
    """AI 分析服务类，封装与大模型的交互"""
    
    def __init__(self, config=None):
        # 从配置字典或环境变量获取 API 设置
        if config is None:
            config = get_ai_config()
        
        self.api_base_url = config.get('AI_API_BASE_URL')
        self.api_key = config.get('AI_API_KEY')
        self.model_name = config.get('AI_MODEL_NAME')
        self.video_frames_count = config.get('AI_VIDEO_FRAMES_COUNT', 8)
        
        # 初始化 OpenAI 客户端（兼容 DashScope）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base_url
        )
    
    def analyze_video(self, video_url: str, dance_style: str = "", subject_description: str = None) -> Dict[str, Any]:
        """
        分析舞蹈视频并返回结构化结果
        
        Args:
            video_url: 视频的完整 URL
            dance_style: 舞蹈风格（如 breaking, popping, locking 等）
            subject_description: 人物主体描述（多人视频时使用，用于区分视频中的其他人）
            
        Returns:
            包含分析结果的字典，格式为：
            {
                'analysis': {...},  # 分析结果
                'usage': {...}      # token 使用量信息
            }
        """
        if not self.api_key:
            raise ValueError("AI API Key 未配置，请设置 AI_API_KEY 环境变量")
        
        # 调用大模型 API 进行分析，直接传入视频 URL
        response_data, usage_info = self._call_llm_api_with_video_url(video_url, dance_style, subject_description)
        
        # 解析并结构化返回结果
        analysis_result = self._parse_analysis_result(response_data)
        
        # 返回分析结果和 token 使用量
        return {
            'analysis': analysis_result,
            'usage': usage_info
        }
    
    def analyze_video_with_description(self, video_description: str, dance_style: str = "") -> Dict[str, Any]:
        """
        （降级方案）基于视频描述进行分析，当无法处理实际视频时使用
        
        Args:
            video_description: 视频描述或内容说明
            dance_style: 舞蹈风格（如 breaking, popping, locking 等）
            
        Returns:
            包含分析结果的字典，格式为：
            {
                'analysis': {...},  # 分析结果
                'usage': {...}      # token 使用量信息
            }
        """
        if not self.api_key:
            raise ValueError("AI API Key 未配置，请设置 AI_API_KEY 环境变量")
        
        # 构建提示词
        prompt = self._build_analysis_prompt(video_description, dance_style)
        
        # 调用大模型 API
        response_data, usage_info = self._call_llm_api(prompt)
        
        # 解析并结构化返回结果
        analysis_result = self._parse_analysis_result(response_data)
        
        # 返回分析结果和 token 使用量
        return {
            'analysis': analysis_result,
            'usage': usage_info
        }
    
    def generate_subject_description(self, image_url: str) -> str:
        """
        根据框选帧图片生成主体人物描述，用于区分视频中的其他人
        
        Args:
            image_url: 图片的完整 URL 或路径
            
        Returns:
            人物主体描述文本
        """
        if not self.api_key:
            raise ValueError("AI API Key 未配置，请设置 AI_API_KEY 环境变量")
        
        # 构建消息内容，使用 image_url 格式传入图片
        content_items = [
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            },
            {
                "type": "text",
                "text": """# Role
你是一个高精度的图像分析与特征提取专家。

# Task
请仔细观察输入的图像。图像中有多个人物，其中有一个人被【绿色方框】框选。请提供详细的文字描述，将这个被绿框框选的人物与图中的其他人清晰地推导并区分开。

# Requirements
请严格按照以下结构输出描述，确保语言简练、客观：

1. **基本特征定位**：
   - 说明该目标人物在画面中的大致位置（例如：画面中央、左侧前景、后排右起第二位等）。
   - 估计其性别倾向、年龄段或角色（如：儿童、青年、老年、医护人员等）。

2. **视觉特征细节**：
   - **头部/面部**：发型、发色、是否佩戴眼镜/帽子/口罩、面部表情或视线方向。
   - **衣着/装扮**：上衣与下装的款式、颜色、材质或图案细节，以及鞋子、背包等配饰。
   - **姿态/动作**：此人正在做什么（例如：站立、奔跑、看手机、向右侧侧身等）。

3. **关键区分特征（最重要）**：
   - 指出一到两个最能将此人与周围其他人区别开的特征。例如：“他是周围人中唯一穿着长袖的”、“相比旁边穿黑衣的人，他是唯一穿白衣的”或“他的身高明显高于左侧的人”。

# Constraints
- 仅关注【绿色方框】内的人物，请勿混淆其他颜色方框（如有）或其他未框选的人物。
- 描述必须基于图像中的事实，避免主观臆测（如“他看起来很开心”请描述为“面带微笑”）。
- 如果绿框内有部分细节因遮挡或模糊无法看清，请如实指出，不要编造。"""
            }
        ]
        
        try:
            # 使用 OpenAI SDK 调用
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': content_items
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # 返回模型响应内容
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            raise Exception(f"调用 AI API 生成人物描述失败：{str(e)}")
    
    def _build_analysis_prompt(self, video_description: str, dance_style: str) -> str:
        """构建分析提示词"""
        style_info = f"，舞蹈风格为 {dance_style}" if dance_style else ""
        
        prompt = f"""你是一位专业的舞蹈分析专家。请对以下舞蹈视频进行详细分析{style_info}。

视频内容描述：{video_description}

请从以下几个方面进行分析：
1. 姿态检测 (pose_detection): 评估舞者的基本姿态、身体对齐情况
2. 动作质量 (movement_quality): 包括节奏感、流畅度、力量控制、柔韧性等
3. 技术要点：指出做得好的地方和需要改进的地方
4. 综合评分：给出 0-100 的综合评分
5. 具体建议：给出针对性的训练建议

请以 JSON 格式返回分析结果，格式如下：
{{
    "pose_detection": {{
        "confidence": 0.95,
        "keypoints": ["头部稳定", "脊柱对齐良好", "四肢伸展充分"],
        "issues": []
    }},
    "movement_quality": {{
        "score": 85.5,
        "rhythm": 88,
        "flow": 82,
        "power": 85,
        "flexibility": 80,
        "feedback": "具体的反馈意见"
    }},
    "technical_analysis": {{
        "strengths": ["优点 1", "优点 2"],
        "areas_to_improve": ["需要改进的方面 1", "需要改进的方面 2"]
    }},
    "overall_score": 85,
    "technique_score": 85,
    "rhythm_score": 88,
    "expression_score": 82,
    "completeness_score": 85,
    "strengths": ["姿态稳定", "节奏感好"],
    "improvements": ["动作连贯性", "表情管理"],
    "movements": [
        {{
            "name": "动作名称",
            "timestamp": 30.5,
            "quality": "优秀",
            "comment": "动作点评"
        }}
    ],
    "suggestions": ["建议多加练习基本功", "注意动作之间的过渡"],
    "summary": "综合评价总结"
}}

请确保返回有效的 JSON 格式，不要包含其他解释性文字。"""
        
        return prompt
    
    def _call_llm_api_with_video_url(self, video_url: str, dance_style: str, subject_description: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        调用大模型 API，直接传入视频 URL
        
        Args:
            video_url: 视频的完整 URL
            dance_style: 舞蹈风格
            subject_description: 人物主体描述（多人视频时使用，用于区分视频中的其他人）
            
        Returns:
            (模型返回的文本内容，token 使用量信息)
        """
        # 构建消息内容，包含视频 URL 和文本
        content_items = []
        
        # 根据示例代码，使用视频 URL 的方式传入
        content_items.append({
            "type": "video_url",
            "video_url": {
                "url": video_url,
                "fps": 2  # 指定采样帧率，默认为 2fps
            }
        })
        
        # 添加文本提示
        style_info = f"，舞蹈风格为 {dance_style}" if dance_style else ""
        
        # 如果是多人视频且提供了主体描述，加入到提示词中
        subject_info = ""
        if subject_description:
            subject_info = f"\n\n【重要】视频中有多人，以下是需要分析的主体人物的详细描述：\n{subject_description}\n\n请重点关注并仅分析上述描述的人物，忽略视频中的其他人。"
        
        prompt_text = f"""你是一位专业的舞蹈分析专家。请分析这个舞蹈视频{style_info}。
{subject_info}
请从以下几个方面进行详细分析：
1. 姿态检测 (pose_detection): 评估舞者的基本姿态、身体对齐情况
2. 动作质量 (movement_quality): 包括节奏感、流畅度、力量控制、柔韧性等
3. 技术要点：指出做得好的地方和需要改进的地方
4. 综合评分：给出 0-100 的综合评分
5. 具体建议：给出针对性的训练建议

请以 JSON 格式返回分析结果，格式如下：
{{
    "pose_detection": {{
        "confidence": 0.95,
        "keypoints": ["头部稳定", "脊柱对齐良好", "四肢伸展充分"],
        "issues": []
    }},
    "movement_quality": {{
        "score": 85.5,
        "rhythm": 88,
        "flow": 82,
        "power": 85,
        "flexibility": 80,
        "feedback": "具体的反馈意见"
    }},
    "technical_analysis": {{
        "strengths": ["优点 1", "优点 2"],
        "areas_to_improve": ["需要改进的方面 1", "需要改进的方面 2"]
    }},
    "overall_score": 85,
    "technique_score": 85,
    "rhythm_score": 88,
    "expression_score": 82,
    "completeness_score": 85,
    "strengths": ["姿态稳定", "节奏感好"],
    "improvements": ["动作连贯性", "表情管理"],
    "movements": [
        {{
            "name": "动作名称",
            "timestamp": 30.5,
            "quality": "优秀",
            "comment": "动作点评"
        }}
    ],
    "suggestions": ["建议多加练习基本功", "注意动作之间的过渡"],
    "summary": "综合评价总结"
}}

请确保返回有效的 JSON 格式，不要包含其他解释性文字。"""
        
        content_items.append({
            "type": "text",
            "text": prompt_text
        })
        
        try:
            # 使用 OpenAI SDK 调用
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': content_items
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 提取 token 使用量信息
            usage_info = {}
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                    'model': self.model_name
                }
            
            # 返回模型响应内容和 token 使用量
            return response.choices[0].message.content, usage_info
                
        except Exception as e:
            raise Exception(f"调用 AI API 失败：{str(e)}")
    
    def _call_llm_api_with_frames(self, frame_paths: List[str], dance_style: str) -> Tuple[str, Dict[str, Any]]:
        """
        （已废弃）调用大模型 API，传入视频帧图片
        保留此方法以兼容旧版本，现在直接使用视频 URL
        
        Args:
            frame_paths: 视频帧图片路径列表
            dance_style: 舞蹈风格
            
        Returns:
            (模型返回的文本内容，token 使用量信息)
        """
        # 为了向后兼容，将帧路径转换为 URL 形式调用新方法
        # 注意：这个方法不再被使用，建议直接使用 _call_llm_api_with_video_url
        raise NotImplementedError("此方法已废弃，请直接使用视频 URL 方式调用")
    
    def _call_llm_api(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        调用大模型 API（纯文本方式，用于降级方案）
        
        Args:
            prompt: 提示词
            
        Returns:
            (模型返回的文本内容，token 使用量信息)
        """
        try:
            # 使用 OpenAI SDK 调用
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一位专业的舞蹈分析专家，擅长分析舞蹈动作、姿态和技术细节。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 提取 token 使用量信息
            usage_info = {}
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                    'model': self.model_name
                }
            
            # 返回模型响应内容和 token 使用量
            return response.choices[0].message.content, usage_info
                
        except Exception as e:
            raise Exception(f"调用 AI API 失败：{str(e)}")
    
    def _parse_analysis_result(self, response_text: str) -> Dict[str, Any]:
        """
        解析模型返回的结果
        
        Args:
            response_text: 模型返回的文本
            
        Returns:
            结构化的分析结果字典
        """
        import json
        import re
        
        # 尝试提取 JSON 内容（可能包含在代码块中）
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 如果没有代码块标记，尝试直接解析整个响应
            json_str = response_text.strip()
        
        try:
            result = json.loads(json_str)
            
            # 确保返回格式符合预期，并映射到前端期望的字段名
            technical_analysis = result.get('technical_analysis', {})
            movement_quality = result.get('movement_quality', {})
            
            formatted_result = {
                'pose_detection': result.get('pose_detection', {
                    'confidence': 0.8,
                    'keypoints': [],
                    'issues': []
                }),
                'movement_quality': movement_quality,
                'comparison_with_previous': {
                    'improvement': 'N/A',
                    'areas_to_focus': technical_analysis.get('areas_to_improve', [])
                },
                'technical_analysis': technical_analysis,
                # 映射到前端期望的字段名：优先使用 AI 直接返回的字段，如果没有则从嵌套结构映射
                'overall_score': result.get('overall_score', 75),
                'technique_score': result.get('technique_score', movement_quality.get('score', 75)),
                'rhythm_score': result.get('rhythm_score', movement_quality.get('rhythm', 75)),
                'expression_score': result.get('expression_score', movement_quality.get('flow', 75)),
                'completeness_score': result.get('completeness_score', movement_quality.get('power', 75)),
                # 映射 strengths 和 improvements：优先使用顶层字段
                'strengths': result.get('strengths', technical_analysis.get('strengths', [])),
                'improvements': result.get('improvements', technical_analysis.get('areas_to_improve', [])),
                # 添加 movements 和 suggestions（如果 AI 返回的话）
                'movements': result.get('movements', []),
                'suggestions': result.get('suggestions', []),
                'summary': result.get('summary', '')
            }
            
            return formatted_result
            
        except json.JSONDecodeError as e:
            # 如果解析失败，返回默认结果（包含前端期望的所有字段）
            return {
                'pose_detection': {
                    'confidence': 0.8,
                    'keypoints': [],
                    'issues': []
                },
                'movement_quality': {
                    'score': 75.0,
                    'feedback': f'分析结果解析失败：{str(e)}'
                },
                'comparison_with_previous': {
                    'improvement': 'N/A',
                    'areas_to_focus': []
                },
                'technical_analysis': {
                    'strengths': [],
                    'areas_to_improve': []
                },
                'overall_score': 75,
                'technique_score': 75,
                'rhythm_score': 75,
                'expression_score': 75,
                'completeness_score': 75,
                'strengths': [],
                'improvements': [],
                'movements': [],
                'suggestions': [],
                'summary': response_text[:500]  # 返回原始响应的部分内容
            }


# 全局服务实例
_ai_service_instance = None


def get_ai_service() -> AIAnalysisService:
    """获取 AI 分析服务单例实例"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIAnalysisService()
    return _ai_service_instance
