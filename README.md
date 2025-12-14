# 自动签到系统

一个支持多站点的自动登录签到系统，使用 Python + Playwright 实现浏览器自动化。

## 功能特性

- **多站点支持**: 可扩展架构，轻松添加新站点适配器
- **多账号管理**: 通过 YAML 配置文件管理多个站点和账号
- **会话保持**: 自动保存浏览器会话，减少登录频率
- **反爬虫应对**: 使用真实浏览器环境，模拟人工操作
- **通知系统**: 支持日志文件和邮件通知
- **定时执行**: 配合 cron 实现每日自动签到

## 项目结构

```
auto-checkin/
├── config/
│   └── sites.yaml           # 站点和账号配置
├── src/
│   ├── main.py              # 主程序
│   ├── config_loader.py     # 配置加载
│   ├── browser_manager.py   # 浏览器管理
│   ├── adapters/            # 站点适配器
│   │   ├── base_adapter.py
│   │   └── anyrouter.py
│   └── notifiers/           # 通知模块
│       ├── logger.py
│       └── email.py
├── storage/sessions/        # 浏览器会话存储
├── logs/                    # 日志文件
├── requirements.txt
├── run.sh                   # 启动脚本
└── README.md
```

## 安装

### 1. 克隆项目

```bash
cd auto-checkin
```

### 2. 安装依赖

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

### 3. 配置

编辑 `config/sites.yaml`:

```yaml
sites:
  anyrouter:
    url: https://anyrouter.top
    accounts:
      - username: your-email@example.com
        password: your-password
        enabled: true

notifications:
  log:
    enabled: true
    level: INFO

  email:
    enabled: false  # 设置为 true 启用邮件通知
    smtp_server: smtp.gmail.com
    smtp_port: 587
    use_tls: true
    username: your-email@gmail.com
    password: your-app-password  # Gmail 应用专用密码
    to_addresses:
      - notify@example.com
```

## 使用方法

### 手动运行

```bash
# 直接运行
python3 src/main.py

# 使用启动脚本
./run.sh

# 指定配置文件
python3 src/main.py --config config/sites.yaml

# 指定站点
python3 src/main.py --site anyrouter

# 调试模式（显示浏览器窗口）
python3 src/main.py --debug

# 测试模式（不实际执行）
python3 src/main.py --dry-run
```

### 定时执行

使用 cron 实现每日自动签到：

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

## 首次运行

由于 anyrouter.top 有反爬虫保护，首次运行建议使用调试模式查看页面结构：

```bash
python3 src/main.py --debug
```

这将显示浏览器窗口，你可以：
1. 观察登录流程是否正确
2. 检查元素选择器是否准确
3. 查看 `logs/` 目录下的截图

如果登录或签到失败，可能需要调整 `src/adapters/anyrouter.py` 中的选择器。

## 邮件通知配置

### Gmail 配置

1. 启用两步验证
2. 生成应用专用密码：https://myaccount.google.com/apppasswords
3. 在配置文件中使用应用专用密码

### 其他邮箱

根据邮箱提供商的 SMTP 设置调整配置：

- **QQ 邮箱**: smtp.qq.com:587 (需要授权码)
- **163 邮箱**: smtp.163.com:587
- **Outlook**: smtp-mail.outlook.com:587

## 添加新站点

要支持新站点，创建新的适配器：

1. 在 `src/adapters/` 创建新文件，如 `newsite.py`
2. 继承 `BaseAdapter` 并实现三个方法：
   ```python
   class NewSiteAdapter(BaseAdapter):
       async def login(self) -> bool:
           # 实现登录逻辑
           pass

       async def checkin(self) -> CheckinResult:
           # 实现签到逻辑
           pass

       async def is_logged_in(self) -> bool:
           # 检查登录状态
           pass
   ```
3. 在 `src/main.py` 的 `ADAPTERS` 字典中注册
4. 在配置文件中添加站点配置

## 日志和调试

- 日志文件: `logs/checkin.log`
- 截图文件: `logs/{站点}_{用户}_{阶段}.png`
- Cron 日志: `logs/cron.log` (如果配置了 cron)

调试技巧：
- 使用 `--debug` 查看浏览器操作
- 检查截图了解失败原因
- 提高日志级别到 DEBUG: 在配置中设置 `level: DEBUG`

## 常见问题

### 1. 登录失败

- 检查用户名密码是否正确
- 使用 `--debug` 模式观察浏览器行为
- 查看 `logs/` 目录下的截图
- 可能需要调整 `anyrouter.py` 中的选择器

### 2. 签到按钮找不到

- 使用浏览器开发者工具检查页面结构
- 更新 `anyrouter.py` 中的 `checkin_selectors` 列表

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

## 安全建议

1. **保护配置文件**: 不要将包含密码的配置文件提交到版本控制
2. **使用强密码**: 为邮箱和站点账号设置强密码
3. **定期检查**: 定期查看日志，确保系统正常运行
4. **限制权限**: 确保配置文件和脚本只有所有者可读写

```bash
chmod 600 config/sites.yaml
chmod 700 run.sh
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2025-12-14)
- 初始版本
- 支持 anyrouter.top
- 实现多账号管理
- 支持日志和邮件通知
- 会话保持功能
