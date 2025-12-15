#!/usr/bin/env python3
"""
日志清理脚本
清理指定天数前的日志文件和截图
"""
import argparse
import os
from pathlib import Path
from datetime import datetime, timedelta


def clean_logs(days: int = 7, dry_run: bool = False):
    """
    清理指定天数前的日志

    Args:
        days: 保留最近N天的日志
        dry_run: 模拟运行，不实际删除
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        print(f"日志目录不存在: {log_dir}")
        return

    # 计算截止时间
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_timestamp = cutoff_date.timestamp()

    deleted_count = 0
    deleted_size = 0

    print(f"{'[模拟]' if dry_run else ''} 清理 {days} 天前的日志文件...")
    print(f"截止时间: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # 遍历所有文件
    for file_path in log_dir.rglob("*"):
        if file_path.is_file():
            # 获取文件修改时间
            mtime = file_path.stat().st_mtime

            if mtime < cutoff_timestamp:
                file_size = file_path.stat().st_size
                deleted_size += file_size

                print(f"{'[将删除]' if dry_run else '[删除]'} {file_path} "
                      f"({file_size / 1024:.1f} KB)")

                if not dry_run:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"  错误: 删除失败 - {e}")
                else:
                    deleted_count += 1

    print("-" * 60)
    print(f"{'预计' if dry_run else '已'}删除 {deleted_count} 个文件，"
          f"释放 {deleted_size / 1024 / 1024:.2f} MB 空间")

    if dry_run:
        print("\n提示: 使用不带 --dry-run 参数执行实际删除")


def main():
    parser = argparse.ArgumentParser(description='清理旧日志文件')
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='保留最近N天的日志（默认: 7）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行，不实际删除文件'
    )

    args = parser.parse_args()

    if args.days < 1:
        print("错误: days 参数必须大于 0")
        return

    clean_logs(days=args.days, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
