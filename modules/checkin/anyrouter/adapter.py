"""AnyRouter 站点适配器"""
import sys
import re
import random
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.base_adapter import BaseAdapter, CheckinResult
import asyncio


class AnyrouterAdapter(BaseAdapter):
    """AnyRouter 站点适配器

    注意：由于 anyrouter.top 有反爬虫保护，实际的选择器可能需要根据页面结构调整。
    建议首次运行时使用 --debug 模式查看页面结构。
    """

    # 页面加载超时配置（毫秒）
    PAGE_LOAD_TIMEOUT = 30000
    ELEMENT_WAIT_TIMEOUT = 10000  # 元素查找超时

    def __init__(self, site_url: str, username: str, password: str, logger=None, anti_detection_config: dict = None):
        super().__init__(
            site_name="anyrouter",
            site_url=site_url,
            username=username,
            password=password,
            logger=logger
        )
        # 防检测配置
        self.anti_detection = anti_detection_config or {}
        self.action_delay = self.anti_detection.get('action_delay', {'min': 1, 'max': 3})
        self.typing_delay = self.anti_detection.get('typing_delay', {'min': 0.1, 'max': 0.3})

    async def _random_delay(self, delay_config: dict = None):
        """随机延迟（模拟人类行为）"""
        if delay_config is None:
            delay_config = self.action_delay
        delay = random.uniform(delay_config['min'], delay_config['max'])
        await asyncio.sleep(delay)

    async def _human_type(self, element, text: str):
        """模拟人类输入（逐字符输入）"""
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(self.typing_delay['min'], self.typing_delay['max']))

    async def _goto_with_retry(self, url: str, max_retries: int = 3, **kwargs):
        """
        带重试机制的页面跳转，处理 SSL 错误

        Args:
            url: 目标 URL
            max_retries: 最大重试次数
            **kwargs: 传递给 page.goto 的其他参数

        Returns:
            page.goto 的返回值

        Raises:
            最后一次重试失败的异常
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.page.goto(url, **kwargs)
            except Exception as e:
                error_str = str(e)
                # 检查是否是 SSL 相关错误
                is_ssl_error = any(err in error_str for err in [
                    'ERR_SSL_VERSION_OR_CIPHER_MISMATCH',
                    'ERR_SSL_PROTOCOL_ERROR',
                    'ERR_CERT_',
                    'SSL',
                    'ERR_CONNECTION_CLOSED'
                ])

                if is_ssl_error and attempt < max_retries - 1:
                    self.logger.warning(f"SSL 错误，第 {attempt + 1}/{max_retries} 次重试: {error_str}")
                    await asyncio.sleep(2 * (attempt + 1))  # 递增等待时间
                    continue
                else:
                    last_error = e
                    break

        if last_error:
            raise last_error

    async def is_logged_in(self) -> bool:
        """
        检查是否已登录

        通过访问控制台页面判断登录状态
        """
        try:
            # 直接访问控制台页面（需要登录才能访问）
            console_url = f"{self.site_url}/console"
            await self._goto_with_retry(console_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)

            # 等待页面稳定
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

            # 方法1: 检查 URL 是否被重定向到登录页
            current_url = self.page.url
            if '/auth/login' in current_url or '/login' in current_url:
                self.logger.debug("URL 重定向到登录页，未登录")
                return False

            # 方法2: 检查页面内容是否包含控制台相关元素
            page_content = await self.page.content()

            # 检查控制台关键字
            console_keywords = ['Console', 'Dashboard', 'Account Data', '账户数据', 'Current balance']
            has_console_content = any(keyword in page_content for keyword in console_keywords)

            if has_console_content:
                self.logger.debug("检测到控制台页面内容，已登录")
                return True

            # 方法3: 检查是否有登录表单（如果有说明未登录）
            try:
                login_form = await self.page.query_selector('input[type="password"]')
                if login_form:
                    self.logger.debug("检测到登录表单，未登录")
                    return False
            except:
                pass

            # 如果能访问控制台页面且没有重定向，默认认为已登录
            self.logger.debug("页面未重定向到登录页，假设已登录")
            return True

        except Exception as e:
            self.logger.error(f"检查登录状态失败: {str(e)}")
            return False

    async def login(self) -> bool:
        """
        执行登录操作

        注意：选择器需要根据实际页面调整
        """
        try:
            # 先访问首页
            self.logger.info(f"访问首页: {self.site_url}")
            await self._goto_with_retry(self.site_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

            # 随机延迟，模拟人类浏览
            await self._random_delay()

            # 尝试关闭可能的弹窗/公告
            popup_close_selectors = [
                'button:has-text("Close Notice")',
                'button:has-text("Close Today")',
                'button:has-text("关闭")',
                'button.close',
                '.modal-close',
                '[aria-label="Close"]',
                'button[class*="close"]'
            ]

            for selector in popup_close_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                    if element:
                        self.logger.info(f"关闭弹窗: {selector}")
                        await element.click()
                        await asyncio.sleep(0.5)  # 短暂等待弹窗关闭动画
                        break
                except:
                    continue

            # 查找并点击 Sign In 按钮
            signin_selectors = [
                'a:has-text("Sign In")',
                'a:has-text("Sign in")',
                'a:has-text("登录")',
                'button:has-text("Sign In")',
                'button:has-text("登录")',
                'a[href*="login"]',
                'a[href*="signin"]'
            ]

            signin_clicked = False
            for selector in signin_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000, state='visible')
                    if element:
                        self.logger.info(f"点击登录按钮: {selector}")
                        await self._random_delay()  # 点击前随机延迟
                        await element.click()
                        signin_clicked = True
                        # 等待页面跳转到登录页
                        await self.page.wait_for_load_state('domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
                        await self._random_delay()  # 页面加载后延迟
                        break
                except:
                    continue

            if not signin_clicked:
                self.logger.warning("未找到Sign In按钮，尝试直接访问登录页面")
                # 尝试常见的登录路径
                login_paths = ['/auth/login', '/login', '/signin', '/user/login']
                for path in login_paths:
                    try:
                        login_url = f"{self.site_url}{path}"
                        await self._goto_with_retry(login_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
                        await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)
                        # 检查是否是404
                        page_content = await self.page.content()
                        if 'not found' not in page_content.lower():
                            break
                    except:
                        continue

            # 截图用于调试
            await self.take_screenshot("before_login")

            # 检查是否需要点击"使用邮箱/用户名登录"按钮
            email_login_selectors = [
                'button:has-text("Sign in with Email or Username")',
                'button:has-text("Email or Username")',
                'button:has-text("邮箱登录")',
                'button:has-text("邮箱或用户名")'
            ]

            for selector in email_login_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                    if element:
                        self.logger.info(f"点击邮箱登录按钮: {selector}")
                        await element.click()
                        await asyncio.sleep(1)  # 等待表单显示
                        break
                except:
                    continue

            # 可能的用户名字段选择器
            username_selectors = [
                'input[name="email"]',
                'input[name="username"]',
                'input[type="email"]',
                'input[type="text"]',
                '#email',
                '#username'
            ]

            # 填写用户名
            username_filled = False
            for selector in username_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        # 先清空输入框
                        await element.click()
                        await self._random_delay({'min': 0.3, 'max': 0.8})
                        await element.fill('')
                        # 使用人类行为模拟输入
                        await self._human_type(element, self.username)
                        self.logger.debug(f"使用选择器填写用户名: {selector}")
                        username_filled = True
                        await self._random_delay({'min': 0.5, 'max': 1.5})
                        break
                except:
                    continue

            if not username_filled:
                self.logger.error("无法找到用户名输入框")
                await self.take_screenshot("login_failed_no_username")
                return False

            # 可能的密码字段选择器
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]

            # 填写密码
            password_filled = False
            for selector in password_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        # 先清空输入框
                        await element.click()
                        await self._random_delay({'min': 0.3, 'max': 0.8})
                        await element.fill('')
                        # 使用人类行为模拟输入
                        await self._human_type(element, self.password)
                        self.logger.debug(f"使用选择器填写密码: {selector}")
                        password_filled = True
                        await self._random_delay({'min': 0.5, 'max': 1.5})
                        break
                except:
                    continue

            if not password_filled:
                self.logger.error("无法找到密码输入框")
                await self.take_screenshot("login_failed_no_password")
                return False

            # 可能的登录按钮选择器
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("Login")',
                '.btn-login',
                '#login-button'
            ]

            # 点击登录按钮
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        await element.click()
                        self.logger.debug(f"点击登录按钮: {selector}")
                        submit_clicked = True
                        break
                except:
                    continue

            if not submit_clicked:
                self.logger.error("无法找到登录按钮")
                await self.take_screenshot("login_failed_no_button")
                return False

            # 等待登录完成（等待页面跳转）
            try:
                # 等待导航完成或特定元素出现
                await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)
                await self.take_screenshot("after_login")

                # 检查是否登录成功
                is_success = await self.is_logged_in()

                if is_success:
                    self.logger.info("登录成功")
                    return True
                else:
                    self.logger.error("登录可能失败，请检查截图")
                    return False

            except Exception as e:
                self.logger.error(f"等待登录完成时出错: {str(e)}")
                await self.take_screenshot("login_error")
                return False

        except Exception as e:
            self.logger.error(f"登录过程出错: {str(e)}")
            await self.take_screenshot("login_exception")
            return False

    async def checkin(self) -> CheckinResult:
        """
        执行签到操作

        anyrouter 不需要点击签到按钮，只需要获取账户余额信息
        """
        try:
            # 访问控制台页面
            console_url = f"{self.site_url}/console"
            self.logger.info(f"访问控制台: {console_url}")
            await self._goto_with_retry(console_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

            await self.take_screenshot("console_page")

            # 获取页面内容
            page_content = await self.page.content()

            # 使用正则表达式提取余额
            # 匹配格式：Current balance$424.96 或 当前余额$100.00
            balance_patterns = [
                r'Current balance\$?([\d,.]+)',  # Current balance$424.96
                r'当前余额\$?([\d,.]+)',           # 当前余额$100.00
                r'balance[:\s]*\$?([\d,.]+)',    # balance: $100.00
                r'Balance[:\s]*\$?([\d,.]+)',    # Balance: $100.00
            ]

            balance_text = None
            for pattern in balance_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    balance_value = match.group(1)
                    balance_text = f"${balance_value}"
                    self.logger.info(f"提取到余额: {balance_text}")
                    break

            if not balance_text:
                # 尝试从页面元素中提取
                balance_selectors = [
                    'div:has-text("Current balance") + div',
                    'div:has-text("当前余额") + div',
                ]

                for selector in balance_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=3000, state='visible')
                        if element:
                            text = await element.text_content()
                            # 从文本中提取金额
                            match = re.search(r'\$?([\d,.]+)', text)
                            if match:
                                balance_text = f"${match.group(1)}"
                                self.logger.info(f"从元素提取到余额: {balance_text}")
                                break
                    except Exception as e:
                        self.logger.debug(f"选择器 {selector} 失败: {e}")
                        continue

            if balance_text:
                return CheckinResult(
                    True,
                    f"登录成功，当前余额: {balance_text}",
                    {"balance": balance_text}
                )
            else:
                # 即使没找到余额，只要能访问控制台就算成功
                self.logger.warning("未找到余额信息，但已成功访问控制台")
                return CheckinResult(
                    True,
                    "登录成功，已访问控制台",
                    {"balance": "未获取到"}
                )

        except Exception as e:
            self.logger.error(f"获取账户信息出错: {str(e)}")
            await self.take_screenshot("checkin_exception")
            return CheckinResult(False, f"获取账户信息出错: {str(e)}")
