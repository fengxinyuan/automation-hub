#!/usr/bin/env python3
"""
配置检查脚本
检查各模块的配置文件是否正确
"""
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def check_config_file(config_path: Path) -> Tuple[bool, List[str]]:
    """
    检查配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        (是否有效, 错误/警告列表)
    """
    errors = []
    warnings = []

    # 检查文件是否存在
    if not config_path.exists():
        return False, [f"配置文件不存在: {config_path}"]

    try:
        # 尝试加载 YAML
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            errors.append("配置文件为空")
            return False, errors

        # 检查基本结构
        if 'site' not in config:
            errors.append("缺少 'site' 配置节")

        if 'site' in config:
            site = config['site']

            # 检查 URL
            if 'url' not in site:
                errors.append("缺少 site.url 配置")

            # 检查账号
            if 'accounts' not in site:
                errors.append("缺少 site.accounts 配置")
            elif not site['accounts']:
                warnings.append("accounts 列表为空")
            else:
                # 检查每个账号
                enabled_count = 0
                for i, account in enumerate(site['accounts']):
                    if not isinstance(account, dict):
                        errors.append(f"账号 {i+1} 格式错误")
                        continue

                    # 检查必需字段
                    if 'username' not in account:
                        errors.append(f"账号 {i+1} 缺少 username")

                    # 检查是否启用
                    if account.get('enabled', True):
                        enabled_count += 1

                if enabled_count == 0:
                    warnings.append("没有启用的账号")

        # 返回结果
        is_valid = len(errors) == 0
        messages = errors + warnings
        return is_valid, messages

    except yaml.YAMLError as e:
        return False, [f"YAML 格式错误: {str(e)}"]
    except Exception as e:
        return False, [f"读取配置文件失败: {str(e)}"]


def check_all_modules():
    """检查所有模块的配置"""
    modules_dir = Path("modules")

    if not modules_dir.exists():
        print("错误: modules 目录不存在")
        return

    print("=" * 70)
    print("配置文件检查")
    print("=" * 70)

    total_modules = 0
    valid_modules = 0

    # 遍历所有模块
    for module_type in modules_dir.iterdir():
        if not module_type.is_dir():
            continue

        for module_name in module_type.iterdir():
            if not module_name.is_dir():
                continue

            # 检查配置文件
            config_file = module_name / "config.yaml"
            example_file = module_name / "config.yaml.example"

            module_path = f"{module_type.name}/{module_name.name}"
            total_modules += 1

            print(f"\n模块: {module_path}")
            print("-" * 70)

            # 检查是否有示例文件
            if example_file.exists():
                print(f"✓ 示例文件: {example_file.name}")
            else:
                print(f"⚠ 缺少示例文件: {example_file.name}")

            # 检查配置文件
            if not config_file.exists():
                print(f"✗ 配置文件不存在: {config_file.name}")
                print(f"  提示: 复制 {example_file.name} 为 {config_file.name}")
                continue

            # 验证配置
            is_valid, messages = check_config_file(config_file)

            if is_valid:
                print(f"✓ 配置文件有效: {config_file.name}")
                valid_modules += 1
            else:
                print(f"✗ 配置文件有错误: {config_file.name}")

            # 输出错误和警告
            for msg in messages:
                prefix = "  ⚠" if msg.startswith("没有") or "为空" in msg else "  ✗"
                print(f"{prefix} {msg}")

    print("\n" + "=" * 70)
    print(f"检查完成: {valid_modules}/{total_modules} 个模块配置有效")
    print("=" * 70)


def main():
    check_all_modules()


if __name__ == '__main__':
    main()
