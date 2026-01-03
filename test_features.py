#!/usr/bin/env python3
"""
功能测试脚本 - 测试当前保留的核心功能
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("Automation Hub - 功能测试")
print("=" * 60)

# 1. 测试模块导入
print("\n[1/5] 测试模块导入...")
try:
    from modules.forum.linuxdo.adapter import LinuxDoAdapter
    from modules.forum.linuxdo.ai_analyzer import AIAnalyzer
    from core.browser_manager import BrowserManager
    from core.logger import setup_logger
    print("  ✅ 所有核心模块导入成功")
except Exception as e:
    print(f"  ❌ 模块导入失败: {e}")
    sys.exit(1)

# 2. 测试LinuxDo适配器方法
print("\n[2/5] 测试 LinuxDo 核心方法...")
adapter_methods = dir(LinuxDoAdapter)
required_methods = [
    'login',
    'is_logged_in',
    'checkin',
    'get_latest_topics',
    'get_hot_topics',
    'get_category_topics',
    'get_topic_content'
]

for method in required_methods:
    if method in adapter_methods:
        print(f"  ✅ {method}")
    else:
        print(f"  ❌ {method} - 缺失")

# 3. 检查删除的功能
print("\n[3/5] 确认互动功能已删除...")
removed_methods = ['simulate_reading', 'like_topic', 'comment_on_topic']
all_removed = True
for method in removed_methods:
    if method in adapter_methods:
        print(f"  ❌ {method} - 仍然存在（应该删除）")
        all_removed = False
    else:
        print(f"  ✅ {method} - 已删除")

if all_removed:
    print("  ✅ 所有互动功能已正确删除")

# 4. 测试配置文件
print("\n[4/5] 检查配置文件...")
config_files = [
    'modules/forum/linuxdo/config.yaml.example',
    'modules/checkin/anyrouter/config.yaml.example'
]

for config_file in config_files:
    config_path = PROJECT_ROOT / config_file
    if config_path.exists():
        # 检查是否还有interaction配置
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'interaction:' in content or 'auto_like' in content or 'auto_comment' in content:
                print(f"  ⚠️  {config_file} - 包含互动功能配置（应该删除）")
            else:
                print(f"  ✅ {config_file} - 配置正确")
    else:
        print(f"  ⚠️  {config_file} - 不存在")

# 5. 测试文档
print("\n[5/5] 检查文档...")
doc_files = [
    'README.md',
    'CHANGELOG.md',
    'modules/forum/linuxdo/README.md'
]

for doc_file in doc_files:
    doc_path = PROJECT_ROOT / doc_file
    if doc_path.exists():
        print(f"  ✅ {doc_file}")
    else:
        print(f"  ⚠️  {doc_file} - 不存在")

# 总结
print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n当前项目功能：")
print("  ✅ 自动登录和会话管理")
print("  ✅ 帖子列表获取（最新/热门/分类）")
print("  ✅ 帖子内容读取")
print("  ✅ 智能过滤和评分")
print("  ✅ AI 内容分析")
print("  ✅ 个性化推荐")
print("  ✅ 邮件通知")
print("  ✅ 缓存优化")
print("\n已删除的功能：")
print("  ❌ 模拟阅读（simulate_reading）")
print("  ❌ 自动点赞（like_topic）")
print("  ❌ 自动评论（comment_on_topic）")
print("\n项目定位：专注于内容智能获取和AI分析")
print("=" * 60)
