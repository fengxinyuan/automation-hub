"""站点适配器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from playwright.async_api import BrowserContext, Page
import asyncio
import logging


class CheckinResult:
    """签到结果"""

    def __init__(
        self,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化签到结果

        Args:
            success: 是否成功
            message: 结果消息
            details: 额外详情
        """
        self.success = success
        self.message = message
        self.details = details or {}

    def __str__(self):
        status = "成功" if self.success else "失败"
        return f"[{status}] {self.message}"


class BaseAdapter(ABC):
    """站点适配器抽象基类"""

    def __init__(
        self,
        site_name: str,
        site_url: str,
        username: str,
        password: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化适配器

        Args:
            site_name: 站点名称
            site_url: 站点 URL
            username: 用户名
            password: 密码
            logger: 日志记录器
        """
        self.site_name = site_name
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def run(self, context: BrowserContext) -> CheckinResult:
        """
        执行完整的签到流程

        Args:
            context: 浏览器上下文

        Returns:
            签到结果
        """
        self.context = context
        self.page = await context.new_page()

        try:
            # 检查是否已登录
            is_logged_in = await self.is_logged_in()

            if not is_logged_in:
                self.logger.info(f"[{self.site_name}] 用户 {self.username} 未登录，开始登录")
                login_result = await self._retry_operation(self.login, max_retries=3)
                if not login_result:
                    return CheckinResult(False, "登录失败")
                self.logger.info(f"[{self.site_name}] 登录成功")
            else:
                self.logger.info(f"[{self.site_name}] 用户 {self.username} 已登录")

            # 执行签到
            self.logger.info(f"[{self.site_name}] 开始签到")
            result = await self._retry_operation(self.checkin, max_retries=3)

            if result:
                self.logger.info(f"[{self.site_name}] {result}")
                return result
            else:
                return CheckinResult(False, "签到失败")

        except Exception as e:
            self.logger.error(f"[{self.site_name}] 执行出错: {str(e)}", exc_info=True)
            return CheckinResult(False, f"执行出错: {str(e)}")

        finally:
            if self.page:
                await self.page.close()

    async def _retry_operation(self, operation, max_retries: int = 3):
        """
        重试操作（带指数退避）

        Args:
            operation: 要执行的异步操作
            max_retries: 最大重试次数

        Returns:
            操作结果
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                self.logger.debug(f"尝试执行操作 (第 {attempt + 1}/{max_retries} 次)")
                result = await operation()
                if attempt > 0:
                    self.logger.info(f"操作在第 {attempt + 1} 次尝试后成功")
                return result

            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"操作失败 (尝试 {attempt + 1}/{max_retries}): {type(e).__name__}: {str(e)}"
                )

                # 如果不是最后一次尝试，则等待后重试
                if attempt < max_retries - 1:
                    # 指数退避：2^attempt 秒（1秒、2秒、4秒...）
                    wait_time = 2 ** attempt
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)

                    # 在重试前截图（用于调试）
                    if self.page:
                        await self.take_screenshot(f"retry_{attempt + 1}")

        # 所有重试都失败
        self.logger.error(f"操作在 {max_retries} 次尝试后仍然失败")
        raise last_exception

    @abstractmethod
    async def login(self) -> bool:
        """
        登录站点

        Returns:
            是否登录成功
        """
        pass

    @abstractmethod
    async def checkin(self) -> CheckinResult:
        """
        执行签到

        Returns:
            签到结果
        """
        pass

    @abstractmethod
    async def is_logged_in(self) -> bool:
        """
        检查是否已登录

        Returns:
            是否已登录
        """
        pass

    async def take_screenshot(self, name: str):
        """
        截图用于调试

        Args:
            name: 截图文件名
        """
        if self.page:
            try:
                screenshot_path = f"logs/{self.site_name}_{self.username}_{name}.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.debug(f"截图已保存: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"截图失败: {str(e)}")
