"""配置加载模块"""
import yaml
from pathlib import Path
from typing import Dict, Any, List


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

    def load(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self._validate()
        self._set_defaults()

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
        """设置默认值"""
        # 通知默认配置
        if 'notifications' not in self.config:
            self.config['notifications'] = {}

        notifications = self.config['notifications']

        # 日志默认配置
        if 'log' not in notifications:
            notifications['log'] = {}
        notifications['log'].setdefault('enabled', True)
        notifications['log'].setdefault('level', 'INFO')

        # 邮件默认配置
        if 'email' not in notifications:
            notifications['email'] = {}
        notifications['email'].setdefault('enabled', False)

        # 账号默认启用
        for site_config in self.config['sites'].values():
            for account in site_config['accounts']:
                account.setdefault('enabled', True)

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
