# Automation Hub

<p align="center">
  <strong>功能强大、易于扩展的自动化任务中心</strong><br>
  支持网站签到、论坛内容获取、游戏签到等多种自动化任务
</p>

---

## 🎯 功能模块

本项目采用模块化架构，每个功能完全独立，易于扩展。

### ✅ 已实现模块

| 模块 | 类型 | 功能 | AI 支持 |
|------|------|------|---------|
| **anyrouter** | 签到类 | AnyRouter 路由器服务自动签到 | ❌ |
| **linuxdo** | 论坛类 | Linux.do 论坛内容获取 + AI 智能分析 | ✅ qwen-flash |

### 🔜 待扩展模块

**签到类** (`modules/checkin/`):
- GLaDOS、ikuuu 等网络服务签到

**论坛类** (`modules/forum/`):
- V2EX、HostLoc 等论坛内容获取

**游戏类** (`modules/game/`):
- 米哈游（原神/崩铁）、B站游戏等签到

**自定义** (`modules/custom/`):
- 使用模板快速创建新模块

---

## 🏗️ 项目架构

```
automation-hub/
├── core/                      # 共享基础设施
│   ├── browser_manager.py     # 浏览器管理器
│   ├── base_adapter.py        # 基础适配器
│   ├── logger.py              # 日志管理
│   └── notifiers/             # 通知模块
│
├── modules/                   # 功能模块（按类型分组）
│   ├── checkin/              # 签到类模块
│   │   └── anyrouter/        # ✅ AnyRouter 签到
│   ├── forum/                # 论坛类模块
│   │   └── linuxdo/          # ✅ Linux.do 论坛
│   ├── game/                 # 游戏类模块（待扩展）
│   └── custom/               # 自定义模块模板
│
├── storage/                  # 存储目录
│   ├── sessions/             # 浏览器会话
│   └── data/                 # 持久化数据
│
├── logs/                     # 日志目录
├── scripts/                  # 工具脚本
└── docs/                     # 文档目录
```

**架构特点**：
- ✅ **模块化** - 每个功能完全独立
- ✅ **分类清晰** - 按功能类型组织
- ✅ **易于扩展** - 提供模块模板和生成器
- ✅ **共享基础** - 核心功能统一管理

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 运行模块

每个模块都可以独立运行：

```bash
# AnyRouter 签到
python3 modules/checkin/anyrouter/run.py

# Linux.do 论坛（含 AI 分析）
python3 modules/forum/linuxdo/run.py

# 调试模式
python3 modules/checkin/anyrouter/run.py --debug

# 模拟运行
python3 modules/checkin/anyrouter/run.py --dry-run
```

### 3. 配置说明

每个模块的配置文件独立，使用 `.example` 模板创建：

```bash
# AnyRouter 模块
cp modules/checkin/anyrouter/config.yaml.example modules/checkin/anyrouter/config.yaml

# Linux.do 模块
cp modules/forum/linuxdo/config.yaml.example modules/forum/linuxdo/config.yaml
```

**AnyRouter** (`modules/checkin/anyrouter/config.yaml`):
```yaml
site:
  url: https://anyrouter.top
  accounts:
    - username: your-email@example.com
      password: your-password
      enabled: true
```

**Linux.do** (`modules/forum/linuxdo/config.yaml`):
```yaml
site:
  url: https://linux.do
  accounts:
    - username: your-email@example.com
      password: your-password
      enabled: true

# AI 配置（可选）
ai:
  enabled: true
  api_key: ${DASHSCOPE_API_KEY}  # 阿里云通义千问
  model: qwen-flash
```

---

## ➕ 添加新模块

### 方式 1：使用模块生成器（推荐）

```bash
python3 scripts/module_generator.py --name 模块名 --type checkin|forum|game
```

### 方式 2：手动创建

1. 复制模块模板
2. 修改配置文件
3. 实现适配器逻辑
4. 运行测试

详见：[模块开发指南](docs/MODULE_DEVELOPMENT.md)

---

## 🤖 AI 功能说明

### 支持的模块

当前 **linuxdo** 模块支持 AI 智能分析：
- AI 内容总结
- AI 智能推荐
- 关键信息提取
- 情感分析

### AI 模型

使用**阿里云通义千问 qwen-flash**：
- ⚡ 速度快
- 💰 成本低
- 🎯 准确度高
- 🔌 兼容 OpenAI API

### 配置 AI

1. 获取 API Key：https://dashscope.console.aliyun.com/apiKey

2. 创建 `.env` 文件：
```bash
DASHSCOPE_API_KEY=sk-your-api-key-here
```

3. 在模块配置中启用：
```yaml
ai:
  enabled: true
  api_key: ${DASHSCOPE_API_KEY}
  model: qwen-flash
```

---

## 📊 批量运行

使用批量运行脚本同时执行多个模块：

```bash
# 运行指定模块
python3 scripts/batch_run.py --modules checkin.anyrouter forum.linuxdo

# 运行某一类型的所有模块
python3 scripts/batch_run.py --type checkin

# 运行所有模块
python3 scripts/batch_run.py --all
```

---

## 🛠️ 实用工具

项目提供了一些实用脚本帮助管理和维护：

### 配置检查

检查所有模块的配置文件是否正确：

```bash
python3 scripts/check_config.py
```

该脚本会：
- 检查配置文件是否存在
- 验证 YAML 格式
- 检查必需字段
- 列出警告和错误

### 日志清理

清理旧的日志文件和截图：

```bash
# 清理 7 天前的日志（默认）
python3 scripts/clean_logs.py

# 清理 30 天前的日志
python3 scripts/clean_logs.py --days 30

# 模拟运行，查看将删除哪些文件
python3 scripts/clean_logs.py --dry-run
```

---

## ⏰ 定时任务

使用 cron 设置定时执行：

```bash
crontab -e

# 每天早上 8:00 运行 anyrouter 签到
0 8 * * * cd /path/to/automation-hub && python3 modules/checkin/anyrouter/run.py >> logs/checkin/anyrouter.log 2>&1

# 每天早上 9:00 运行 linuxdo 论坛分析
0 9 * * * cd /path/to/automation-hub && python3 modules/forum/linuxdo/run.py >> logs/forum/linuxdo.log 2>&1
```

---

## 📚 文档

- [项目架构说明](ARCHITECTURE_REFACTOR.md)
- [模块开发指南](docs/MODULE_DEVELOPMENT.md)
- [功能拆分指南](PROJECT_SPLIT_GUIDE.md)
- [Linux.do AI 功能指南](AI_FEATURE_GUIDE.md)

---

## 🔧 故障排查

### 问题 1：模块运行失败

- 检查配置文件是否正确
- 使用 `--debug` 模式查看详细日志
- 确认依赖已安装

### 问题 2：AI 功能未启用

- 检查 `.env` 文件中的 `DASHSCOPE_API_KEY`
- 确认模块配置中 `ai.enabled: true`
- 检查 API Key 是否有效

### 问题 3：浏览器启动失败

```bash
# 重新安装 Playwright 浏览器
playwright install chromium
```

---

## 📈 特性对比

### vs 旧版架构

| 特性 | 旧版 | 新版（Automation Hub） |
|------|-----|----------------------|
| 架构设计 | 耦合 | ✅ 完全模块化 |
| 扩展性 | ⚠️ 中等 | ✅ 极强 |
| 代码组织 | ⚠️ 分散 | ✅ 清晰分类 |
| 添加新功能 | ⚠️ 手动 | ✅ 自动生成 |
| 批量运行 | ❌ 不支持 | ✅ 统一脚本 |
| 模块独立性 | ✅ 较好 | ✅ 完美 |

---

## 🎯 未来计划

- [ ] Web 管理界面
- [ ] 插件市场
- [ ] 更多模块支持
- [ ] 监控告警系统

## 🐳 关于 Docker

⚠️ **Docker 支持已暂停维护** - 当前推荐使用 Cron 定时任务方式运行（更轻量、更高效）

详见：[DOCKER_NOTE.md](DOCKER_NOTE.md)

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

添加新模块步骤：
1. 使用模块生成器创建模块
2. 实现适配器逻辑
3. 测试确保功能正常
4. 提交 PR

---

<p align="center">
  Made with ❤️ by Automation Hub
</p>
