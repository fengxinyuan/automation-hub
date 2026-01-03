"""浏览器管理模块"""
import asyncio
import os
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright


class BrowserManager:
    """Playwright 浏览器管理器"""

    def __init__(self, storage_dir: str = "storage/sessions", headless: bool = True):
        """
        初始化浏览器管理器

        Args:
            storage_dir: 会话存储目录
            headless: 是否无头模式运行
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

        # 自动检测代理配置
        self.proxy = self._detect_proxy()

    def _detect_proxy(self) -> Optional[dict]:
        """
        自动检测系统代理配置

        优先级：HTTP_PROXY > HTTPS_PROXY > http_proxy > https_proxy

        Returns:
            代理配置字典或 None
        """
        proxy_url = (
            os.getenv('HTTP_PROXY') or
            os.getenv('HTTPS_PROXY') or
            os.getenv('http_proxy') or
            os.getenv('https_proxy')
        )

        if proxy_url:
            print(f"[BrowserManager] 检测到代理: {proxy_url}")
            return {"server": proxy_url}
        return None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()

        # 浏览器启动参数
        launch_options = {
            "headless": self.headless,
            "args": [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        }

        # 如果有代理配置，添加代理
        if self.proxy:
            launch_options["proxy"] = self.proxy
            print(f"[BrowserManager] 使用代理: {self.proxy['server']}")

        self.browser = await self.playwright.chromium.launch(**launch_options)

    async def create_context(
        self, site_name: str, user_id: str, load_session: bool = True
    ) -> BrowserContext:
        """
        创建或恢复浏览器上下文

        Args:
            site_name: 站点名称
            user_id: 用户标识
            load_session: 是否加载已保存的会话

        Returns:
            浏览器上下文
        """
        if not self.browser:
            raise RuntimeError("浏览器未启动，请先调用 start()")

        session_dir = self.storage_dir / f"{site_name}_{user_id}"

        # 如果存在已保存的会话且需要加载，则恢复
        if load_session and session_dir.exists():
            try:
                context = await self.browser.new_context(
                    storage_state=str(session_dir / "state.json"),
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                )
                # 添加反检测脚本
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                    window.chrome = {runtime: {}};
                """)
                return context
            except Exception as e:
                print(f"加载会话失败: {e}，将创建新会话")

        # 创建新上下文
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
        )

        # 添加反检测脚本
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            window.chrome = {runtime: {}};
        """)

        return context

    async def save_context(
        self, context: BrowserContext, site_name: str, user_id: str
    ):
        """
        保存浏览器上下文

        Args:
            context: 浏览器上下文
            site_name: 站点名称
            user_id: 用户标识
        """
        session_dir = self.storage_dir / f"{site_name}_{user_id}"
        session_dir.mkdir(parents=True, exist_ok=True)

        try:
            await context.storage_state(path=str(session_dir / "state.json"))
        except Exception as e:
            print(f"保存会话失败: {e}")

    async def close(self):
        """关闭浏览器和 Playwright"""
        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
