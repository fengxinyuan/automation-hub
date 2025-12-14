#!/bin/bash
# Linux.do 论坛自动化快速测试脚本

echo "=========================================="
echo "Linux.do 论坛自动化测试"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi
echo "✅ Python3 已安装"

# 检查依赖
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "⚠️  警告: Playwright 未安装，正在安装..."
    pip3 install -r requirements.txt
    playwright install chromium
fi
echo "✅ 依赖已就绪"

# 检查配置文件
if [ ! -f "config/sites.yaml" ]; then
    echo "❌ 错误: config/sites.yaml 不存在"
    exit 1
fi
echo "✅ 配置文件存在"

echo ""
echo "=========================================="
echo "开始测试"
echo "=========================================="
echo ""

# 1. 测试模式 - 验证配置
echo "1️⃣  验证配置文件..."
python3 src/main.py --site linuxdo --dry-run
if [ $? -ne 0 ]; then
    echo "❌ 配置验证失败"
    exit 1
fi
echo "✅ 配置验证成功"
echo ""

# 2. 实际运行
echo "2️⃣  执行 Linux.do 论坛动态获取..."
python3 src/main.py --site linuxdo

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 测试完成"
    echo "=========================================="
    echo ""
    echo "📋 查看结果："
    echo "   - 日志文件: logs/checkin.log"
    echo "   - 截图文件: logs/linuxdo_*.png"
    echo ""
    echo "📧 如果启用了邮件通知，请检查收件箱"
    echo ""
    echo "🔁 设置定时任务："
    echo "   crontab -e"
    echo "   # 添加: 0 8 * * * cd $(pwd) && python3 src/main.py --site linuxdo >> logs/cron.log 2>&1"
else
    echo ""
    echo "=========================================="
    echo "❌ 测试失败"
    echo "=========================================="
    echo ""
    echo "🔍 排查步骤："
    echo "   1. 检查配置文件中的用户名和密码"
    echo "   2. 查看日志文件: logs/checkin.log"
    echo "   3. 查看截图文件: logs/linuxdo_*.png"
    echo "   4. 查看详细文档: docs/LINUXDO_GUIDE.md"
    exit 1
fi
