#!/usr/bin/env python3
"""
Linux.do 论坛自动阅读脚本
每10分钟执行一次（带随机化），仅阅读帖子不做AI分析
支持防重复阅读和评论滚动
"""
import asyncio
import sys
import random
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any, Set

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.browser_manager import BrowserManager
from core.logger import setup_logger
from modules.forum.linuxdo.adapter import LinuxDoAdapter


class ReadHistory:
    """已读帖子历史记录管理"""

    def __init__(self, username: str, cache_days: int = 7):
        """初始化已读历史

        Args:
            username: 用户名
            cache_days: 缓存天数（默认7天）
        """
        self.cache_days = cache_days
        cache_dir = PROJECT_ROOT / 'storage' / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / f'read_history_{username}.json'
        self.history: Dict[str, str] = {}
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self._clean_expired()
            except Exception:
                self.history = {}

    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _clean_expired(self):
        """清理过期记录"""
        expiry_time = datetime.now() - timedelta(days=self.cache_days)
        expired_keys = [
            key for key, timestamp in self.history.items()
            if datetime.fromisoformat(timestamp) < expiry_time
        ]
        for key in expired_keys:
            del self.history[key]
        if expired_keys:
            self._save_history()

    def get_topic_id(self, topic_link: str) -> str:
        """生成帖子唯一标识"""
        return hashlib.md5(topic_link.encode()).hexdigest()[:16]

    def is_read(self, topic_link: str) -> bool:
        """检查帖子是否已读"""
        topic_id = self.get_topic_id(topic_link)
        return topic_id in self.history

    def mark_read(self, topic_link: str):
        """标记帖子为已读"""
        topic_id = self.get_topic_id(topic_link)
        self.history[topic_id] = datetime.now().isoformat()
        self._save_history()

    def filter_unread(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤出未读帖子"""
        return [t for t in topics if not self.is_read(t.get('link', ''))]


async def auto_read(username: str, password: str, site_url: str = "https://linux.do"):
    """
    自动阅读论坛帖子（轻量级版本）

    Args:
        username: 用户名
        password: 密码
        site_url: 站点URL
    """
    # 设置日志
    logger = setup_logger('linuxdo_auto_read', level='DEBUG')

    # 初始化已读历史
    read_history = ReadHistory(username, cache_days=7)
    logger.info(f"已读历史：过去7天已读 {len(read_history.history)} 个帖子")

    # 添加随机延迟（0-120秒，即0-2分钟）
    random_delay = random.randint(0, 120)
    logger.info(f"添加随机延迟: {random_delay}秒 (约{random_delay/60:.1f}分钟)")
    await asyncio.sleep(random_delay)

    logger.info("=" * 60)
    logger.info(f"自动阅读开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 初始化浏览器
    browser_manager = BrowserManager(headless=True)

    try:
        await browser_manager.start()

        # 尝试从 cookies.json 恢复会话（如果会话不存在）
        cookies_file = PROJECT_ROOT / 'modules' / 'forum' / 'linuxdo' / 'cookies.json'
        session_dir = PROJECT_ROOT / 'storage' / 'sessions' / f'linuxdo_{username}'
        state_file = session_dir / 'state.json'

        if cookies_file.exists() and not state_file.exists():
            logger.info("发现 cookies 配置但无会话文件，创建会话...")
            try:
                session_dir.mkdir(parents=True, exist_ok=True)
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    cookies_data = json.load(f)
                # 写入 state.json
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'cookies': cookies_data.get('cookies', []),
                        'origins': []
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"成功创建会话文件: {state_file}")
            except Exception as e:
                logger.warning(f"创建会话失败: {e}")

        # 创建浏览器上下文（会自动加载 state.json）
        context = await browser_manager.create_context('linuxdo', username, load_session=True)

        # 创建适配器（简化配置，只做阅读）
        adapter = LinuxDoAdapter(
            site_url=site_url,
            username=username,
            password=password,
            logger=logger,
            # 轻量级配置
            latest_limit=30,  # 获取30个最新帖子
            hot_limit=0,  # 不获取热门帖子
            read_limit=10,  # 深度阅读10个帖子
            ai_limit=0,  # 不做AI分析
            enable_scroll_loading=False,  # 不滚动加载
            fetch_priority_categories=False,  # 不获取分类
            # 禁用AI
            ai_enabled=False
        )

        # 创建 page 对象（必须在调用 adapter 方法之前）
        adapter.context = context
        adapter.page = await context.new_page()

        # 检查登录状态
        logger.info("检查登录状态...")
        is_logged = await adapter.is_logged_in()

        if not is_logged:
            logger.info("未登录，执行登录...")
            login_success = await adapter.login()
            if not login_success:
                logger.error("登录失败")
                return False
        else:
            logger.info("已登录")

        # 获取并阅读帖子
        logger.info("获取最新帖子...")
        topics = await adapter.get_latest_topics(limit=30)

        if not topics:
            logger.warning("未获取到帖子")
            return False

        logger.info(f"成功获取 {len(topics)} 个帖子")

        # 过滤未读帖子
        unread_topics = read_history.filter_unread(topics)
        logger.info(f"过滤后未读帖子: {len(unread_topics)} 个")

        # 如果未读帖子太少，允许重读部分帖子
        if len(unread_topics) < 5:
            logger.info(f"未读帖子不足5个，补充部分已读帖子")
            # 从原列表中随机选择一些帖子
            additional = random.sample(topics, min(5, len(topics)))
            unread_topics = unread_topics + additional
            # 去重
            seen = set()
            unread_topics = [t for t in unread_topics if not (t['link'] in seen or seen.add(t['link']))]

        # 随机选择5-10个帖子进行深度阅读
        read_count = random.randint(5, min(10, len(unread_topics)))
        topics_to_read = random.sample(unread_topics, read_count)

        logger.info(f"随机选择 {len(topics_to_read)} 个帖子进行阅读")

        for i, topic in enumerate(topics_to_read, 1):
            try:
                logger.info(f"[{i}/{len(topics_to_read)}] 阅读: {topic['title'][:40]}...")

                # 访问帖子并获取内容
                content = await adapter.get_topic_content(topic['link'])

                if content and content.get('first_post'):
                    content_length = len(content['first_post'])
                    logger.info(f"  成功阅读内容 ({content_length} 字符)")

                    # 滚动阅读评论（模拟真实用户行为）
                    scroll_times = random.randint(2, 4)  # 随机滚动2-4次
                    logger.info(f"  滚动阅读评论 ({scroll_times} 次)")

                    for scroll_idx in range(scroll_times):
                        # 滚动页面
                        await adapter.page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
                        # 随机停留1-3秒
                        await asyncio.sleep(random.randint(1, 3))

                    # 添加随机阅读时间（5-15秒）
                    reading_time = random.randint(5, 15)
                    logger.debug(f"  额外停留时间: {reading_time}秒")
                    await asyncio.sleep(reading_time)

                    # 标记为已读
                    read_history.mark_read(topic['link'])
                else:
                    logger.debug(f"  内容为空或获取失败")

                # 帖子之间添加随机间隔（2-5秒）
                interval = random.randint(2, 5)
                await asyncio.sleep(interval)

            except Exception as e:
                logger.warning(f"  阅读失败: {str(e)[:100]}")
                continue

        # 保存会话
        await browser_manager.save_context(context, 'linuxdo', username)

        # 关闭 page 和 context
        if adapter.page:
            await adapter.page.close()
        await context.close()

        logger.info("=" * 60)
        logger.info(f"自动阅读完成")
        logger.info(f"  本次阅读: {len(topics_to_read)} 个帖子（含评论滚动）")
        logger.info(f"  历史记录: {len(read_history.history)} 个已读帖子（7天内）")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"自动阅读失败: {str(e)}", exc_info=True)
        return False

    finally:
        await browser_manager.close()


async def main():
    """主函数"""
    # 加载环境变量
    env_file = PROJECT_ROOT / '.env'
    if env_file.exists():
        load_dotenv(env_file)

    # 硬编码账号信息（从配置文件读取）
    import yaml
    config_file = PROJECT_ROOT / 'modules' / 'forum' / 'linuxdo' / 'config.yaml'

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    accounts = config.get('site', {}).get('accounts', [])
    enabled_accounts = [acc for acc in accounts if acc.get('enabled', True)]

    if not enabled_accounts:
        print("没有启用的账号")
        return

    # 只处理第一个账号
    account = enabled_accounts[0]
    username = account.get('username')
    password = account.get('password')

    if not username or not password:
        print("账号配置不完整")
        return

    # 执行自动阅读
    success = await auto_read(username, password)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
