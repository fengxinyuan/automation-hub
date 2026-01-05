#!/usr/bin/env python3
"""
Linux.do 手动登录并导出 Cookies
用于绕过 Cloudflare 验证
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def manual_login_and_export():
    """手动登录并导出 cookies"""
    print("=" * 60)
    print("Linux.do 手动登录工具")
    print("=" * 60)
    print()
    print("说明：")
    print("1. 浏览器会打开 Linux.do 登录页面（非无头模式）")
    print("2. 请手动完成 Cloudflare 验证")
    print("3. 手动登录到你的账号")
    print("4. 登录成功后，按回车键导出 cookies")
    print("5. Cookies 将保存到配置文件，供自动化脚本使用")
    print()
    input("按回车键开始...")

    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便手动操作）
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        print("\n正在打开 Linux.do...")
        await page.goto('https://linux.do', wait_until='domcontentloaded')

        print("\n✓ 页面已打开")
        print("\n请在浏览器中完成以下操作：")
        print("  1. 通过 Cloudflare 验证")
        print("  2. 点击右上角的「登录」按钮")
        print("  3. 输入你的邮箱和密码")
        print("  4. 完成登录")
        print()
        print("登录成功后，回到这里按回车键继续...")
        input()

        # 获取当前页面的 cookies
        cookies = await context.cookies()

        # 检查是否有登录标识
        has_auth = any(c['name'] == '_t' for c in cookies)

        if not has_auth:
            print("\n⚠️  警告：未检测到登录 cookie (_t)")
            print("请确认你已经成功登录！")
            choice = input("\n是否仍要导出 cookies？(y/n): ")
            if choice.lower() != 'y':
                print("已取消")
                await browser.close()
                return

        # 保存 cookies 到配置文件
        config_dir = PROJECT_ROOT / 'modules' / 'forum' / 'linuxdo'
        cookies_file = config_dir / 'cookies.json'

        # 只保存 linux.do 相关的 cookies
        linuxdo_cookies = [
            c for c in cookies
            if 'linux.do' in c.get('domain', '') or
               'cloudflare' in c.get('domain', '').lower()
        ]

        cookies_data = {
            'cookies': linuxdo_cookies,
            'exported_at': asyncio.get_event_loop().time(),
            'note': '从浏览器手动登录导出，用于自动化脚本'
        }

        with open(cookies_file, 'w', encoding='utf-8') as f:
            json.dump(cookies_data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Cookies 已导出到: {cookies_file}")
        print(f"  共 {len(linuxdo_cookies)} 个 cookies")
        print(f"  包含登录 token: {'是' if has_auth else '否'}")

        # 显示关键 cookies
        print("\n关键 Cookies:")
        for c in linuxdo_cookies:
            if c['name'] in ['_t', 'cf_clearance', '__cf_bm']:
                print(f"  - {c['name']}: {c['value'][:30]}...")

        await browser.close()

        print("\n" + "=" * 60)
        print("✓ 完成！")
        print("\n现在你可以运行自动化脚本，它会自动使用这些 cookies")
        print("=" * 60)


if __name__ == '__main__':
    asyncio.run(manual_login_and_export())
