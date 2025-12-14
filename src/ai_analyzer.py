"""AI 内容分析和总结服务"""
import os
import json
from typing import List, Dict, Any, Optional
import logging


class AIAnalyzer:
    """AI 内容分析器 - 支持多种 AI 服务"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 AI 分析器

        Args:
            api_key: API 密钥（如果为空，从环境变量读取）
            api_base: API 基础 URL（可选，用于自定义端点）
            model: 使用的模型名称
            logger: 日志记录器
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('AI_API_KEY')
        self.api_base = api_base or os.getenv('OPENAI_API_BASE') or os.getenv('AI_API_BASE')
        self.model = model or os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        self.logger = logger or logging.getLogger(__name__)

        # 检查是否配置了 API
        self.enabled = bool(self.api_key)
        if not self.enabled:
            self.logger.warning("未配置 AI API 密钥，将使用简单文本提取")

    async def summarize_topic(self, topic: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        使用 AI 总结帖子内容

        Args:
            topic: 帖子元信息（标题、作者等）
            content: 帖子内容

        Returns:
            总结结果字典，包含：
            - summary: 内容摘要
            - key_points: 关键点列表
            - tags: 主题标签
            - sentiment: 情感倾向
        """
        if not self.enabled:
            return self._simple_summary(content)

        try:
            # 导入 OpenAI 库
            try:
                import openai
            except ImportError:
                self.logger.warning("未安装 openai 库，将使用简单文本提取")
                return self._simple_summary(content)

            # 配置 OpenAI
            if self.api_base:
                openai.api_base = self.api_base
            openai.api_key = self.api_key

            # 构建提示词
            prompt = self._build_summary_prompt(topic, content)

            # 调用 AI 模型
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容分析助手，擅长提炼文章要点和识别关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # 解析响应
            result_text = response.choices[0].message.content.strip()
            return self._parse_ai_response(result_text)

        except Exception as e:
            self.logger.error(f"AI 总结失败: {str(e)}")
            return self._simple_summary(content)

    async def analyze_interests(
        self,
        topics: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        分析并推荐用户可能感兴趣的话题

        Args:
            topics: 帖子列表
            user_profile: 用户兴趣画像（可选）

        Returns:
            按相关度排序的帖子列表，每个帖子包含：
            - 原始信息
            - relevance_score: 相关度分数
            - reason: 推荐理由
        """
        if not self.enabled:
            # 简单按回复数和浏览数排序
            return self._simple_ranking(topics)

        try:
            import openai

            if self.api_base:
                openai.api_base = self.api_base
            openai.api_key = self.api_key

            # 构建分析提示词
            prompt = self._build_interest_prompt(topics, user_profile)

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个内容推荐专家，擅长分析用户兴趣并推荐相关内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )

            result_text = response.choices[0].message.content.strip()
            return self._parse_recommendations(result_text, topics)

        except Exception as e:
            self.logger.error(f"AI 兴趣分析失败: {str(e)}")
            return self._simple_ranking(topics)

    def _build_summary_prompt(self, topic: Dict[str, Any], content: str) -> str:
        """构建总结提示词"""
        return f"""请分析以下 Linux.do 论坛帖子，并提供结构化的总结：

标题：{topic.get('title', '')}
作者：{topic.get('author', '')}
分类：{topic.get('category', '')}
回复数：{topic.get('replies', '0')}
浏览数：{topic.get('views', '0')}

内容：
{content[:2000]}

请以 JSON 格式返回分析结果，包含以下字段：
{{
  "summary": "一句话总结（50字以内）",
  "key_points": ["关键点1", "关键点2", "关键点3"],
  "tags": ["标签1", "标签2", "标签3"],
  "sentiment": "positive/neutral/negative",
  "category": "技术讨论/求助/分享/其他"
}}"""

    def _build_interest_prompt(
        self,
        topics: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]]
    ) -> str:
        """构建兴趣分析提示词"""
        topics_text = "\n\n".join([
            f"{i+1}. 【{t.get('category', '')}】{t.get('title', '')}\n"
            f"   作者: {t.get('author', '')} | 回复: {t.get('replies', '0')} | 浏览: {t.get('views', '0')}\n"
            f"   摘要: {t.get('content_summary', {}).get('first_post', '')[:200]}"
            for i, t in enumerate(topics[:20])  # 最多分析20个
        ])

        profile_text = ""
        if user_profile:
            profile_text = f"\n用户兴趣画像：{json.dumps(user_profile, ensure_ascii=False)}\n"

        return f"""请分析以下 Linux.do 论坛帖子列表，为用户推荐最相关和有价值的内容。
{profile_text}
帖子列表：
{topics_text}

请以 JSON 数组格式返回推荐结果，每个推荐包含：
{{
  "index": 帖子序号（从1开始）,
  "relevance_score": 相关度分数（0-100）,
  "reason": "推荐理由（30字以内）",
  "tags": ["关键词1", "关键词2"]
}}

只返回相关度分数 > 60 的帖子，按分数降序排列。"""

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # 解析失败，返回默认结构
        return {
            "summary": response_text[:200] if response_text else "",
            "key_points": [],
            "tags": [],
            "sentiment": "neutral",
            "category": "其他"
        }

    def _parse_recommendations(
        self,
        response_text: str,
        topics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """解析推荐结果"""
        try:
            import re
            # 尝试提取 JSON 数组
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                recommendations = json.loads(json_match.group())

                # 关联推荐信息到帖子
                result = []
                for rec in recommendations:
                    index = rec.get('index', 0) - 1
                    if 0 <= index < len(topics):
                        topic = topics[index].copy()
                        topic['relevance_score'] = rec.get('relevance_score', 0)
                        topic['recommendation_reason'] = rec.get('reason', '')
                        topic['recommendation_tags'] = rec.get('tags', [])
                        result.append(topic)

                return result
        except Exception as e:
            self.logger.error(f"解析推荐结果失败: {str(e)}")

        # 解析失败，返回简单排序
        return self._simple_ranking(topics)

    def _simple_summary(self, content: str) -> Dict[str, Any]:
        """简单文本摘要（不使用 AI）"""
        return {
            "summary": content[:150] + "..." if len(content) > 150 else content,
            "key_points": [],
            "tags": [],
            "sentiment": "neutral",
            "category": "其他"
        }

    def _simple_ranking(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """简单排序（不使用 AI）"""
        # 按回复数和浏览数的加权分数排序
        def calculate_score(topic):
            try:
                replies = int(str(topic.get('replies', '0')).replace('k', '000').replace('.', ''))
                views = int(str(topic.get('views', '0')).replace('k', '000').replace('.', ''))
                return replies * 2 + views  # 回复权重更高
            except:
                return 0

        sorted_topics = sorted(topics, key=calculate_score, reverse=True)

        # 添加简单的推荐信息
        for i, topic in enumerate(sorted_topics):
            topic['relevance_score'] = max(100 - i * 5, 50)  # 递减分数
            topic['recommendation_reason'] = f"热度排名第 {i+1}"
            topic['recommendation_tags'] = [topic.get('category', '')]

        return sorted_topics
