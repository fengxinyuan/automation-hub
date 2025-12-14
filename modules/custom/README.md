# 自定义模块

## 📝 模块模板

本目录提供模块开发模板，帮助快速创建新模块。

## 📁 模板文件

- `config.yaml.example` - 配置文件模板
- `adapter.py.template` - 适配器代码模板
- `run.py.template` - 运行脚本模板

## 🚀 使用模板创建新模块

### 方法 1：使用模块生成器（推荐）

```bash
# 从项目根目录运行
python3 scripts/module_generator.py --name 模块名 --type checkin|forum|game|custom
```

### 方法 2：手动复制模板

```bash
# 1. 创建新模块目录
mkdir modules/类型/模块名

# 2. 复制模板文件
cp modules/custom/template/config.yaml.example modules/类型/模块名/config.yaml
cp modules/custom/template/adapter.py.template modules/类型/模块名/adapter.py
cp modules/custom/template/run.py.template modules/类型/模块名/run.py

# 3. 编辑文件，替换占位符
# - 修改 config.yaml 中的站点信息
# - 修改 adapter.py 中的逻辑实现
# - 修改 run.py 中的导入路径和模块名

# 4. 运行测试
chmod +x modules/类型/模块名/run.py
python3 modules/类型/模块名/run.py --dry-run
```

## 📝 开发步骤

### 1. 分析目标网站

- 登录方式（用户名/邮箱 + 密码）
- 登录状态检查方法
- 签到/任务执行方式
- 结果获取方法

### 2. 修改配置文件

编辑 `config.yaml`：
- 设置站点 URL
- 配置账号信息
- 调整浏览器参数

### 3. 实现适配器

编辑 `adapter.py`，实现三个关键方法：

```python
async def is_logged_in(self) -> bool:
    """检查是否已登录"""
    # 检查页面上是否有登录状态指示器

async def login(self) -> bool:
    """执行登录"""
    # 填写用户名密码，提交表单

async def checkin(self) -> TaskResult:
    """执行主要任务"""
    # 执行签到或其他操作，返回结果
```

### 4. 调试测试

```bash
# 调试模式（显示浏览器）
python3 run.py --debug

# 模拟运行
python3 run.py --dry-run

# 正式运行
python3 run.py
```

## 🔍 选择器查找技巧

使用浏览器开发者工具（F12）：
1. 选择元素检查器
2. 找到目标元素
3. 右键 > Copy > Copy selector

常用选择器：
- `#id` - ID 选择器
- `.class` - 类选择器
- `input[name="username"]` - 属性选择器
- `button[type="submit"]` - 组合选择器

## 📚 相关文档

- [Playwright 文档](https://playwright.dev/python/)
- [CSS 选择器参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Selectors)
- [模块开发指南](../../../docs/MODULE_DEVELOPMENT.md)
- [项目架构说明](../../../ARCHITECTURE_REFACTOR.md)
