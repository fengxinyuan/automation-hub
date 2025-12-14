#!/usr/bin/env python3
"""探索 Linux.do 网站结构的脚本"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent))


async def explore_linuxdo():
    """探索 Linux.do 网站结构"""
    print("=" * 60)
    print("开始探索 Linux.do 网站结构")
    print("=" * 60)

    async with async_playwright() as p:
        # 启动浏览器（无头模式）
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )

        # 创建上下文
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        try:
            # 访问首页
            print("\n1. 访问首页...")
            await page.goto('https://linux.do/', wait_until='domcontentloaded', timeout=60000)
            print("   - 页面 DOM 加载完成")

            # 等待一段时间让页面渲染
            await asyncio.sleep(3)

            # 保存首页截图
            await page.screenshot(path='logs/linuxdo_homepage.png')
            print("   - 首页截图已保存: logs/linuxdo_homepage.png")

            # 获取页面标题
            title = await page.title()
            print(f"   - 页面标题: {title}")

            # 检查是否是 Discourse 论坛
            is_discourse = await page.evaluate("""
                () => {
                    return typeof Discourse !== 'undefined' ||
                           document.querySelector('meta[name="discourse_theme_id"]') !== null;
                }
            """)
            print(f"   - 是否是 Discourse 论坛: {is_discourse}")

            # 查找登录按钮
            print("\n2. 查找登录入口...")
            login_selectors = [
                'button:has-text("登录")',
                'button:has-text("Login")',
                'a:has-text("登录")',
                'a:has-text("Login")',
                '.login-button',
                '#login-button'
            ]

            for selector in login_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000, state='visible')
                    if element:
                        text = await element.text_content()
                        print(f"   - 找到登录按钮: {selector} (文本: {text})")
                        break
                except:
                    continue

            # 查找帖子列表
            print("\n3. 分析首页帖子列表...")
            topics = await page.evaluate("""
                () => {
                    const topics = [];
                    // Discourse 论坛的帖子通常在 .topic-list-item 或 .latest-topic-list-item 中
                    const topicElements = document.querySelectorAll('.topic-list-item, [data-topic-id]');
                    topicElements.forEach((el, idx) => {
                        if (idx < 5) {  // 只获取前5个
                            const titleEl = el.querySelector('.title, .topic-title, a.title');
                            const title = titleEl ? titleEl.textContent.trim() : '';
                            const link = titleEl ? titleEl.getAttribute('href') : '';
                            topics.push({title, link});
                        }
                    });
                    return topics;
                }
            """)

            if topics:
                print(f"   - 找到 {len(topics)} 个帖子:")
                for i, topic in enumerate(topics, 1):
                    print(f"     {i}. {topic['title'][:50]}...")
            else:
                print("   - 未找到帖子（可能需要登录或使用其他选择器）")

            # 查找导航菜单
            print("\n4. 分析导航结构...")
            nav_items = await page.evaluate("""
                () => {
                    const items = [];
                    const navSelectors = ['nav a', '.navigation a', 'header a'];
                    for (const selector of navSelectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            const text = el.textContent.trim();
                            const href = el.getAttribute('href');
                            if (text && href && text.length < 50) {
                                items.push({text, href});
                            }
                        });
                        if (items.length > 0) break;
                    }
                    return items.slice(0, 10);
                }
            """)

            if nav_items:
                print(f"   - 找到 {len(nav_items)} 个导航项:")
                for item in nav_items[:10]:
                    print(f"     - {item['text']}: {item['href']}")

            print("\n5. 探索完成")

        except Exception as e:
            print(f"\n错误: {str(e)}")
            await page.screenshot(path='logs/linuxdo_error.png')
            print("   - 错误截图已保存: logs/linuxdo_error.png")

        finally:
            await browser.close()
            print("\n" + "=" * 60)
            print("探索完成")
            print("=" * 60)


if __name__ == '__main__':
    asyncio.run(explore_linuxdo())
