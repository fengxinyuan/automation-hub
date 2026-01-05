#!/bin/bash
#
# Linux.do 自动阅读脚本（每10分钟执行）
# 轻量级版本，只做阅读不做AI分析
#

set -e

# 项目根目录
PROJECT_ROOT="/root/automation-hub"
cd "$PROJECT_ROOT"

# 日志目录
LOG_DIR="$PROJECT_ROOT/storage/logs"
mkdir -p "$LOG_DIR"

# 日志文件（按日期）
DATE=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/auto_read_${DATE}.log"

# 激活 Python 虚拟环境（如果有）
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 执行自动阅读
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始自动阅读" >> "$LOG_FILE"
python3 "$PROJECT_ROOT/modules/forum/linuxdo/read_auto.py" >> "$LOG_FILE" 2>&1

# 记录结果
if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 自动阅读完成" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 自动阅读失败" >> "$LOG_FILE"
fi

# 清理旧日志（保留最近7天）
find "$LOG_DIR" -name "auto_read_*.log" -type f -mtime +7 -delete

exit 0
