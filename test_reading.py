#!/usr/bin/env python3
"""测试 Linux.do 内容阅读和摘要生成功能"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader
from src.browser_manager import BrowserManager
from src.adapters.linuxdo import LinuxDoAdapter
from src.notifiers.logger import setup_logger


async def main():
    print("=" * 60)
    print("测试 Linux.do 内容阅读和摘要功能")
    print("=" * 60)
    print()

    # 加载配置
    config_loader = ConfigLoader('config/sites.yaml')
    config_loader.load()  # 需要先调用 load()
    sites = config_loader.get_sites()
    linuxdo_config = sites['linuxdo']
    account = linuxdo_config['accounts'][0]

    logger = setup_logger(level='INFO')

    async with BrowserManager(headless=True) as browser_manager:
        context = await browser_manager.create_context(
            site_name='linuxdo',
            user_id=account['username'].replace('@', '_').replace('.', '_')
        )

        adapter = LinuxDoAdapter(
            site_url=linuxdo_config['url'],
            username=account['username'],
            password=account['password'],
            logger=logger
        )

        result = await adapter.run(context)

        print()
        print("=" * 60)
        print("执行结果")
        print("=" * 60)
        print(f"状态: {'成功' if result.success else '失败'}")
        print(f"消息: {result.message}")
        print()

        if result.success and result.details:
            details = result.details

            print(f"最新帖子数: {len(details.get('latest_topics', []))}")
            print(f"热门帖子数: {len(details.get('hot_topics', []))}")
            print(f"已读取内容的帖子数: {len(details.get('topics_with_content', []))}")
            print()

            # 打印完整摘要
            if details.get('summary'):
                print(details['summary'])

        await context.close()

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
