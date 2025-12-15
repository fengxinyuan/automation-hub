# 项目架构重构方案

## 📋 背景

当前项目将扩展支持更多功能：
- ✅ AnyRouter 及同类网络服务签到
- ✅ Linux.do 及其他论坛自动化
- 🆕 游戏签到脚本
- 🆕 其他自动化任务

需要重构为更通用、可扩展的架构。

---

## 🎯 项目重命名建议

### 选项 1：`automation-hub`（推荐）⭐
**含义**：自动化中心
**适用场景**：通用自动化平台，支持各种类型任务
**特点**：专业、通用、易理解

### 选项 2：`auto-tasks`
**含义**：自动任务
**适用场景**：任务型自动化
**特点**：简洁明了

### 选项 3：`bot-garden`
**含义**：机器人花园
**适用场景**：多种自动化脚本集合
**特点**：有趣、形象

### 选项 4：`daily-automation`
**含义**：日常自动化
**适用场景**：日常任务自动化
**特点**：明确定位

### 选项 5：`task-runner`
**含义**：任务运行器
**适用场景**：任务执行平台
**特点**：技术范

---

## 🏗️ 新架构设计

### 方案 A：按功能类型分组（推荐）⭐

```
automation-hub/
├── README.md                      # 项目总览
├── requirements.txt               # 共享依赖
├── .env.example                   # 环境变量模板
│
├── core/                          # 核心共享模块
│   ├── browser_manager.py         # 浏览器管理器
│   ├── config_loader.py           # 配置加载器
│   ├── logger.py                  # 日志管理
│   └── notifiers/                 # 通知模块
│       ├── email.py
│       ├── telegram.py            # 🆕 Telegram 通知
│       └── webhook.py             # 🆕 Webhook 通知
│
├── modules/                       # 功能模块目录
│   │
│   ├── checkin/                   # 🔹 签到类模块
│   │   ├── README.md              # 签到模块说明
│   │   ├── anyrouter/             # AnyRouter 签到
│   │   │   ├── config.yaml        # 独立配置
│   │   │   ├── adapter.py         # 适配器
│   │   │   └── run.py             # 独立运行脚本
│   │   ├── glados/                # 🆕 GLaDOS 签到
│   │   │   ├── config.yaml
│   │   │   ├── adapter.py
│   │   │   └── run.py
│   │   └── ikuuu/                 # 🆕 ikuuu 签到
│   │       ├── config.yaml
│   │       ├── adapter.py
│   │       └── run.py
│   │
│   ├── forum/                     # 🔹 论坛类模块
│   │   ├── README.md              # 论坛模块说明
│   │   ├── linuxdo/               # Linux.do 论坛
│   │   │   ├── config.yaml        # 独立配置（含 AI）
│   │   │   ├── adapter.py         # 适配器
│   │   │   ├── ai_analyzer.py     # AI 分析器（模块专用）
│   │   │   └── run.py             # 独立运行脚本
│   │   ├── v2ex/                  # 🆕 V2EX 论坛
│   │   │   ├── config.yaml
│   │   │   ├── adapter.py
│   │   │   └── run.py
│   │   └── hostloc/               # 🆕 全球主机论坛
│   │       ├── config.yaml
│   │       ├── adapter.py
│   │       └── run.py
│   │
│   ├── game/                      # 🔹 游戏类模块
│   │   ├── README.md              # 游戏模块说明
│   │   ├── mihoyo/                # 🆕 米哈游（原神/崩铁等）
│   │   │   ├── config.yaml
│   │   │   ├── adapter.py
│   │   │   └── run.py
│   │   ├── bilibili/              # 🆕 B站游戏签到
│   │   │   ├── config.yaml
│   │   │   ├── adapter.py
│   │   │   └── run.py
│   │   └── steam/                 # 🆕 Steam 相关
│   │       ├── config.yaml
│   │       ├── adapter.py
│   │       └── run.py
│   │
│   └── custom/                    # 🔹 自定义类模块
│       ├── README.md              # 自定义模块说明
│       └── template/              # 模块模板
│           ├── config.yaml.example
│           ├── adapter.py.template
│           └── run.py.template
│
├── storage/                       # 存储目录
│   ├── sessions/                  # 浏览器会话
│   ├── cache/                     # 缓存数据
│   └── data/                      # 持久化数据
│
├── logs/                          # 日志目录
│   ├── checkin/                   # 签到日志
│   ├── forum/                     # 论坛日志
│   └── game/                      # 游戏日志
│
├── scripts/                       # 工具脚本
│   ├── install.sh                 # 安装脚本
│   ├── batch_run.py               # 批量运行脚本
│   └── module_generator.py        # 模块生成器
│
├── docs/                          # 文档目录
│   ├── GETTING_STARTED.md         # 快速开始
│   ├── MODULE_DEVELOPMENT.md      # 模块开发指南
│   ├── ARCHITECTURE.md            # 架构说明
│   └── API_REFERENCE.md           # API 参考
│
└── tests/                         # 测试目录
    ├── test_browser.py
    ├── test_modules.py
    └── test_notifiers.py
```

### 架构特点

#### 1. **模块化设计** 🧩
- 每个功能都是独立模块
- 每个模块包含：配置、适配器、运行脚本
- 模块间完全隔离，互不影响

#### 2. **按类型分组** 📁
- `checkin/` - 网站签到类
- `forum/` - 论坛内容类
- `game/` - 游戏相关类
- `custom/` - 自定义扩展

#### 3. **共享基础设施** 🔧
- `core/` 目录包含所有模块共用的工具
- 浏览器管理、日志、通知等统一管理
- 减少代码重复

#### 4. **易于扩展** ➕
- 提供模块模板
- 添加新功能只需复制模板
- 遵循统一规范

---

## 🔄 迁移方案

### 步骤 1：创建新目录结构

```bash
# 创建核心目录
mkdir -p core/notifiers
mkdir -p modules/{checkin,forum,game,custom}/template
mkdir -p storage/{sessions,cache,data}
mkdir -p logs/{checkin,forum,game}
mkdir -p scripts docs tests

# 移动现有文件
mv src/browser_manager.py core/
mv src/notifiers/* core/notifiers/

# 迁移 anyrouter
mkdir -p modules/checkin/anyrouter
mv run_anyrouter.py modules/checkin/anyrouter/run.py
mv config/anyrouter.yaml modules/checkin/anyrouter/config.yaml
mv src/adapters/anyrouter.py modules/checkin/anyrouter/adapter.py

# 迁移 linuxdo
mkdir -p modules/forum/linuxdo
mv run_linuxdo.py modules/forum/linuxdo/run.py
mv config/linuxdo.yaml modules/forum/linuxdo/config.yaml
mv src/adapters/linuxdo.py modules/forum/linuxdo/adapter.py
mv src/ai_analyzer.py modules/forum/linuxdo/ai_analyzer.py
```

### 步骤 2：更新导入路径

所有模块导入改为：
```python
# 旧方式
from src.browser_manager import BrowserManager
from src.notifiers.email import EmailNotifier

# 新方式
from core.browser_manager import BrowserManager
from core.notifiers.email import EmailNotifier
```

### 步骤 3：更新运行方式

```bash
# 旧方式
python3 run_anyrouter.py
python3 run_linuxdo.py

# 新方式
python3 modules/checkin/anyrouter/run.py
python3 modules/forum/linuxdo/run.py

# 或使用快捷脚本
python3 scripts/batch_run.py --module checkin.anyrouter
python3 scripts/batch_run.py --module forum.linuxdo
```

---

## 📦 模块标准规范

### 每个模块必须包含：

#### 1. `config.yaml` - 配置文件
```yaml
module:
  name: module_name
  type: checkin|forum|game|custom
  description: 模块描述

site:
  url: https://example.com
  accounts:
    - username: user
      password: pass
      enabled: true

# 模块特定配置...
```

#### 2. `adapter.py` - 适配器
```python
from core.base_adapter import BaseAdapter, TaskResult

class ModuleAdapter(BaseAdapter):
    """模块适配器"""

    def __init__(self, config, logger=None):
        super().__init__(config, logger)

    async def execute(self) -> TaskResult:
        """执行主要任务"""
        pass
```

#### 3. `run.py` - 独立运行脚本
```python
import asyncio
from pathlib import Path
from core.runner import ModuleRunner

async def main():
    runner = ModuleRunner(
        module_path=Path(__file__).parent,
        adapter_class='adapter.ModuleAdapter'
    )
    await runner.run()

if __name__ == '__main__':
    asyncio.run(main())
```

#### 4. `README.md` - 模块说明（可选）
- 功能描述
- 配置说明
- 使用示例

---

## 🎨 统一运行器

创建 `core/runner.py` 统一运行逻辑：

```python
class ModuleRunner:
    """通用模块运行器"""

    def __init__(self, module_path, adapter_class):
        self.module_path = module_path
        self.adapter_class = adapter_class

    async def run(self):
        # 1. 加载配置
        # 2. 初始化浏览器
        # 3. 执行适配器
        # 4. 发送通知
        # 5. 清理资源
        pass
```

---

## 🚀 批量运行脚本

创建 `scripts/batch_run.py`：

```python
#!/usr/bin/env python3
"""批量运行多个模块"""

import asyncio
import argparse

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--modules', nargs='+', help='模块列表')
    parser.add_argument('--type', choices=['checkin', 'forum', 'game'])
    parser.add_argument('--all', action='store_true', help='运行所有模块')

    args = parser.parse_args()

    # 批量执行逻辑...

if __name__ == '__main__':
    asyncio.run(main())
```

使用方式：
```bash
# 运行指定模块
python3 scripts/batch_run.py --modules checkin.anyrouter forum.linuxdo

# 运行某一类型的所有模块
python3 scripts/batch_run.py --type checkin

# 运行所有模块
python3 scripts/batch_run.py --all
```

---

## 🔧 模块生成器

创建 `scripts/module_generator.py`：

```bash
# 快速创建新模块
python3 scripts/module_generator.py --name glados --type checkin

# 生成的文件：
# modules/checkin/glados/
#   ├── config.yaml
#   ├── adapter.py
#   ├── run.py
#   └── README.md
```

---

## 📊 优势对比

| 特性 | 当前架构 | 新架构 |
|------|----------|--------|
| 可扩展性 | ⚠️ 中等 | ✅ 极强 |
| 模块独立性 | ✅ 好 | ✅ 完美 |
| 代码组织 | ⚠️ 较散 | ✅ 清晰 |
| 添加新功能 | ⚠️ 需手动配置 | ✅ 使用生成器 |
| 批量运行 | ❌ 不支持 | ✅ 统一脚本 |
| 文档完整性 | ⚠️ 一般 | ✅ 完善 |

---

## 🗓️ 实施建议

### 阶段 1：基础重构（第1周）
1. 创建新目录结构
2. 迁移现有两个模块
3. 更新导入路径
4. 测试确保功能正常

### 阶段 2：工具开发（第2周）
1. 开发统一运行器
2. 开发批量运行脚本
3. 开发模块生成器
4. 编写开发文档

### 阶段 3：扩展功能（第3周+）
1. 添加游戏签到模块
2. 添加其他论坛模块
3. 添加更多网络服务模块
4. 优化和完善

---

## 🎯 未来展望

### 可能的扩展方向

1. **Web 管理界面**
   - 可视化配置
   - 实时日志查看
   - 任务调度管理

2. **插件系统**
   - 支持第三方模块
   - 模块市场
   - 一键安装

3. **云端部署**
   - Docker 容器化
   - K8s 支持
   - Serverless 部署

4. **监控告警**
   - 任务执行监控
   - 失败告警
   - 性能分析

---

## 💡 总结

新架构将使项目：
- ✅ 更易于扩展新功能
- ✅ 更好的代码组织
- ✅ 更简单的维护
- ✅ 更专业的形象
- ✅ 更强大的功能

**推荐项目名称**：`automation-hub`
**推荐架构方案**：按功能类型分组

---

## 📝 下一步

1. 确认项目新名称
2. 确认架构方案
3. 开始实施迁移
4. 逐步添加新功能

你觉得这个方案如何？需要调整吗？
