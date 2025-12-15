# 项目拆分指南

## 📦 概述

本项目已完成功能隔离重构，现在包含两个完全独立的功能模块：

1. **AnyRouter 自动签到** - 传统网站自动签到功能
2. **Linux.do 论坛自动化** - 论坛内容获取 + AI 智能分析

这两个功能可以：
- ✅ **独立运行** - 各自有独立的配置文件和运行脚本
- ✅ **独立部署** - 可以拆分为两个独立的 Git 仓库
- ✅ **独立开发** - 各自有清晰的依赖关系和代码边界

---

## 🚀 独立运行方式

### 方式 1：使用独立脚本（推荐）

#### AnyRouter 签到
```bash
# 使用独立脚本和配置
python3 run_anyrouter.py

# 调试模式
python3 run_anyrouter.py --debug

# 指定配置文件
python3 run_anyrouter.py --config config/anyrouter.yaml
```

#### Linux.do 论坛
```bash
# 使用独立脚本和配置
python3 run_linuxdo.py

# 调试模式
python3 run_linuxdo.py --debug

# 指定配置文件
python3 run_linuxdo.py --config config/linuxdo.yaml
```

### 方式 2：使用原有主脚本

```bash
# 只运行 anyrouter
python3 src/main.py --site anyrouter

# 只运行 linuxdo
python3 src/main.py --site linuxdo
```

---

## 📂 文件依赖关系

### AnyRouter 项目依赖

**配置文件：**
- `config/anyrouter.yaml` - 独立配置

**运行脚本：**
- `run_anyrouter.py` - 独立启动脚本

**核心代码：**
```
src/
├── adapters/
│   ├── base_adapter.py         # 基础适配器（共享）
│   └── anyrouter.py            # AnyRouter 适配器
├── browser_manager.py          # 浏览器管理器（共享）
├── config_loader.py            # 配置加载器（共享）
└── notifiers/
    ├── logger.py               # 日志记录器（共享）
    └── email.py                # 邮件通知器（共享，但不含 linuxdo 特定代码）
```

**依赖库：**
- `playwright` - 浏览器自动化
- `pyyaml` - YAML 配置解析
- `python-dotenv` - 环境变量支持

**不需要：**
- ❌ `src/ai_analyzer.py` - 不需要 AI 功能
- ❌ `src/adapters/linuxdo.py` - 不需要 linuxdo 适配器
- ❌ `openai` 库 - 不需要 AI SDK

---

### Linux.do 项目依赖

**配置文件：**
- `config/linuxdo.yaml` - 独立配置（包含 AI 配置）
- `.env` - 环境变量（AI API Key）

**运行脚本：**
- `run_linuxdo.py` - 独立启动脚本

**核心代码：**
```
src/
├── adapters/
│   ├── base_adapter.py         # 基础适配器（共享）
│   └── linuxdo.py              # Linux.do 适配器
├── ai_analyzer.py              # AI 分析器（Linux.do 专用）
├── browser_manager.py          # 浏览器管理器（共享）
├── config_loader.py            # 配置加载器（共享）
└── notifiers/
    ├── logger.py               # 日志记录器（共享）
    └── email.py                # 邮件通知器（共享）
```

**依赖库：**
- `playwright` - 浏览器自动化
- `pyyaml` - YAML 配置解析
- `python-dotenv` - 环境变量支持
- `openai` - OpenAI 兼容 API 客户端（用于阿里云通义千问）

**不需要：**
- ❌ `src/adapters/anyrouter.py` - 不需要 anyrouter 适配器

---

## 🔧 如何拆分为两个独立项目

### 项目 1：anyrouter-auto-checkin

```bash
# 1. 创建新目录
mkdir anyrouter-auto-checkin
cd anyrouter-auto-checkin

# 2. 复制共享基础设施
cp -r ../auto-checkin/src/adapters/base_adapter.py src/adapters/
cp -r ../auto-checkin/src/browser_manager.py src/
cp -r ../auto-checkin/src/config_loader.py src/
cp -r ../auto-checkin/src/notifiers src/

# 3. 复制 AnyRouter 专用文件
cp ../auto-checkin/src/adapters/anyrouter.py src/adapters/
cp ../auto-checkin/run_anyrouter.py ./
cp ../auto-checkin/config/anyrouter.yaml config/

# 4. 从 email.py 中移除 Linux.do 特定代码（163-274 行）

# 5. 创建 requirements.txt
cat > requirements.txt << EOF
playwright==1.40.0
pyyaml==6.0.1
python-dotenv==1.0.0
EOF

# 6. 创建 README.md
# 7. 初始化 Git
git init
git add .
git commit -m "Initial commit: AnyRouter auto-checkin"
```

**独立项目结构：**
```
anyrouter-auto-checkin/
├── README.md
├── requirements.txt
├── run_anyrouter.py         # 主入口
├── config/
│   └── anyrouter.yaml       # 配置文件
└── src/
    ├── adapters/
    │   ├── base_adapter.py
    │   └── anyrouter.py
    ├── browser_manager.py
    ├── config_loader.py
    └── notifiers/
        ├── logger.py
        └── email.py         # 简化版，无 linuxdo 代码
```

---

### 项目 2：linuxdo-ai-automation

```bash
# 1. 创建新目录
mkdir linuxdo-ai-automation
cd linuxdo-ai-automation

# 2. 复制共享基础设施
cp -r ../auto-checkin/src/adapters/base_adapter.py src/adapters/
cp -r ../auto-checkin/src/browser_manager.py src/
cp -r ../auto-checkin/src/config_loader.py src/
cp -r ../auto-checkin/src/notifiers src/

# 3. 复制 Linux.do 专用文件
cp ../auto-checkin/src/adapters/linuxdo.py src/adapters/
cp ../auto-checkin/src/ai_analyzer.py src/
cp ../auto-checkin/run_linuxdo.py ./
cp ../auto-checkin/config/linuxdo.yaml config/
cp ../auto-checkin/.env.example ./

# 4. 复制文档
cp ../auto-checkin/AI_FEATURE_GUIDE.md docs/
cp ../auto-checkin/GET_STARTED.md docs/
cp ../auto-checkin/docs/LINUXDO_GUIDE.md docs/

# 5. 创建 requirements.txt
cat > requirements.txt << EOF
playwright==1.40.0
pyyaml==6.0.1
python-dotenv==1.0.0
openai>=1.0.0
EOF

# 6. 创建 README.md
# 7. 初始化 Git
git init
git add .
git commit -m "Initial commit: Linux.do AI automation"
```

**独立项目结构：**
```
linuxdo-ai-automation/
├── README.md
├── requirements.txt
├── .env.example
├── run_linuxdo.py           # 主入口
├── config/
│   └── linuxdo.yaml         # 配置文件（含 AI 配置）
├── docs/
│   ├── AI_FEATURE_GUIDE.md
│   ├── GET_STARTED.md
│   └── LINUXDO_GUIDE.md
└── src/
    ├── adapters/
    │   ├── base_adapter.py
    │   └── linuxdo.py       # Linux.do 适配器
    ├── ai_analyzer.py       # AI 分析器
    ├── browser_manager.py
    ├── config_loader.py
    └── notifiers/
        ├── logger.py
        └── email.py         # 完整版，含 AI 展示代码
```

---

## ⚙️ 配置隔离说明

### AnyRouter 配置（config/anyrouter.yaml）

```yaml
site:
  name: anyrouter
  url: https://anyrouter.top
  accounts:
    - username: user@example.com
      password: password
      enabled: true

notifications:
  log:
    enabled: true
  email:
    enabled: false

browser:
  headless: true
  timeout: 30000

concurrency:
  max_concurrent: 2
```

**特点：**
- ✅ 无 AI 相关配置
- ✅ 专注签到功能
- ✅ 简单并发控制

---

### Linux.do 配置（config/linuxdo.yaml）

```yaml
site:
  name: linuxdo
  url: https://linux.do
  accounts:
    - username: user@example.com
      password: password
      enabled: true

content:
  latest_topics_limit: 20
  hot_topics_limit: 10
  read_content_limit: 5
  ai_analysis_limit: 3

ai:
  enabled: true
  api_key: ${DASHSCOPE_API_KEY}
  api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
  model: qwen-flash
  temperature: 0.7
  max_tokens: 800
  user_interests:
    - Linux 服务器
    - 开源软件

notifications:
  log:
    enabled: true
  email:
    enabled: true

browser:
  headless: true
  timeout: 60000
```

**特点：**
- ✅ 包含完整 AI 配置
- ✅ 内容获取参数可配置
- ✅ 用户兴趣画像支持
- ✅ 使用阿里云通义千问 qwen-flash

---

## 🔌 AI 模型：qwen-flash

两个功能都使用阿里云通义千问的 **qwen-flash** 模型：

### 特点
- ⚡ **速度快** - 响应时间短
- 💰 **成本低** - 价格实惠
- 🎯 **准确度高** - 满足内容分析需求
- 🔌 **兼容 OpenAI API** - 使用 openai 库即可调用

### 配置方式

**环境变量（推荐）：**
```bash
# .env 文件
DASHSCOPE_API_KEY=sk-your-api-key-here
AI_MODEL=qwen-flash
```

**配置文件：**
```yaml
ai:
  api_key: ${DASHSCOPE_API_KEY}
  api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
  model: qwen-flash
```

### 获取 API Key
1. 访问：https://dashscope.console.aliyun.com/apiKey
2. 登录阿里云账号
3. 创建 API Key
4. 复制到配置文件或环境变量

---

## 📊 对比总结

| 特性 | AnyRouter | Linux.do |
|------|-----------|----------|
| 主要功能 | 自动签到 | 内容获取 + AI 分析 |
| 配置文件 | anyrouter.yaml | linuxdo.yaml |
| 运行脚本 | run_anyrouter.py | run_linuxdo.py |
| AI 依赖 | ❌ 无 | ✅ 有（qwen-flash） |
| 代码行数 | ~300 行 | ~1000+ 行 |
| 依赖库数量 | 3 个 | 4 个（+openai） |
| 可拆分性 | ✅ 完全独立 | ✅ 完全独立 |

---

## ✅ 验证独立性

### 测试 AnyRouter 独立运行

```bash
# 1. 只安装 AnyRouter 需要的依赖
pip install playwright pyyaml python-dotenv

# 2. 只运行 AnyRouter
python3 run_anyrouter.py

# 3. 验证不会导入 linuxdo 或 ai_analyzer
# 应该能正常运行，不报错
```

### 测试 Linux.do 独立运行

```bash
# 1. 安装 Linux.do 需要的依赖
pip install playwright pyyaml python-dotenv openai

# 2. 配置 AI API Key
echo "DASHSCOPE_API_KEY=your-key" > .env

# 3. 只运行 Linux.do
python3 run_linuxdo.py

# 4. 验证 AI 功能正常
# 应该能看到 "AI 分析器已启用 - 模型: qwen-flash"
```

---

## 🎯 总结

通过本次重构，实现了：

1. **配置隔离** ✅
   - 两个独立的 YAML 配置文件
   - 各自的配置参数互不影响

2. **代码隔离** ✅
   - 独立的运行脚本
   - 清晰的依赖关系
   - AI 功能完全可选

3. **可拆分性** ✅
   - 可以拆分为两个独立的 Git 仓库
   - 可以独立开发和部署
   - 共享代码通过复制而非依赖

4. **统一 AI 模型** ✅
   - 使用阿里云通义千问 qwen-flash
   - 兼容 OpenAI API 格式
   - 配置简单，成本低廉

现在你可以：
- 只使用 AnyRouter 进行自动签到
- 只使用 Linux.do 进行论坛分析
- 或者两者都使用

完全根据需求灵活选择！
