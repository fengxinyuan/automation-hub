"""配置验证模块"""
from typing import Dict, Any, List
import re


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """
        验证配置的完整性和有效性

        Args:
            config: 配置字典

        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []

        # 验证站点配置
        if 'sites' not in config or not config['sites']:
            errors.append("配置文件缺少 'sites' 字段或站点列表为空")
            return errors

        for site_name, site_config in config['sites'].items():
            site_errors = ConfigValidator._validate_site(site_name, site_config)
            errors.extend(site_errors)

        # 验证通知配置
        if 'notifications' in config:
            notification_errors = ConfigValidator._validate_notifications(config['notifications'])
            errors.extend(notification_errors)

        return errors

    @staticmethod
    def _validate_site(site_name: str, site_config: Dict[str, Any]) -> List[str]:
        """验证单个站点配置"""
        errors = []

        # 验证 URL
        if 'url' not in site_config:
            errors.append(f"站点 '{site_name}' 缺少 'url' 字段")
        elif not site_config['url'].startswith(('http://', 'https://')):
            errors.append(f"站点 '{site_name}' 的 URL 格式无效: {site_config['url']}")

        # 验证账号列表
        if 'accounts' not in site_config:
            errors.append(f"站点 '{site_name}' 缺少 'accounts' 字段")
        elif not isinstance(site_config['accounts'], list):
            errors.append(f"站点 '{site_name}' 的 'accounts' 必须是列表")
        elif len(site_config['accounts']) == 0:
            errors.append(f"站点 '{site_name}' 的账号列表为空")
        else:
            for idx, account in enumerate(site_config['accounts']):
                account_errors = ConfigValidator._validate_account(
                    site_name, idx, account
                )
                errors.extend(account_errors)

        return errors

    @staticmethod
    def _validate_account(
        site_name: str, idx: int, account: Dict[str, Any]
    ) -> List[str]:
        """验证单个账号配置"""
        errors = []

        # 验证用户名
        if 'username' not in account:
            errors.append(
                f"站点 '{site_name}' 的第 {idx + 1} 个账号缺少 'username' 字段"
            )
        elif not account['username']:
            errors.append(
                f"站点 '{site_name}' 的第 {idx + 1} 个账号的 username 不能为空"
            )

        # 验证密码
        if 'password' not in account:
            errors.append(
                f"站点 '{site_name}' 的第 {idx + 1} 个账号缺少 'password' 字段"
            )
        elif not account['password']:
            errors.append(
                f"站点 '{site_name}' 的第 {idx + 1} 个账号的 password 不能为空"
            )

        # 验证 enabled 字段
        if 'enabled' in account and not isinstance(account['enabled'], bool):
            errors.append(
                f"站点 '{site_name}' 的第 {idx + 1} 个账号的 'enabled' 必须是布尔值"
            )

        return errors

    @staticmethod
    def _validate_notifications(notifications: Dict[str, Any]) -> List[str]:
        """验证通知配置"""
        errors = []

        # 验证日志配置
        if 'log' in notifications:
            log_config = notifications['log']

            if 'level' in log_config:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if log_config['level'].upper() not in valid_levels:
                    errors.append(
                        f"日志级别无效: {log_config['level']}，"
                        f"有效值: {', '.join(valid_levels)}"
                    )

        # 验证邮件配置
        if 'email' in notifications:
            email_config = notifications['email']

            if email_config.get('enabled', False):
                # 检查必需字段
                required_fields = ['smtp_server', 'smtp_port', 'username', 'password']
                for field in required_fields:
                    if field not in email_config or not email_config[field]:
                        errors.append(f"邮件通知已启用，但缺少必需字段: {field}")

                # 验证端口
                if 'smtp_port' in email_config:
                    try:
                        port = int(email_config['smtp_port'])
                        if port < 1 or port > 65535:
                            errors.append(f"SMTP 端口无效: {port}，必须在 1-65535 之间")
                    except (ValueError, TypeError):
                        errors.append(f"SMTP 端口必须是整数: {email_config['smtp_port']}")

                # 验证邮箱格式
                if 'username' in email_config:
                    email = email_config['username']
                    if not ConfigValidator._is_valid_email(email):
                        errors.append(f"邮箱格式无效: {email}")

                # 验证收件人列表
                if 'to_addresses' in email_config:
                    if not isinstance(email_config['to_addresses'], list):
                        errors.append("to_addresses 必须是列表")
                    else:
                        for addr in email_config['to_addresses']:
                            if not ConfigValidator._is_valid_email(addr):
                                errors.append(f"收件人邮箱格式无效: {addr}")

        return errors

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_and_report(config: Dict[str, Any]) -> bool:
        """
        验证配置并打印错误报告

        Args:
            config: 配置字典

        Returns:
            是否验证通过
        """
        errors = ConfigValidator.validate(config)

        if errors:
            print("\n配置验证失败，发现以下错误：")
            print("=" * 60)
            for idx, error in enumerate(errors, 1):
                print(f"{idx}. {error}")
            print("=" * 60)
            return False

        print("✓ 配置验证通过")
        return True
