# AnyRouter 自动签到模块

## 📝 模块信息

- **类型**: checkin（签到类）
- **站点**: https://anyrouter.top
- **功能**: 自动登录并执行签到
- **AI 依赖**: ❌ 无

## 🚀 快速开始

### 1. 配置账号

编辑 `config.yaml`：

```yaml
site:
  url: https://anyrouter.top
  accounts:
    - username: your-email@example.com
      password: your-password
      enabled: true
```

### 2. 运行

```bash
# 从模块目录运行
cd modules/checkin/anyrouter
python3 run.py

# 或从项目根目录运行
python3 modules/checkin/anyrouter/run.py

# 调试模式
python3 run.py --debug

# 模拟运行
python3 run.py --dry-run
```

## ⚙️ 配置说明

### 站点配置

```yaml
site:
  name: anyrouter         # 模块名称
  url: https://anyrouter.top  # 站点 URL
  accounts:               # 账号列表
    - username: user1@example.com
      password: password1
      enabled: true       # 是否启用
```

### 浏览器配置

```yaml
browser:
  headless: true          # 无头模式
  timeout: 30000          # 超时时间（毫秒）
```

### 并发配置

```yaml
concurrency:
  max_concurrent: 2       # 最大并发数
  delay_between_accounts:
    min: 2                # 最小延迟（秒）
    max: 5                # 最大延迟（秒）
```

### 通知配置

```yaml
notifications:
  log:
    enabled: true
    level: INFO

  email:
    enabled: false        # 邮件通知开关
    smtp_server: smtp.gmail.com
    smtp_port: 587
    use_tls: true
    username: your-email@gmail.com
    password: your-app-password
    to_addresses:
      - notify@example.com
```

## 📊 运行日志

日志保存在：
- 控制台输出
- `logs/checkin/` 目录

## 🔧 故障排查

### 问题 1：登录失败

- 检查用户名和密码是否正确
- 使用 `--debug` 模式查看页面
- 检查网络连接

### 问题 2：签到失败

- anyrouter 可能有反爬虫保护
- 尝试调整超时时间
- 检查会话是否保存成功

## 📚 相关文档

- [项目架构说明](../../../ARCHITECTURE_REFACTOR.md)
- [模块开发指南](../../../docs/MODULE_DEVELOPMENT.md)
