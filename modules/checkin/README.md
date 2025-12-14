# 签到类模块

## 📝 模块列表

- **anyrouter** - AnyRouter 路由器服务签到 ✅
- **glados** - GLaDOS 签到（待添加）
- **ikuuu** - ikuuu 签到（待添加）
- **其他** - 更多签到网站...

## ➕ 添加新模块

### 方式 1：使用模块生成器（推荐）

```bash
# 从项目根目录运行
python3 scripts/module_generator.py --name 新模块名 --type checkin
```

### 方式 2：手动创建

1. **创建模块目录**：
   ```bash
   mkdir modules/checkin/新模块名
   ```

2. **复制模板文件**：
   ```bash
   cp modules/custom/template/* modules/checkin/新模块名/
   ```

3. **编辑配置文件** (`config.yaml`)：
   ```yaml
   site:
     name: 模块名
     url: https://example.com
     accounts:
       - username: your-username
         password: your-password
         enabled: true
   ```

4. **编写适配器** (`adapter.py`)：
   ```python
   from core.base_adapter import BaseAdapter, TaskResult

   class YourAdapter(BaseAdapter):
       async def is_logged_in(self) -> bool:
           # 检查登录状态
           pass

       async def login(self) -> bool:
           # 执行登录
           pass

       async def checkin(self) -> TaskResult:
           # 执行签到
           pass
   ```

5. **运行测试**：
   ```bash
   python3 modules/checkin/新模块名/run.py --dry-run
   ```

## 📚 参考示例

查看 `anyrouter` 模块作为参考实现：
- [anyrouter/config.yaml](anyrouter/config.yaml)
- [anyrouter/adapter.py](anyrouter/adapter.py)
- [anyrouter/run.py](anyrouter/run.py)

## 🔧 开发指南

详见 [模块开发指南](../../../docs/MODULE_DEVELOPMENT.md)
