#!/bin/bash
# 自动签到启动脚本

# 切换到项目目录
cd "$(dirname "$0")"

# 激活虚拟环境（如果使用）
# source venv/bin/activate

# 运行签到程序
python3 src/main.py --config config/sites.yaml "$@"
