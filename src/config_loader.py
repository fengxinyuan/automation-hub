"""配置加载模块"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from src.config_validator import ConfigValidator


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

        # 加载环境变量
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print(f"已加载环境变量文件: {env_file}")

    def load(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
            ValueError: 配置验证失败
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self._validate()
        self._set_defaults()

        # 验证配置完整性
        if not ConfigValidator.validate_and_report(self.config):
            raise ValueError("配置验证失败，请检查上述错误")

        return self.config

    def _validate(self):
        """验证配置的有效性"""
        if 'sites' not in self.config:
            raise ValueError("配置文件缺少 'sites' 字段")

        for site_name, site_config in self.config['sites'].items():
            if 'url' not in site_config:
                raise ValueError(f"站点 {site_name} 缺少 'url' 字段")

            if 'accounts' not in site_config:
                raise ValueError(f"站点 {site_name} 缺少 'accounts' 字段")

            for idx, account in enumerate(site_config['accounts']):
                if 'username' not in account or 'password' not in account:
                    raise ValueError(
                        f"站点 {site_name} 的第 {idx + 1} 个账号缺少 username 或 password"
                    )

    def _set_defaults(self):
        """设置默认值并从环境变量覆盖"""
        # 通知默认配置
        if 'notifications' not in self.config:
            self.config['notifications'] = {}

        notifications = self.config['notifications']

        # 日志默认配置
        if 'log' not in notifications:
            notifications['log'] = {}
        notifications['log'].setdefault('enabled', True)
        notifications['log'].setdefault('level', os.getenv('LOG_LEVEL', 'INFO'))

        # 邮件默认配置
        if 'email' not in notifications:
            notifications['email'] = {}

        # 从环境变量读取邮件配置
        email_config = notifications['email']
        email_config.setdefault('enabled', os.getenv('EMAIL_ENABLED', 'false').lower() == 'true')

        if os.getenv('EMAIL_SMTP_SERVER'):
            email_config['smtp_server'] = os.getenv('EMAIL_SMTP_SERVER')
        if os.getenv('EMAIL_SMTP_PORT'):
            email_config['smtp_port'] = int(os.getenv('EMAIL_SMTP_PORT'))
        if os.getenv('EMAIL_USERNAME'):
            email_config['username'] = os.getenv('EMAIL_USERNAME')
        if os.getenv('EMAIL_PASSWORD'):
            email_config['password'] = os.getenv('EMAIL_PASSWORD')
        if os.getenv('EMAIL_USE_TLS'):
            email_config['use_tls'] = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        if os.getenv('EMAIL_TO_ADDRESSES'):
            email_config['to_addresses'] = [
                addr.strip() for addr in os.getenv('EMAIL_TO_ADDRESSES').split(',')
            ]

        # 账号默认启用，并从环境变量读取密码
        for site_name, site_config in self.config['sites'].items():
            for idx, account in enumerate(site_config['accounts']):
                account.setdefault('enabled', True)

                # 从环境变量读取密码（优先级高于配置文件）
                env_password_key = f"SITE_{site_name.upper()}_{idx}_PASSWORD"
                env_password = os.getenv(env_password_key)
                if env_password:
                    account['password'] = env_password

    def get_sites(self) -> Dict[str, Any]:
        """获取所有站点配置"""
        return self.config.get('sites', {})

    def get_enabled_accounts(self, site_name: str) -> List[Dict[str, Any]]:
        """
        获取指定站点的已启用账号

        Args:
            site_name: 站点名称

        Returns:
            已启用的账号列表
        """
        site_config = self.config['sites'].get(site_name, {})
        accounts = site_config.get('accounts', [])
        return [acc for acc in accounts if acc.get('enabled', True)]

    def get_notification_config(self) -> Dict[str, Any]:
        """获取通知配置"""
        return self.config.get('notifications', {})
