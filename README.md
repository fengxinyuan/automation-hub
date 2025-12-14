# 自动签到系统

一个功能强大、易于扩展的自动登录签到系统，使用 Python + Playwright 实现浏览器自动化。

## 🎯 支持的站点

- **anyrouter** - AnyRouter 路由器服务
- **linuxdo** - Linux.do 论坛（支持帖子推送）

## ✨ 功能特性

- **多站点支持**: 可扩展架构，轻松添加新站点适配器
- **多账号管理**: 通过 YAML 配置文件管理多个站点和账号
- **论坛帖子推送**: Linux.do 支持自动获取最新帖子和热门话题（无需浏览即知论坛动态）
- **智能并发**: 支持并发执行多账号签到，带随机延迟避免被检测
- **会话保持**: 自动保存浏览器会话，减少登录频率
- **智能等待**: 使用 Playwright 智能等待机制，提高执行效率
- **反爬虫应对**: 使用真实浏览器环境，模拟人工操作
- **环境变量**: 支持通过环境变量管理敏感信息
- **配置验证**: 自动验证配置文件完整性和有效性
- **通知系统**: 支持日志文件和邮件通知（包含帖子摘要）
- **错误重试**: 智能重试机制，带指数退避策略
- **Docker 支持**: 提供 Docker 和 Docker Compose 配置，简化部署
- **定时执行**: 配合 cron 实现每日自动签到

## 📋 项目结构

```
auto-checkin/
├── config/
│   ├── sites.yaml           # 站点和账号配置
│   └── sites.yaml.example   # 配置示例
├── src/
│   ├── main.py              # 主程序
│   ├── config_loader.py     # 配置加载
│   ├── config_validator.py  # 配置验证
│   ├── browser_manager.py   # 浏览器管理
│   ├── adapters/            # 站点适配器
│   │   ├── base_adapter.py
│   │   └── anyrouter.py
│   └── notifiers/           # 通知模块
│       ├── logger.py
│       └── email.py
├── storage/sessions/        # 浏览器会话存储
├── logs/                    # 日志文件
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像配置
├── docker-compose.yml       # Docker Compose 配置
├── run.sh                   # 启动脚本
└── README.md
```

## 🚀 快速开始

### 方式一：本地运行

#### 1. 克隆项目

```bash
cd auto-checkin
```

#### 2. 安装依赖

建议使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

#### 3. 配置

**方式 A: 使用配置文件（推荐用于测试）**

编辑 `config/sites.yaml`:

```yaml
sites:
  anyrouter:
    url: https://anyrouter.top
    accounts:
      - username: your-email@example.com
        password: your-password
        enabled: true

  linuxdo:
    url: https://linux.do
    accounts:
      - username: your-username-or-email
        password: your-password
        enabled: true  # 启用以获取论坛动态推送

notifications:
  log:
    enabled: true
    level: INFO

  email:
    enabled: true  # 建议启用，以接收帖子推送
    smtp_server: smtp.gmail.com
    smtp_port: 587
    use_tls: true
    username: your-email@gmail.com
    password: your-app-password
    to_addresses:
      - notify@example.com
```

**方式 B: 使用环境变量（推荐用于生产）**

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填写实际值
nano .env
```

环境变量配置示例：

```bash
# 邮件通知
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO_ADDRESSES=notify@example.com

# 站点密码（可选，优先级高于配置文件）
SITE_ANYROUTER_0_PASSWORD=your-password-here
```

#### 4. 运行

```bash
# 直接运行（所有启用的站点）
python3 src/main.py

# 使用启动脚本
./run.sh

# 指定配置文件
python3 src/main.py --config config/sites.yaml

# 指定站点
python3 src/main.py --site anyrouter
python3 src/main.py --site linuxdo  # Linux.do 论坛

# 调试模式（显示浏览器窗口）
python3 src/main.py --debug

# 测试模式（不实际执行）
python3 src/main.py --dry-run
```

### 📱 Linux.do 论坛特别说明

Linux.do 论坛适配器不是传统的签到功能，而是**自动获取论坛动态并推送**：

- 📰 自动获取最新帖子（默认10条）
- 🔥 自动获取热门话题（默认5条）
- 📧 通过邮件推送帖子摘要（包含标题、作者、分类、回复数、浏览数、链接）
- ⚡ 无需浏览论坛即可了解最新动态

**查看详细文档**: [docs/LINUXDO_GUIDE.md](docs/LINUXDO_GUIDE.md)

**推荐配置**:
```yaml
linuxdo:
  url: https://linux.do
  accounts:
    - username: your_email@example.com
      password: your_password
      enabled: true

notifications:
  email:
    enabled: true  # 必须启用以接收帖子推送
```

**定时任务建议**:
```bash
# 每天早上 8:00 获取论坛动态
0 8 * * * cd /root/auto-checkin && python3 src/main.py --site linuxdo >> logs/cron.log 2>&1
```

### 方式二：Docker 运行

#### 1. 构建镜像

```bash
docker build -t auto-checkin .
```

#### 2. 运行容器

```bash
docker run -d \
  --name auto-checkin \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/.env:/app/.env \
  auto-checkin
```

#### 3. 使用 Docker Compose

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## ⏰ 定时执行

### Cron（Linux/Mac）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天早上 9:00 执行）
0 9 * * * /path/to/auto-checkin/run.sh >> /path/to/auto-checkin/logs/cron.log 2>&1
```

其他时间示例：
- `0 */6 * * *` - 每 6 小时执行一次
- `0 0 * * *` - 每天午夜执行
- `30 8 * * *` - 每天早上 8:30 执行

### Docker Cron

创建 `crontab` 文件：

```bash
0 9 * * * cd /app && python3 src/main.py >> /app/logs/cron.log 2>&1
```

修改 `docker-compose.yml`:

```yaml
command: sh -c "cron && tail -f /app/logs/cron.log"
```

## 📧 邮件通知配置

### Gmail 配置

1. 启用两步验证
2. 生成应用专用密码：https://myaccount.google.com/apppasswords
3. 在配置文件或环境变量中使用应用专用密码

### 其他邮箱

根据邮箱提供商的 SMTP 设置调整配置：

- **QQ 邮箱**: `smtp.qq.com:587` (需要授权码)
- **163 邮箱**: `smtp.163.com:587`
- **Outlook**: `smtp-mail.outlook.com:587`

## 🔧 高级配置

### 并发控制

在 `src/main.py` 中调整并发参数：

```python
MAX_CONCURRENT_TASKS = 2  # 最大并发任务数
MIN_DELAY_BETWEEN_ACCOUNTS = 2  # 账号之间最小延迟（秒）
MAX_DELAY_BETWEEN_ACCOUNTS = 5  # 账号之间最大延迟（秒）
```

或通过环境变量：

```bash
MAX_CONCURRENT_TASKS=2
MIN_DELAY_BETWEEN_ACCOUNTS=2
MAX_DELAY_BETWEEN_ACCOUNTS=5
```

### 浏览器超时配置

在站点适配器中调整：

```python
PAGE_LOAD_TIMEOUT = 30000  # 页面加载超时（毫秒）
ELEMENT_WAIT_TIMEOUT = 10000  # 元素等待超时（毫秒）
```

## 🆕 添加新站点

要支持新站点，创建新的适配器：

1. 在 `src/adapters/` 创建新文件，如 `newsite.py`
2. 继承 `BaseAdapter` 并实现三个方法：

```python
from .base_adapter import BaseAdapter, CheckinResult

class NewSiteAdapter(BaseAdapter):
    async def login(self) -> bool:
        """实现登录逻辑"""
        # 访问登录页面
        await self.page.goto(f"{self.site_url}/login")

        # 填写用户名和密码
        await self.page.fill('input[name="username"]', self.username)
        await self.page.fill('input[name="password"]', self.password)

        # 点击登录按钮
        await self.page.click('button[type="submit"]')

        # 等待登录完成
        await self.page.wait_for_load_state('networkidle')

        return True

    async def checkin(self) -> CheckinResult:
        """实现签到逻辑"""
        # 访问签到页面
        await self.page.goto(f"{self.site_url}/checkin")

        # 点击签到按钮
        await self.page.click('button.checkin-btn')

        return CheckinResult(True, "签到成功")

    async def is_logged_in(self) -> bool:
        """检查登录状态"""
        await self.page.goto(self.site_url)
        # 检查是否存在用户信息元素
        user_element = await self.page.query_selector('.user-info')
        return user_element is not None
```

3. 在 `src/main.py` 的 `ADAPTERS` 字典中注册：

```python
from src.adapters.newsite import NewSiteAdapter

ADAPTERS = {
    'anyrouter': AnyrouterAdapter,
    'newsite': NewSiteAdapter,
}
```

4. 在配置文件中添加站点配置

## 🐛 调试和日志

### 日志文件

- 主日志: `logs/checkin.log`
- 截图: `logs/{站点}_{用户}_{阶段}.png`
- Cron 日志: `logs/cron.log` (如果配置了 cron)

### 调试技巧

1. **使用调试模式查看浏览器操作**:
   ```bash
   python3 src/main.py --debug
   ```

2. **提高日志级别**:
   ```bash
   export LOG_LEVEL=DEBUG
   python3 src/main.py
   ```

3. **检查截图**:
   查看 `logs/` 目录下的截图，了解失败原因

4. **测试模式**:
   ```bash
   python3 src/main.py --dry-run
   ```

## ❓ 常见问题

### 1. 登录失败

- 检查用户名密码是否正确
- 使用 `--debug` 模式观察浏览器行为
- 查看 `logs/` 目录下的截图
- 可能需要调整 `anyrouter.py` 中的选择器

### 2. 签到按钮找不到

- 使用浏览器开发者工具检查页面结构
- 更新适配器中的选择器列表

### 3. Playwright 安装失败

```bash
# 手动安装浏览器
playwright install chromium

# 如果遇到权限问题
sudo playwright install chromium --with-deps
```

### 4. 邮件发送失败

- 检查 SMTP 配置是否正确
- 确认使用了应用专用密码（不是登录密码）
- 检查防火墙是否阻止了 SMTP 端口

### 5. Docker 容器无法启动

```bash
# 查看日志
docker logs auto-checkin

# 检查挂载的配置文件是否存在
ls -la config/sites.yaml .env
```

### 6. 配置验证失败

系统会自动验证配置文件的完整性，如果验证失败会显示详细的错误信息。根据提示修复配置文件即可。

## 🔒 安全建议

1. **保护配置文件**: 不要将包含密码的配置文件提交到版本控制

   ```bash
   # .env 和 config/sites.yaml 已在 .gitignore 中
   ```

2. **使用环境变量**: 在生产环境中使用环境变量存储敏感信息

3. **使用强密码**: 为邮箱和站点账号设置强密码

4. **定期检查**: 定期查看日志，确保系统正常运行

5. **限制权限**: 确保配置文件和脚本只有所有者可读写

   ```bash
   chmod 600 .env config/sites.yaml
   chmod 700 run.sh
   ```

6. **Docker 安全**:
   ```bash
   # 使用非 root 用户运行容器
   # 定期更新基础镜像
   ```

## 📝 更新日志

### v2.1.0 (2024-12-14)

**新功能**:
- ✅ **添加 Linux.do 论坛支持**
  - 自动登录 Linux.do 论坛
  - 获取最新帖子和热门话题
  - 通过邮件推送论坛动态摘要
  - 无需浏览即可了解论坛最新进度
- ✅ **增强邮件通知**
  - 支持显示论坛帖子列表
  - HTML 格式化帖子信息
  - 可点击链接直接跳转

### v2.0.0 (2024-12-14)

**新功能**:
- ✅ 添加并发执行支持，带随机延迟避免检测
- ✅ 智能页面等待机制，使用 Playwright wait_for_selector
- ✅ 环境变量支持，安全管理敏感信息
- ✅ 配置验证器，自动检查配置完整性
- ✅ Docker 支持，简化部署流程
- ✅ 改进的错误处理和重试机制
- ✅ 指数退避重试策略

**改进**:
- ⚡ 性能优化：并发执行提升 2-5 倍速度
- 🔒 安全性提升：支持环境变量管理密码
- 📊 更详细的日志输出
- 🐛 更健壮的错误处理

### v1.0.0 (2025-12-14)

- 初始版本
- 支持 anyrouter.top
- 实现多账号管理
- 支持日志和邮件通知
- 会话保持功能

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如果遇到问题，请：
1. 查看日志文件和截图
2. 使用 `--debug` 模式排查问题
3. 提交 Issue 并附上详细的错误信息
