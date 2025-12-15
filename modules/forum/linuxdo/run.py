#!/usr/bin/env python3
"""
Linux.do 论坛自动化 - 独立运行脚本
包含 AI 智能分析功能（使用阿里云通义千问 qwen-flash）
"""
import asyncio
import argparse
import sys
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.browser_manager import BrowserManager
from core.logger import setup_logger
from core.notifiers.email import EmailNotifier
from modules.forum.linuxdo.adapter import LinuxDoAdapter


def load_config(config_file: str) -> Dict[str, Any]:
    """加载配置文件"""
    # 加载环境变量
    env_file = PROJECT_ROOT / '.env'
    if env_file.exists():
        load_dotenv(env_file)

    # 读取配置文件
    config_path = Path(config_file)
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_file

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def _save_summary_to_file(results: Dict[str, List[Dict[str, Any]]], logger):
    """
    保存总结到文件

    Args:
        results: 执行结果
        logger: 日志记录器
    """
    try:
        from datetime import datetime
        import json

        # 创建输出目录
        output_dir = PROJECT_ROOT / 'storage' / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'linuxdo_summary_{timestamp}.txt'
        json_file = output_dir / f'linuxdo_summary_{timestamp}.json'

        # 保存 JSON（完整数据）
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 生成可读的文本总结
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Linux.do 论坛动态总结\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            for site_name, site_results in results.items():
                for result in site_results:
                    if not result.get('success') or 'details' not in result:
                        continue

                    details = result['details']
                    f.write(f"账号: {result['username']}\n")
                    f.write("-" * 80 + "\n\n")

                    # 输出推荐帖子
                    recommended = details.get('recommended_topics', [])
                    if recommended:
                        f.write(f"📌 推荐帖子 (共 {len(recommended)} 个):\n\n")
                        for i, topic in enumerate(recommended[:10], 1):
                            f.write(f"{i}. {topic.get('title', '无标题')}\n")
                            f.write(f"   作者: {topic.get('author', '未知')} | ")
                            f.write(f"回复: {topic.get('replies', '0')} | ")
                            f.write(f"浏览: {topic.get('views', '0')}\n")
                            f.write(f"   链接: {topic.get('link', '')}\n")

                            if topic.get('recommendation_reason'):
                                f.write(f"   💡 推荐理由: {topic['recommendation_reason']}\n")

                            # AI 总结
                            if topic.get('ai_summary'):
                                summary = topic['ai_summary']
                                if summary.get('summary'):
                                    f.write(f"   📝 AI 总结: {summary['summary']}\n")
                                if summary.get('key_points'):
                                    f.write(f"   🔑 关键点:\n")
                                    for point in summary['key_points']:
                                        f.write(f"      • {point}\n")
                                if summary.get('tags'):
                                    f.write(f"   🏷️  标签: {', '.join(summary['tags'])}\n")

                            f.write("\n")

                    # 输出完整总结文本
                    if details.get('summary'):
                        f.write("\n" + "=" * 80 + "\n")
                        f.write("详细总结:\n")
                        f.write("=" * 80 + "\n")
                        f.write(details['summary'])
                        f.write("\n")

        logger.info(f"✅ 总结已保存到: {output_file}")
        logger.info(f"✅ 完整数据已保存到: {json_file}")

    except Exception as e:
        logger.error(f"保存总结失败: {str(e)}")


async def run_linuxdo(
    config_file: str = "config.yaml",
    debug: bool = False,
    dry_run: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """运行 Linux.do 论坛自动化"""
    # 加载配置
    config = load_config(config_file)

    # 设置日志
    log_level_str = 'DEBUG' if debug else 'INFO'
    logger = setup_logger('linuxdo', level=log_level_str)

    logger.info("=" * 60)
    logger.info("Linux.do 论坛自动化开始")
    logger.info("=" * 60)

    if dry_run:
        logger.info("【模拟运行模式】不会执行实际操作")

    # 获取站点配置
    site_config = config.get('site', {})
    site_name = site_config.get('name', 'linuxdo')
    site_url = site_config.get('url')
    accounts = site_config.get('accounts', [])

    if not site_url:
        logger.error("配置文件中未找到站点 URL")
        return {site_name: []}

    # 过滤启用的账号
    enabled_accounts = [acc for acc in accounts if acc.get('enabled', True)]

    if not enabled_accounts:
        logger.warning(f"没有启用的账号")
        return {site_name: []}

    logger.info(f"站点: {site_url}")
    logger.info(f"启用账号数: {len(enabled_accounts)}")

    # 获取内容配置
    content_config = config.get('content', {})
    latest_limit = content_config.get('latest_topics_limit', 20)
    hot_limit = content_config.get('hot_topics_limit', 10)
    read_limit = content_config.get('read_content_limit', 5)
    ai_limit = content_config.get('ai_analysis_limit', 3)

    logger.info(f"内容获取配置: 最新{latest_limit}条, 热门{hot_limit}条, 深度阅读{read_limit}条, AI分析{ai_limit}条")

    # 获取 AI 配置
    ai_config = config.get('ai', {})
    ai_enabled = ai_config.get('enabled', True)

    if ai_enabled:
        # 处理环境变量替换
        def resolve_env_var(value):
            """解析环境变量"""
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, '')
            return value

        api_key = resolve_env_var(ai_config.get('api_key', ''))
        api_base = resolve_env_var(ai_config.get('api_base', ''))
        model = resolve_env_var(ai_config.get('model', 'qwen-flash'))

        if api_key:
            logger.info(f"AI 功能已启用 - 模型: {model} - 端点: {api_base}")
        else:
            logger.warning("AI 功能已启用但未配置 API Key，将使用简化模式")
            ai_enabled = False
    else:
        logger.info("AI 功能未启用，使用简化模式")
        api_key = None
        api_base = None
        model = None

    # 初始化浏览器管理器
    browser_config = config.get('browser', {})
    headless = not debug if debug else browser_config.get('headless', True)

    browser_manager = BrowserManager(headless=headless)

    # 初始化结果存储
    results = {site_name: []}

    try:
        # 启动浏览器
        await browser_manager.start()

        # 处理每个账号
        for account in enabled_accounts:
            username = account.get('username')
            password = account.get('password')

            if not username or not password:
                logger.warning(f"账号配置不完整，跳过: {username}")
                continue

            try:
                logger.info(f"处理账号: {username}")

                if dry_run:
                    logger.info(f"[模拟] 为 {username} 获取论坛动态")
                    results[site_name].append({
                        'success': True,
                        'username': username,
                        'message': '[模拟运行] 获取成功'
                    })
                    continue

                # 创建浏览器上下文
                context = await browser_manager.create_context('linuxdo', username)

                # 创建适配器（传入配置参数）
                adapter = LinuxDoAdapter(
                    site_url=site_url,
                    username=username,
                    password=password,
                    logger=logger,
                    # 传入内容配置
                    latest_limit=latest_limit,
                    hot_limit=hot_limit,
                    read_limit=read_limit,
                    ai_limit=ai_limit,
                    # 传入 AI 配置（使用解析后的变量）
                    ai_enabled=ai_enabled,
                    ai_api_key=api_key,
                    ai_api_base=api_base,
                    ai_model=model,
                    ai_temperature=ai_config.get('temperature', 0.7),
                    ai_max_tokens=ai_config.get('max_tokens', 800),
                    user_interests=ai_config.get('user_interests')
                )

                # 执行获取
                result = await adapter.run(context)

                # 保存会话
                await browser_manager.save_context(context, 'linuxdo', username)
                await context.close()

                if result.success:
                    logger.info(f"✓ {username} - {result.message}")
                else:
                    logger.error(f"✗ {username} - {result.message}")

                results[site_name].append({
                    'success': result.success,
                    'username': username,
                    'message': result.message,
                    'details': result.details
                })

            except Exception as e:
                logger.error(f"账号 {username} 处理失败: {str(e)}", exc_info=True)
                results[site_name].append({
                    'success': False,
                    'username': username,
                    'message': f"处理失败: {str(e)}"
                })

    finally:
        # 关闭浏览器
        await browser_manager.close()

    # 统计结果
    total = len(results[site_name])
    success = sum(1 for r in results[site_name] if r['success'])
    failed = total - success

    logger.info("=" * 60)
    logger.info(f"执行完成: 成功 {success}/{total}, 失败 {failed}")
    logger.info("=" * 60)

    # 保存总结到文件
    _save_summary_to_file(results, logger)

    # 发送邮件通知
    email_config = config.get('notifications', {}).get('email', {})
    if email_config.get('enabled'):
        logger.info("发送邮件通知...")
        try:
            email_notifier = EmailNotifier(
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                username=email_config['username'],
                password=email_config['password'],
                use_tls=email_config.get('use_tls', True),
                logger=logger
            )
            email_notifier.send_checkin_report(
                to_addresses=email_config['to_addresses'],
                results=results
            )
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")

    return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Linux.do 论坛自动化（含 AI 智能分析）')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径（默认: config.yaml）'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='调试模式（显示浏览器窗口）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行（不执行实际操作）'
    )

    args = parser.parse_args()

    try:
        # 运行自动化
        asyncio.run(run_linuxdo(
            config_file=args.config,
            debug=args.debug,
            dry_run=args.dry_run
        ))
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
