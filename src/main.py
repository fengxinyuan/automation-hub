#!/usr/bin/env python3
"""自动签到系统主程序"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import ConfigLoader
from src.browser_manager import BrowserManager
from src.notifiers.logger import setup_logger
from src.notifiers.email import EmailNotifier
from src.adapters.anyrouter import AnyrouterAdapter


# 站点适配器映射
ADAPTERS = {
    'anyrouter': AnyrouterAdapter,
}


async def run_checkin(
    site_name: str,
    site_config: Dict[str, Any],
    account: Dict[str, Any],
    browser_manager: BrowserManager,
    logger
) -> Dict[str, Any]:
    """
    执行单个账号的签到

    Args:
        site_name: 站点名称
        site_config: 站点配置
        account: 账号信息
        browser_manager: 浏览器管理器
        logger: 日志记录器

    Returns:
        签到结果
    """
    username = account['username']
    password = account['password']

    try:
        # 获取适配器
        adapter_class = ADAPTERS.get(site_name)
        if not adapter_class:
            logger.error(f"不支持的站点: {site_name}")
            return {
                'site': site_name,
                'username': username,
                'success': False,
                'message': f"不支持的站点: {site_name}"
            }

        # 创建浏览器上下文
        context = await browser_manager.create_context(
            site_name=site_name,
            user_id=username.replace('@', '_').replace('.', '_')
        )

        # 创建适配器并执行签到
        adapter = adapter_class(
            site_url=site_config['url'],
            username=username,
            password=password,
            logger=logger
        )

        result = await adapter.run(context)

        # 保存浏览器上下文
        await browser_manager.save_context(
            context=context,
            site_name=site_name,
            user_id=username.replace('@', '_').replace('.', '_')
        )

        # 关闭上下文
        await context.close()

        return {
            'site': site_name,
            'username': username,
            'success': result.success,
            'message': result.message,
            'details': result.details
        }

    except Exception as e:
        logger.error(f"[{site_name}] {username} 执行失败: {str(e)}", exc_info=True)
        return {
            'site': site_name,
            'username': username,
            'success': False,
            'message': f"执行出错: {str(e)}"
        }


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自动签到系统')
    parser.add_argument(
        '--config',
        default='config/sites.yaml',
        help='配置文件路径 (默认: config/sites.yaml)'
    )
    parser.add_argument(
        '--site',
        help='指定站点名称 (默认: 全部站点)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='调试模式 (显示浏览器窗口)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='测试模式 (不实际执行签到)'
    )

    args = parser.parse_args()

    # 加载配置
    try:
        config_loader = ConfigLoader(args.config)
        config = config_loader.load()
    except Exception as e:
        print(f"加载配置失败: {str(e)}")
        sys.exit(1)

    # 设置日志
    notification_config = config_loader.get_notification_config()
    log_config = notification_config.get('log', {})

    logger = setup_logger(
        level=log_config.get('level', 'INFO'),
        log_file='logs/checkin.log' if log_config.get('enabled', True) else None
    )

    logger.info("=" * 60)
    logger.info("开始执行自动签到")
    logger.info("=" * 60)

    # 测试模式
    if args.dry_run:
        logger.info("测试模式: 仅加载配置，不执行签到")
        logger.info(f"配置文件: {args.config}")
        logger.info(f"站点列表: {list(config_loader.get_sites().keys())}")
        for site_name, site_config in config_loader.get_sites().items():
            accounts = config_loader.get_enabled_accounts(site_name)
            logger.info(f"  {site_name}: {len(accounts)} 个账号")
        return

    # 初始化浏览器管理器
    async with BrowserManager(headless=not args.debug) as browser_manager:
        # 收集所有签到任务
        all_results: Dict[str, List[Dict[str, Any]]] = {}

        # 遍历站点
        sites = config_loader.get_sites()
        if args.site:
            if args.site not in sites:
                logger.error(f"站点不存在: {args.site}")
                sys.exit(1)
            sites = {args.site: sites[args.site]}

        for site_name, site_config in sites.items():
            logger.info(f"\n处理站点: {site_name}")

            # 获取已启用的账号
            accounts = config_loader.get_enabled_accounts(site_name)

            if not accounts:
                logger.warning(f"站点 {site_name} 没有启用的账号")
                continue

            site_results = []

            # 遍历账号
            for account in accounts:
                result = await run_checkin(
                    site_name=site_name,
                    site_config=site_config,
                    account=account,
                    browser_manager=browser_manager,
                    logger=logger
                )
                site_results.append(result)

                # 输出结果
                status = "✓" if result['success'] else "✗"
                logger.info(
                    f"  {status} {result['username']}: {result['message']}"
                )

            all_results[site_name] = site_results

    # 汇总统计
    logger.info("\n" + "=" * 60)
    logger.info("签到完成")

    total_success = sum(
        1 for results in all_results.values()
        for r in results if r['success']
    )
    total_failed = sum(
        1 for results in all_results.values()
        for r in results if not r['success']
    )

    logger.info(f"成功: {total_success}, 失败: {total_failed}")
    logger.info("=" * 60)

    # 发送邮件通知
    email_config = notification_config.get('email', {})
    if email_config.get('enabled', False):
        try:
            notifier = EmailNotifier(
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                username=email_config['username'],
                password=email_config['password'],
                use_tls=email_config.get('use_tls', True),
                logger=logger
            )

            notifier.send_checkin_report(
                to_addresses=email_config.get('to_addresses', []),
                results=all_results
            )
        except Exception as e:
            logger.error(f"发送邮件通知失败: {str(e)}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n程序异常: {str(e)}")
        sys.exit(1)
