#!/bin/bash
#
# Automation Hub - 每日自动运行脚本
# 包含：AnyRouter 签到 + Linux.do 论坛总结
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
LOG_FILE="$LOG_DIR/daily_${DATE}.log"

# 开始日志
echo "======================================================" | tee -a "$LOG_FILE"
echo "Automation Hub - 开始执行" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "======================================================" | tee -a "$LOG_FILE"

# 激活 Python 虚拟环境（如果有）
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 1. AnyRouter 签到
echo "" | tee -a "$LOG_FILE"
echo ">>> [1/2] 执行 AnyRouter 签到..." | tee -a "$LOG_FILE"
if python3 "$PROJECT_ROOT/modules/checkin/anyrouter/run.py" >> "$LOG_FILE" 2>&1; then
    echo "✓ AnyRouter 签到完成" | tee -a "$LOG_FILE"
else
    echo "✗ AnyRouter 签到失败" | tee -a "$LOG_FILE"
fi

# 等待一下，避免请求过快
sleep 5

# 2. Linux.do 论坛总结
echo "" | tee -a "$LOG_FILE"
echo ">>> [2/2] 执行 Linux.do 论坛总结..." | tee -a "$LOG_FILE"
if python3 "$PROJECT_ROOT/modules/forum/linuxdo/run.py" >> "$LOG_FILE" 2>&1; then
    echo "✓ Linux.do 论坛总结完成" | tee -a "$LOG_FILE"
else
    echo "✗ Linux.do 论坛总结失败" | tee -a "$LOG_FILE"
fi

# 完成日志
echo "" | tee -a "$LOG_FILE"
echo "======================================================" | tee -a "$LOG_FILE"
echo "Automation Hub - 执行完成" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "======================================================" | tee -a "$LOG_FILE"

# 清理旧日志（保留最近30天）
find "$LOG_DIR" -name "daily_*.log" -type f -mtime +30 -delete

exit 0
