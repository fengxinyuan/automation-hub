"""AnyRouter 站点适配器"""
import sys
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

    def __init__(self, site_url: str, username: str, password: str, logger=None):
        super().__init__(
            site_name="anyrouter",
            site_url=site_url,
            username=username,
            password=password,
            logger=logger
        )

    async def is_logged_in(self) -> bool:
        """
        检查是否已登录

        通过访问用户中心或检查特定元素来判断
        """
        try:
            # 访问首页
            await self.page.goto(self.site_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)

            # 等待页面稳定（等待网络请求完成）
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

            # 方法1: 检查 URL 是否在登录页
            current_url = self.page.url
            if '/auth/login' in current_url or '/login' in current_url:
                return False

            # 方法2: 尝试查找用户相关元素（可能需要调整选择器）
            user_indicators = [
                'a[href*="user"]',
                'a[href*="logout"]',
                '.user-info',
                '.user-menu',
                '#user-menu'
            ]

            for selector in user_indicators:
                try:
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=3000,  # 每个选择器只等待3秒
                        state='visible'
                    )
                    if element:
                        self.logger.debug(f"找到登录状态指示器: {selector}")
                        return True
                except:
                    continue

            # 方法3: 检查是否有登录按钮（如果有说明未登录）
            try:
                login_button = await self.page.wait_for_selector(
                    'a[href*="login"]',
                    timeout=2000,
                    state='visible'
                )
                if login_button:
                    return False
            except:
                pass

            # 默认假设已登录（由于有会话恢复）
            self.logger.warning("无法确定登录状态，假设已登录")
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
            await self.page.goto(self.site_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

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
                        await element.click()
                        signin_clicked = True
                        # 等待页面跳转到登录页
                        await self.page.wait_for_load_state('domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
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
                        await self.page.goto(login_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
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
                        await element.fill(self.username)
                        self.logger.debug(f"使用选择器填写用户名: {selector}")
                        username_filled = True
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
                        await element.fill(self.password)
                        self.logger.debug(f"使用选择器填写密码: {selector}")
                        password_filled = True
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
            await self.page.goto(console_url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
            await self.page.wait_for_load_state('networkidle', timeout=self.PAGE_LOAD_TIMEOUT)

            await self.take_screenshot("console_page")

            # 查找余额信息
            balance_selectors = [
                'div:has-text("当前余额") + div',  # 余额文本下方的 div
                'div.text-lg.font-semibold',  # 根据类名查找
                'div:has-text("$")',  # 包含美元符号的元素
            ]

            balance_text = None
            for selector in balance_selectors:
                try:
                    # 等待元素出现
                    await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and '$' in text:
                            balance_text = text.strip()
                            self.logger.info(f"找到余额: {balance_text}")
                            break
                    if balance_text:
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
