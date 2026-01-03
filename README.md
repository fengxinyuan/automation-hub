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
| **linuxdo** | 论坛类 | Linux.do 论坛智能内容获取 + AI 分析推荐 | ✅ qwen-flash |

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

# 内容获取配置
content:
  latest_topics_limit: 20  # 最新帖子数量
  hot_topics_limit: 10     # 热门帖子数量
  read_content_limit: 5    # 深度阅读数量
  ai_analysis_limit: 3     # AI 分析数量

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
- 📝 AI 内容摘要 - 自动总结帖子核心内容
- 🎯 智能推荐 - 基于用户兴趣的个性化推荐
- 🔑 关键信息提取 - 提取帖子要点和标签
- 💭 情感分析 - 分析内容情感倾向
- 📊 综合评分 - 基于热度、互动率、分类和兴趣的智能评分

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

### 方式 1：使用提供的 crontab 配置（推荐）

项目提供了预配置的定时任务文件：

```bash
# 应用 crontab 配置（每天北京时间 12:00 执行）
crontab /root/automation-hub/crontab.txt

# 查看当前任务
crontab -l

# 查看执行日志
tail -f /root/automation-hub/storage/logs/cron.log
```

### 方式 2：自定义 cron 任务

```bash
crontab -e

# 每天早上 8:00 运行 anyrouter 签到
0 8 * * * cd /path/to/automation-hub && python3 modules/checkin/anyrouter/run.py >> logs/checkin/anyrouter.log 2>&1

# 每天早上 9:00 运行 linuxdo 论坛分析
0 9 * * * cd /path/to/automation-hub && python3 modules/forum/linuxdo/run.py >> logs/forum/linuxdo.log 2>&1
```

**注意**：服务器使用北京时间（Asia/Shanghai CST +0800），cron 时间直接对应北京时间。

---

## 📚 文档

- [项目架构说明](ARCHITECTURE_REFACTOR.md)
- [模块开发指南](docs/MODULE_DEVELOPMENT.md)
- [Linux.do AI 功能指南](AI_FEATURE_GUIDE.md)

---

## 🔧 故障排查

### 常见问题

**浏览器启动失败**
```bash
playwright install chromium
```

**模块运行失败**
- 检查配置文件：`python3 scripts/check_config.py`
- 使用 `--debug` 查看详细日志
- 确认依赖已安装：`pip install -r requirements.txt`

**AI 功能未生效**
- 检查 `.env` 中的 API Key
- 确认配置文件 `ai.enabled: true`

---

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
