"""Linux.do 论坛适配器"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base_adapter import BaseAdapter, CheckinResult
from modules.forum.linuxdo.ai_analyzer import AIAnalyzer
import asyncio
from typing import List, Dict, Any, Optional
import os
import json
import hashlib
from datetime import datetime, timedelta


class TopicCache:
    """帖子缓存管理器"""

    def __init__(self, cache_file: str, cache_days: int = 7):
        """初始化缓存管理器"""
        self.cache_file = Path(cache_file)
        self.cache_days = cache_days
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        """加载缓存文件"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                self._clean_expired()
            except Exception:
                self.cache = {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _clean_expired(self):
        """清理过期缓存"""
        expiry_time = datetime.now() - timedelta(days=self.cache_days)
        expired_keys = [
            key for key, value in self.cache.items()
            if datetime.fromisoformat(value.get('cached_at', '2000-01-01')) < expiry_time
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_topic_id(self, topic: Dict[str, Any]) -> str:
        """生成帖子唯一标识"""
        link = topic.get('link', '')
        return hashlib.md5(link.encode()).hexdigest()

    def get(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取缓存的帖子分析结果"""
        topic_id = self.get_topic_id(topic)
        return self.cache.get(topic_id)

    def set(self, topic: Dict[str, Any], analysis: Dict[str, Any]):
        """缓存帖子分析结果"""
        topic_id = self.get_topic_id(topic)
        self.cache[topic_id] = {
            'topic': topic,
            'analysis': analysis,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache()

    def is_cached(self, topic: Dict[str, Any]) -> bool:
        """检查帖子是否已缓存"""
        return self.get_topic_id(topic) in self.cache


class LinuxDoAdapter(BaseAdapter):
    """Linux.do 论坛适配器

    Linux.do 是基于 Discourse 的论坛系统
    支持自动登录、获取最新帖子和热门话题
    """

    # 页面加载超时配置（毫秒）
    PAGE_LOAD_TIMEOUT = 60000
    ELEMENT_WAIT_TIMEOUT = 10000

    def __init__(
        self,
        site_url: str,
        username: str,
        password: str,
        logger=None,
        # 内容获取配置
        latest_limit: int = 20,
        hot_limit: int = 10,
        read_limit: int = 5,
        ai_limit: int = 3,
        enable_scroll_loading: bool = False,
        scroll_times: int = 3,
        scroll_interval: float = 2.0,
        fetch_priority_categories: bool = False,
        # 过滤配置
        exclude_categories: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
        priority_categories: Optional[List[str]] = None,
        min_replies: int = 0,
        min_views: int = 50,
        min_score_for_zero_replies: int = 50,
        # AI 配置
        ai_enabled: bool = True,
        ai_api_key: Optional[str] = None,
        ai_api_base: Optional[str] = None,
        ai_model: str = "qwen-flash",
        ai_temperature: float = 0.7,
        ai_max_tokens: int = 800,
        user_interests: Optional[List[str]] = None
    ):
        """
        初始化 Linux.do 适配器

        Args:
            site_url: 站点 URL
            username: 用户名
            password: 密码
            logger: 日志记录器
            latest_limit: 获取最新帖子数量
            hot_limit: 获取热门帖子数量
            read_limit: 深度阅读帖子数量
            ai_limit: AI 分析帖子数量
            enable_scroll_loading: 是否启用滚动加载
            scroll_times: 滚动次数
            scroll_interval: 滚动间隔（秒）
            fetch_priority_categories: 是否获取优先分类的帖子
            exclude_categories: 排除的分类列表
            exclude_keywords: 排除的关键词列表
            priority_categories: 优先分类列表
            min_replies: 最小回复数
            min_views: 最小浏览数
            min_score_for_zero_replies: 0回复帖子的最小浏览数
            ai_enabled: 是否启用 AI 功能
            ai_api_key: AI API 密钥
            ai_api_base: AI API 端点
            ai_model: AI 模型名称
            ai_temperature: AI 温度参数
            ai_max_tokens: AI 最大生成长度
            user_interests: 用户兴趣列表
        """
        super().__init__(
            site_name="linuxdo",
            site_url=site_url,
            username=username,
            password=password,
            logger=logger
        )

        # 保存内容获取配置
        self.latest_limit = latest_limit
        self.hot_limit = hot_limit
        self.read_limit = read_limit
        self.ai_limit = ai_limit
        self.enable_scroll_loading = enable_scroll_loading
        self.scroll_times = scroll_times
        self.scroll_interval = scroll_interval
        self.fetch_priority_categories = fetch_priority_categories
        self.user_interests = user_interests

        # 保存过滤配置（使用默认值如果未提供）
        self.exclude_categories = set(exclude_categories or [
            '公告', '运营反馈', '站务', 'Announcement', 'Feedback'
        ])
        self.exclude_keywords = exclude_keywords or [
            '社区公约', '抽奖规则', '园丁邀请', '阻断', '戾气',
            '社区规则', '论坛公告', '管理员', '版规', '封禁',
            '人设贴', '水贴', '灌水'
        ]
        self.priority_categories = set(priority_categories or [
            '开发调优', 'Linux', '服务器管理', '自动化运维',
            '工具分享', '教程', '技术讨论', '编程', 'AI',
            '云计算', 'Docker', 'DevOps'
        ])
        self.min_replies = min_replies
        self.min_views = min_views
        self.min_score_for_zero_replies = min_score_for_zero_replies

        # 初始化 AI 分析器（如果启用）
        if ai_enabled:
            # 处理环境变量
            if ai_api_key and ai_api_key.startswith('${') and ai_api_key.endswith('}'):
                env_var = ai_api_key[2:-1]
                ai_api_key = os.getenv(env_var, '')

            self.ai_analyzer = AIAnalyzer(
                api_key=ai_api_key,
                api_base=ai_api_base,
                model=ai_model,
                temperature=ai_temperature,
                max_tokens=ai_max_tokens,
                logger=logger
            )
        else:
            # 创建一个禁用的 AI 分析器
            self.ai_analyzer = AIAnalyzer(api_key=None, logger=logger)

        # 初始化缓存（性能优化）
        cache_dir = PROJECT_ROOT / 'storage' / 'cache'
        cache_file = cache_dir / f'linuxdo_{username}_topics.json'
        self.cache = TopicCache(str(cache_file), cache_days=7)

    def _calculate_topic_score(self, topic: Dict[str, Any]) -> float:
        """
        计算帖子的综合评分

        评分维度：
        1. 基础热度：回复数 + 浏览数
        2. 互动率：回复数/浏览数比例
        3. 优先分类加成
        4. 用户兴趣匹配度
        5. 时效性（如果有时间信息）

        Args:
            topic: 帖子信息

        Returns:
            综合评分（0-100）
        """
        try:
            # 解析数值（处理 k/万等单位）
            def parse_number(value):
                if not value:
                    return 0
                s = str(value).lower()
                # 处理 k 后缀（1k = 1000）
                if 'k' in s:
                    s = s.replace('k', '').replace('.', '')
                    return int(float(s) * 100) if '.' in str(value) else int(s) * 1000
                # 处理万后缀
                if '万' in s:
                    return int(float(s.replace('万', '')) * 10000)
                # 处理小数点（3.5k -> 3500）
                try:
                    return int(float(s))
                except:
                    return 0

            replies = parse_number(topic.get('replies', 0))
            views = parse_number(topic.get('views', 0))
            category = topic.get('category', '')
            title = topic.get('title', '')

            # 1. 基础热度分 (0-40分)
            # 使用对数缩放避免大数字主导
            import math
            heat_score = min(40, (math.log10(replies + 1) * 10 + math.log10(views + 1) * 3))

            # 2. 互动率分 (0-20分)
            # 高互动率说明内容有价值
            interaction_rate = replies / max(views, 1) * 100
            interaction_score = min(20, interaction_rate * 100)

            # 3. 优先分类加成 (0-20分)
            category_score = 0
            if category in self.priority_categories:
                category_score = 20
            elif any(pri_cat in category or pri_cat.lower() in title.lower()
                    for pri_cat in self.priority_categories):
                category_score = 10

            # 4. 用户兴趣匹配度 (0-20分)
            interest_score = 0
            if self.user_interests:
                # 检查标题和分类是否包含用户兴趣关键词
                content_text = f"{title} {category}".lower()
                matches = sum(1 for interest in self.user_interests
                            if interest.lower() in content_text)
                interest_score = min(20, matches * 10)

            # 总分
            total_score = heat_score + interaction_score + category_score + interest_score

            # 存储评分信息用于调试
            topic['_score_details'] = {
                'heat': round(heat_score, 2),
                'interaction': round(interaction_score, 2),
                'category': category_score,
                'interest': interest_score,
                'total': round(total_score, 2)
            }

            return total_score

        except Exception as e:
            self.logger.debug(f"计算评分失败: {str(e)}")
            return 0

    def _filter_quality_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤优质内容，移除站务、公告等无关内容

        使用配置的过滤规则和智能评分系统

        Args:
            topics: 帖子列表

        Returns:
            过滤并排序后的帖子列表
        """
        filtered_topics = []

        for topic in topics:
            title = topic.get('title', '')
            category = topic.get('category', '')

            # 过滤：排除特定分类
            if category in self.exclude_categories:
                self.logger.debug(f"过滤分类 '{category}': {title[:30]}")
                continue

            # 过滤：排除包含特定关键词的帖子
            if any(keyword in title for keyword in self.exclude_keywords):
                self.logger.debug(f"过滤关键词: {title[:30]}")
                continue

            # 过滤：排除低质量帖子
            try:
                def parse_number(value):
                    if not value:
                        return 0
                    s = str(value).lower()
                    if 'k' in s:
                        s = s.replace('k', '').replace('.', '')
                        return int(float(s) * 100) if '.' in str(value) else int(s) * 1000
                    try:
                        return int(float(s))
                    except:
                        return 0

                replies = parse_number(topic.get('replies', '0'))
                views = parse_number(topic.get('views', '0'))

                # 0回复的帖子需要更高的浏览数
                if replies == 0 and views < self.min_score_for_zero_replies:
                    self.logger.debug(f"过滤低质量（0回复，低浏览）: {title[:30]}")
                    continue

                # 普通质量过滤
                if replies < self.min_replies and views < self.min_views:
                    self.logger.debug(f"过滤低质量: {title[:30]}")
                    continue

            except Exception as e:
                self.logger.debug(f"解析数值失败: {str(e)}")
                pass

            # 计算综合评分
            score = self._calculate_topic_score(topic)
            topic['quality_score'] = score

            # 添加优先级标记（向后兼容）
            topic['is_priority'] = category in self.priority_categories or any(
                cat in category or cat.lower() in title.lower()
                for cat in self.priority_categories
            )

            filtered_topics.append(topic)

        # 按综合评分排序（从高到低）
        filtered_topics.sort(key=lambda t: t.get('quality_score', 0), reverse=True)

        self.logger.info(
            f"内容过滤: {len(topics)} -> {len(filtered_topics)} 个帖子 "
            f"(平均评分: {sum(t.get('quality_score', 0) for t in filtered_topics) / max(len(filtered_topics), 1):.1f})"
        )

        return filtered_topics

    async def is_logged_in(self) -> bool:
        """
        检查是否已登录

        Discourse 论坛已登录的特征：
        - 有用户菜单元素
        - URL 不在登录页
        """
        try:
            # 访问首页
            await self.page.goto(self.site_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)  # 等待页面渲染

            # 检查 URL 是否在登录页
            current_url = self.page.url
            if '/login' in current_url or '/signin' in current_url:
                self.logger.debug("URL 在登录页，未登录")
                return False

            # 查找已登录状态的指示器
            logged_in_indicators = [
                '.current-user',  # Discourse 用户菜单
                '.header-dropdown-toggle.current-user',
                'button.icon.btn-flat[aria-label*="用户"]',
                'button[title*="用户菜单"]',
                '.d-header .icons .icon[data-icon="user"]',
                '#current-user',  # 用户 ID
                '.user-menu'  # 用户菜单
            ]

            for selector in logged_in_indicators:
                try:
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state='attached'  # 改为 attached，不要求可见
                    )
                    if element:
                        self.logger.debug(f"找到登录状态指示器: {selector}")
                        return True
                except:
                    continue

            # 检查是否有登录按钮（如果有说明未登录）
            try:
                login_button = await self.page.query_selector('button:has-text("登录"), button:has-text("Login")')
                if login_button:
                    self.logger.debug("检测到登录按钮，未登录")
                    return False
            except:
                pass

            # 最后检查页面内容是否包含已登录关键字
            page_content = await self.page.content()
            if 'current-user' in page_content or 'user-menu' in page_content:
                self.logger.debug("页面内容检测到登录状态")
                return True

            # 如果都没检测到，假设已登录（因为有会话恢复）
            self.logger.debug("无明确登录标识，假设已登录")
            return True

        except Exception as e:
            self.logger.error(f"检查登录状态失败: {str(e)}")
            return False

    async def login(self) -> bool:
        """
        执行登录操作

        Discourse 论坛的登录流程：
        1. 点击登录按钮
        2. 填写用户名/邮箱
        3. 填写密码
        4. 点击登录
        """
        try:
            # 访问首页
            self.logger.info(f"访问首页: {self.site_url}")
            await self.page.goto(self.site_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)

            # 查找并点击登录按钮
            login_selectors = [
                'button:has-text("登录")',
                'button:has-text("Login")',
                '.login-button',
                'header button.login-button'
            ]

            login_clicked = False
            for selector in login_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        self.logger.info(f"点击登录按钮: {selector}")
                        await element.click()
                        login_clicked = True
                        await asyncio.sleep(2)  # 等待登录模态框显示
                        break
                except:
                    continue

            if not login_clicked:
                self.logger.error("未找到登录按钮")
                await self.take_screenshot("login_failed_no_button")
                return False

            await self.take_screenshot("before_login")

            # Discourse 登录表单选择器
            username_selectors = [
                '#login-account-name',  # Discourse 标准
                'input[name="login"]',
                'input[type="text"]',
                'input.username'
            ]

            # 填写用户名/邮箱
            username_filled = False
            for selector in username_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        await element.fill(self.username)
                        self.logger.debug(f"使用选择器填写用户名: {selector}")
                        username_filled = True
                        break
                except:
                    continue

            if not username_filled:
                self.logger.error("无法找到用户名输入框")
                await self.take_screenshot("login_failed_no_username")
                return False

            # 填写密码
            password_selectors = [
                '#login-account-password',  # Discourse 标准
                'input[name="password"]',
                'input[type="password"]',
                'input.password'
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        await element.fill(self.password)
                        self.logger.debug(f"使用选择器填写密码: {selector}")
                        password_filled = True
                        break
                except:
                    continue

            if not password_filled:
                self.logger.error("无法找到密码输入框")
                await self.take_screenshot("login_failed_no_password")
                return False

            # 点击登录按钮
            submit_selectors = [
                '#login-button',  # Discourse 标准
                'button[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("Login")',
                '.login-modal button.btn-primary'
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        await element.click()
                        self.logger.debug(f"点击登录按钮: {selector}")
                        submit_clicked = True
                        break
                except:
                    continue

            if not submit_clicked:
                self.logger.error("无法找到提交按钮")
                await self.take_screenshot("login_failed_no_submit")
                return False

            # 等待登录完成
            await asyncio.sleep(3)
            await self.take_screenshot("after_login")

            # 检查是否登录成功
            is_success = await self.is_logged_in()

            if is_success:
                self.logger.info("登录成功")
                return True
            else:
                self.logger.error("登录可能失败，请检查截图")
                return False

        except Exception as e:
            self.logger.error(f"登录过程出错: {str(e)}")
            await self.take_screenshot("login_exception")
            return False

    async def checkin(self) -> CheckinResult:
        """
        执行签到操作

        混合方案：串行获取列表 + 并发处理内容
        - 串行：获取帖子列表（避免触发限制）
        - 并发：读取帖子内容、AI分析（提速）
        """
        try:
            # 串行获取帖子列表（避免触发限制）
            self.logger.info(f"串行获取帖子列表...")
            self.logger.info(f"  获取最新帖子（{self.latest_limit} 条）...")
            latest_topics_raw = await self.get_latest_topics(limit=self.latest_limit)
            await asyncio.sleep(0.5)  # 请求间隔

            self.logger.info(f"  获取热门帖子（{self.hot_limit} 条）...")
            hot_topics_raw = await self.get_hot_topics(limit=self.hot_limit)
            await asyncio.sleep(0.5)  # 请求间隔

            # 如果启用了优先分类获取，从关注的分类中获取更多帖子
            category_topics_raw = []
            if self.fetch_priority_categories and self.priority_categories:
                self.logger.info(f"  从优先分类获取帖子...")
                for category in list(self.priority_categories)[:2]:  # 限制最多2个分类，避免请求过多
                    try:
                        topics = await self.get_category_topics(category, limit=20)
                        category_topics_raw.extend(topics)
                        await asyncio.sleep(0.5)  # 请求间隔
                    except Exception as e:
                        self.logger.warning(f"从分类 '{category}' 获取失败: {str(e)}")

                self.logger.info(f"  从优先分类获取到 {len(category_topics_raw)} 个帖子")

            # 应用内容过滤
            latest_topics = self._filter_quality_topics(latest_topics_raw)
            hot_topics = self._filter_quality_topics(hot_topics_raw)
            category_topics = self._filter_quality_topics(category_topics_raw) if category_topics_raw else []

            self.logger.info(f"✓ 最新帖子: {len(latest_topics)} 个")
            self.logger.info(f"✓ 热门帖子: {len(hot_topics)} 个")
            if category_topics:
                self.logger.info(f"✓ 分类帖子: {len(category_topics)} 个")

            # 合并所有帖子并去重
            all_topics_raw = latest_topics + hot_topics + category_topics
            seen = set()
            all_topics = []
            for t in all_topics_raw:
                if t['link'] not in seen:
                    seen.add(t['link'])
                    all_topics.append(t)

            # 按评分重新排序（最高质量的在前）
            all_topics.sort(key=lambda t: t.get('quality_score', 0), reverse=True)

            self.logger.info(f"✓ 去重后总共: {len(all_topics)} 个帖子")

            # 并发读取帖子内容（从高质量帖子中选择）
            self.logger.info(f"并发读取帖子内容（{self.read_limit} 条）...")
            read_count = min(self.read_limit, len(all_topics))

            # 使用 asyncio.gather 并发获取
            content_tasks = [
                self.get_topic_content(topic['link'])
                for topic in all_topics[:read_count]
            ]
            contents = await asyncio.gather(*content_tasks, return_exceptions=True)

            # 处理结果
            topics_with_content = []
            for topic, content in zip(all_topics[:read_count], contents):
                if isinstance(content, Exception):
                    self.logger.warning(f"获取内容失败: {topic['title'][:30]}")
                    continue
                if content:
                    topic_with_content = topic.copy()
                    topic_with_content['content_summary'] = content
                    topics_with_content.append(topic_with_content)

            self.logger.info(f"✓ 成功读取 {len(topics_with_content)} 个帖子内容")

            # 缓存+并发AI分析（性能优化）
            self.logger.info(f"AI 分析中（共 {self.ai_limit} 个帖子）...")
            ai_analysis_tasks = []
            ai_topics = []
            cached_count = 0
            ai_summaries = []

            for topic in topics_with_content[:self.ai_limit]:
                # 检查缓存
                cached_data = self.cache.get(topic)
                if cached_data:
                    # 使用缓存的分析结果
                    topic['ai_summary'] = cached_data.get('analysis', {})
                    ai_summaries.append(topic)
                    cached_count += 1
                    self.logger.debug(f"  ✓ [缓存] {topic['title'][:30]}")
                    continue

                # 需要新分析
                content_text = topic.get('content_summary', {}).get('first_post', '')
                if content_text and len(content_text) > 100:
                    ai_analysis_tasks.append(
                        self.ai_analyzer.summarize_topic(topic, content_text)
                    )
                    ai_topics.append(topic)

            # 并发执行 AI 分析（仅对未缓存的帖子）
            if ai_analysis_tasks:
                self.logger.info(f"  需要分析 {len(ai_analysis_tasks)} 个新帖子（{cached_count} 个使用缓存）")
                ai_results = await asyncio.gather(*ai_analysis_tasks, return_exceptions=True)

                for topic, ai_result in zip(ai_topics, ai_results):
                    if isinstance(ai_result, Exception):
                        self.logger.warning(f"AI分析失败: {topic['title'][:30]}")
                        continue

                    topic['ai_summary'] = ai_result
                    ai_summaries.append(topic)

                    # 缓存分析结果
                    self.cache.set(topic, ai_result)
                    self.logger.debug(f"  ✓ [新分析] {topic['title'][:30]}")

                self.logger.info(f"✓ AI分析完成: {len(ai_summaries)} 个 (缓存命中 {cached_count}/{self.ai_limit})")
            elif cached_count > 0:
                self.logger.info(f"✓ 全部使用缓存: {cached_count} 个帖子")

            # 使用 AI 进行兴趣推荐
            self.logger.info("生成推荐列表...")

            # 构建用户画像（如果配置了）
            user_profile = None
            if self.user_interests:
                user_profile = {
                    'interests': self.user_interests
                }

            recommended_topics = await self.ai_analyzer.analyze_interests(
                topics=all_topics,
                user_profile=user_profile
            )

            # 生成摘要
            summary = self._generate_summary(
                latest_topics,
                hot_topics,
                ai_summaries,
                recommended_topics
            )

            return CheckinResult(
                True,
                f"成功获取论坛动态并生成 AI 分析（共{len(all_topics)}个帖子，推荐{len(recommended_topics[:10])}个）",
                {
                    "latest_topics": latest_topics,
                    "hot_topics": hot_topics,
                    "category_topics": category_topics,
                    "topics_with_content": topics_with_content,
                    "ai_summaries": ai_summaries,
                    "recommended_topics": recommended_topics[:10],  # 只保留前10个推荐
                    "summary": summary
                }
            )

        except Exception as e:
            self.logger.error(f"获取帖子信息出错: {str(e)}")
            await self.take_screenshot("checkin_exception")
            return CheckinResult(False, f"获取帖子信息出错: {str(e)}")

    async def get_latest_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最新帖子列表（支持滚动加载）

        Args:
            limit: 获取数量限制

        Returns:
            帖子列表
        """
        try:
            # 访问最新页面
            latest_url = f"{self.site_url}/latest"
            await self.page.goto(latest_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)

            # 如果启用了滚动加载，滚动页面加载更多内容
            if self.enable_scroll_loading:
                self.logger.debug(f"开始滚动加载更多帖子（{self.scroll_times}次）...")
                for i in range(self.scroll_times):
                    # 滚动到页面底部
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(self.scroll_interval)

                    # 检查是否还有新内容
                    current_count = await self.page.evaluate(
                        "document.querySelectorAll('.topic-list-item, [data-topic-id]').length"
                    )
                    self.logger.debug(f"  滚动 {i+1}/{self.scroll_times}，当前帖子数：{current_count}")

                    # 如果已经达到目标数量，可以提前退出
                    if current_count >= limit:
                        self.logger.debug(f"  已达到目标数量 {limit}，停止滚动")
                        break

            await self.take_screenshot("latest_topics")

            # 使用 JavaScript 提取帖子信息
            topics = await self.page.evaluate(f"""
                (limit) => {{
                    const topics = [];
                    const topicElements = document.querySelectorAll('.topic-list-item, [data-topic-id]');

                    topicElements.forEach((el, idx) => {{
                        if (idx >= limit) return;

                        // 标题和链接
                        const titleEl = el.querySelector('.title a, .topic-title a, a.title');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        const link = titleEl ? titleEl.getAttribute('href') : '';

                        // 作者
                        const authorEl = el.querySelector('.topic-poster a, .author a');
                        const author = authorEl ? authorEl.getAttribute('data-user-card') || authorEl.textContent.trim() : '';

                        // 回复数和浏览数
                        const repliesEl = el.querySelector('.posts, .num.posts');
                        const replies = repliesEl ? repliesEl.textContent.trim() : '0';

                        const viewsEl = el.querySelector('.views, .num.views');
                        const views = viewsEl ? viewsEl.textContent.trim() : '0';

                        // 最后活动时间
                        const activityEl = el.querySelector('.age.activity a, time');
                        const lastActivity = activityEl ? activityEl.getAttribute('title') || activityEl.textContent.trim() : '';

                        // 分类
                        const categoryEl = el.querySelector('.category, .badge-category');
                        const category = categoryEl ? categoryEl.textContent.trim() : '';

                        if (title && link) {{
                            topics.push({{
                                title,
                                link,
                                author,
                                replies,
                                views,
                                lastActivity,
                                category
                            }});
                        }}
                    }});

                    return topics;
                }}
            """, limit)

            self.logger.info(f"获取到 {len(topics)} 个最新帖子")
            return topics

        except Exception as e:
            self.logger.error(f"获取最新帖子失败: {str(e)}")
            return []

    async def get_hot_topics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取热门帖子列表（支持滚动加载）

        Args:
            limit: 获取数量限制

        Returns:
            帖子列表
        """
        try:
            # 访问热门页面
            hot_url = f"{self.site_url}/top"
            await self.page.goto(hot_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)

            # 如果启用了滚动加载，滚动页面加载更多内容
            if self.enable_scroll_loading:
                self.logger.debug(f"开始滚动加载更多热门帖子（{self.scroll_times}次）...")
                for i in range(self.scroll_times):
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(self.scroll_interval)

                    current_count = await self.page.evaluate(
                        "document.querySelectorAll('.topic-list-item, [data-topic-id]').length"
                    )
                    self.logger.debug(f"  滚动 {i+1}/{self.scroll_times}，当前帖子数：{current_count}")

                    if current_count >= limit:
                        self.logger.debug(f"  已达到目标数量 {limit}，停止滚动")
                        break

            await self.take_screenshot("hot_topics")

            # 使用与 get_latest_topics 相同的提取逻辑
            topics = await self.page.evaluate(f"""
                (limit) => {{
                    const topics = [];
                    const topicElements = document.querySelectorAll('.topic-list-item, [data-topic-id]');

                    topicElements.forEach((el, idx) => {{
                        if (idx >= limit) return;

                        const titleEl = el.querySelector('.title a, .topic-title a, a.title');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        const link = titleEl ? titleEl.getAttribute('href') : '';

                        const authorEl = el.querySelector('.topic-poster a, .author a');
                        const author = authorEl ? authorEl.getAttribute('data-user-card') || authorEl.textContent.trim() : '';

                        const repliesEl = el.querySelector('.posts, .num.posts');
                        const replies = repliesEl ? repliesEl.textContent.trim() : '0';

                        const viewsEl = el.querySelector('.views, .num.views');
                        const views = viewsEl ? viewsEl.textContent.trim() : '0';

                        const activityEl = el.querySelector('.age.activity a, time');
                        const lastActivity = activityEl ? activityEl.getAttribute('title') || activityEl.textContent.trim() : '';

                        const categoryEl = el.querySelector('.category, .badge-category');
                        const category = categoryEl ? categoryEl.textContent.trim() : '';

                        if (title && link) {{
                            topics.push({{
                                title,
                                link,
                                author,
                                replies,
                                views,
                                lastActivity,
                                category
                            }});
                        }}
                    }});

                    return topics;
                }}
            """, limit)

            self.logger.info(f"获取到 {len(topics)} 个热门帖子")
            return topics

        except Exception as e:
            self.logger.error(f"获取热门帖子失败: {str(e)}")
            return []

    async def get_category_topics(self, category_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        从特定分类获取帖子

        Args:
            category_name: 分类名称（如"福利羊毛"）
            limit: 获取数量限制

        Returns:
            帖子列表
        """
        try:
            # 根据分类名称构建 URL（Discourse 的分类 URL 格式）
            # Linux.do 的分类 URL 格式: https://linux.do/c/{category-slug}/{id}
            # 需要先映射分类名称到 slug
            category_map = {
                '福利羊毛': 'welfare',
                '优惠活动': 'promotion',
                '工具分享': 'tools',
                '开发调优': 'dev',
                '资源荟萃': 'resources'
            }

            category_slug = category_map.get(category_name, category_name.lower())

            # 尝试通过搜索找到分类
            # 或者直接访问分类页面（如果知道ID）
            # 这里我们使用搜索功能来找到分类帖子
            search_url = f"{self.site_url}/latest?category={category_slug}"

            self.logger.debug(f"访问分类页面: {search_url}")
            await self.page.goto(search_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)

            # 滚动加载更多
            if self.enable_scroll_loading:
                self.logger.debug(f"在分类 '{category_name}' 中滚动加载...")
                for i in range(self.scroll_times):
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(self.scroll_interval)

            # 提取帖子
            topics = await self.page.evaluate(f"""
                (limit) => {{
                    const topics = [];
                    const topicElements = document.querySelectorAll('.topic-list-item, [data-topic-id]');

                    topicElements.forEach((el, idx) => {{
                        if (idx >= limit) return;

                        const titleEl = el.querySelector('.title a, .topic-title a, a.title');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        const link = titleEl ? titleEl.getAttribute('href') : '';

                        const authorEl = el.querySelector('.topic-poster a, .author a');
                        const author = authorEl ? authorEl.getAttribute('data-user-card') || authorEl.textContent.trim() : '';

                        const repliesEl = el.querySelector('.posts, .num.posts');
                        const replies = repliesEl ? repliesEl.textContent.trim() : '0';

                        const viewsEl = el.querySelector('.views, .num.views');
                        const views = viewsEl ? viewsEl.textContent.trim() : '0';

                        const activityEl = el.querySelector('.age.activity a, time');
                        const lastActivity = activityEl ? activityEl.getAttribute('title') || activityEl.textContent.trim() : '';

                        const categoryEl = el.querySelector('.category, .badge-category');
                        const category = categoryEl ? categoryEl.textContent.trim() : '';

                        if (title && link) {{
                            topics.push({{
                                title,
                                link,
                                author,
                                replies,
                                views,
                                lastActivity,
                                category
                            }});
                        }}
                    }});

                    return topics;
                }}
            """, limit)

            self.logger.info(f"从分类 '{category_name}' 获取到 {len(topics)} 个帖子")
            return topics

        except Exception as e:
            self.logger.error(f"从分类 '{category_name}' 获取帖子失败: {str(e)}")
            return []

    async def get_topic_content(self, topic_link: str) -> Dict[str, str]:
        """
        获取帖子详细内容

        Args:
            topic_link: 帖子链接（相对路径）

        Returns:
            帖子内容摘要字典，包含：
            - first_post: 第一楼内容（截取前500字符）
            - key_points: 关键信息点列表
        """
        try:
            # 访问帖子页面
            topic_url = f"{self.site_url}{topic_link}"
            self.logger.debug(f"访问帖子: {topic_url}")

            await self.page.goto(topic_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)

            # 提取帖子内容
            content_data = await self.page.evaluate("""
                () => {
                    // 获取第一楼内容
                    const firstPost = document.querySelector('.topic-post:first-of-type .cooked, article.post:first-of-type .cooked');
                    let firstPostText = '';

                    if (firstPost) {
                        // 移除代码块和引用块，只保留主要文本
                        const clone = firstPost.cloneNode(true);

                        // 移除代码块
                        clone.querySelectorAll('pre, code').forEach(el => el.remove());

                        // 移除引用
                        clone.querySelectorAll('blockquote').forEach(el => el.remove());

                        // 移除图片
                        clone.querySelectorAll('img').forEach(el => el.remove());

                        firstPostText = clone.textContent.trim();

                        // 截取前800字符
                        if (firstPostText.length > 800) {
                            firstPostText = firstPostText.substring(0, 800) + '...';
                        }
                    }

                    // 尝试提取关键信息（列表项、加粗文本等）
                    const keyPoints = [];
                    if (firstPost) {
                        // 提取列表项
                        const listItems = firstPost.querySelectorAll('li');
                        listItems.forEach((item, idx) => {
                            if (idx < 3) {  // 只取前3个
                                const text = item.textContent.trim();
                                if (text.length < 100 && text.length > 10) {
                                    keyPoints.push(text);
                                }
                            }
                        });

                        // 如果没有列表项，提取加粗文本
                        if (keyPoints.length === 0) {
                            const boldTexts = firstPost.querySelectorAll('strong, b');
                            boldTexts.forEach((item, idx) => {
                                if (idx < 3) {
                                    const text = item.textContent.trim();
                                    if (text.length < 100 && text.length > 5) {
                                        keyPoints.push(text);
                                    }
                                }
                            });
                        }
                    }

                    return {
                        first_post: firstPostText,
                        key_points: keyPoints
                    };
                }
            """)

            self.logger.debug(f"提取到内容长度: {len(content_data.get('first_post', ''))} 字符")
            return content_data

        except Exception as e:
            self.logger.warning(f"获取帖子内容失败: {str(e)}")
            return {"first_post": "", "key_points": []}

    def _generate_summary(
        self,
        latest_topics: List[Dict[str, Any]],
        hot_topics: List[Dict[str, Any]],
        ai_summaries: List[Dict[str, Any]] = None,
        recommended_topics: List[Dict[str, Any]] = None
    ) -> str:
        """
        生成论坛动态摘要

        Args:
            latest_topics: 最新帖子列表
            hot_topics: 热门帖子列表
            ai_summaries: AI 分析的帖子列表
            recommended_topics: 推荐帖子列表

        Returns:
            摘要文本
        """
        summary_lines = []

        summary_lines.append("=" * 60)
        summary_lines.append("Linux.do 论坛智能分析报告")
        summary_lines.append("=" * 60)

        # ===== AI 推荐的最感兴趣的话题 =====
        if recommended_topics and len(recommended_topics) > 0:
            summary_lines.append("\n【🎯 为你推荐 - 最可能感兴趣的话题】")
            for i, topic in enumerate(recommended_topics[:5], 1):  # 显示前5个
                score = topic.get('relevance_score', 0)
                reason = topic.get('recommendation_reason', '热门话题')
                tags = topic.get('recommendation_tags', [])

                summary_lines.append(
                    f"\n{i}. {topic['title']}"
                )
                summary_lines.append(
                    f"   📊 相关度: {score}% | 💬 {topic['replies']} | 👁️ {topic['views']}"
                )
                summary_lines.append(
                    f"   📝 推荐理由: {reason}"
                )
                if tags:
                    summary_lines.append(
                        f"   🏷️ 标签: {', '.join(tags)}"
                    )
                summary_lines.append(
                    f"   🔗 {self.site_url}{topic['link']}"
                )

        # ===== AI 深度分析的帖子 =====
        if ai_summaries and len(ai_summaries) > 0:
            summary_lines.append("\n【🤖 AI 深度分析】")
            for i, topic in enumerate(ai_summaries, 1):
                ai_summary = topic.get('ai_summary', {})

                summary_lines.append(f"\n{i}. {topic['title']}")
                summary_lines.append(f"   作者: {topic['author']} | 分类: {topic['category']}")

                # AI 生成的摘要
                if ai_summary.get('summary'):
                    summary_lines.append(f"   📝 AI 摘要: {ai_summary['summary']}")

                # 关键点
                if ai_summary.get('key_points'):
                    summary_lines.append("   🔑 关键要点:")
                    for point in ai_summary['key_points'][:3]:
                        summary_lines.append(f"      • {point}")

                # 标签
                if ai_summary.get('tags'):
                    summary_lines.append(f"   🏷️ 主题标签: {', '.join(ai_summary['tags'])}")

                # 情感
                sentiment_emoji = {"positive": "😊", "negative": "😟", "neutral": "😐"}
                sentiment = ai_summary.get('sentiment', 'neutral')
                summary_lines.append(f"   💭 情感倾向: {sentiment_emoji.get(sentiment, '😐')} {sentiment}")

                summary_lines.append(f"   🔗 {self.site_url}{topic['link']}")

        # ===== 最新帖子 =====
        if latest_topics:
            summary_lines.append("\n【📰 最新帖子】")
            for i, topic in enumerate(latest_topics[:10], 1):
                summary_lines.append(
                    f"{i}. {topic['title']}\n"
                    f"   作者: {topic['author']} | "
                    f"分类: {topic['category']} | "
                    f"回复: {topic['replies']} | "
                    f"浏览: {topic['views']}\n"
                    f"   链接: {self.site_url}{topic['link']}"
                )

        # ===== 热门帖子 =====
        if hot_topics:
            summary_lines.append("\n【🔥 热门话题】")
            for i, topic in enumerate(hot_topics[:10], 1):
                summary_lines.append(
                    f"{i}. {topic['title']}\n"
                    f"   作者: {topic['author']} | "
                    f"分类: {topic['category']} | "
                    f"回复: {topic['replies']} | "
                    f"浏览: {topic['views']}\n"
                    f"   链接: {self.site_url}{topic['link']}"
                )

        summary_lines.append("\n" + "=" * 60)
        summary_lines.append(f"📊 统计: 共分析 {len(latest_topics) + len(hot_topics)} 个帖子")
        if recommended_topics:
            summary_lines.append(f"🎯 为你推荐 {min(5, len(recommended_topics))} 个最相关话题")
        if ai_summaries:
            summary_lines.append(f"🤖 AI 深度分析 {len(ai_summaries)} 个热门帖子")
        summary_lines.append("=" * 60)

        return "\n".join(summary_lines)
