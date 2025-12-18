FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Playwright 需要）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install chromium && \
    playwright install-deps chromium

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p logs storage/sessions

# 设置时区（可选）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 运行签到
CMD ["python3", "src/main.py"]
