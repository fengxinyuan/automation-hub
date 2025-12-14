# 论坛类模块

## 📝 模块列表

- **linuxdo** - Linux.do 论坛（含 AI 智能分析）✅
- **v2ex** - V2EX 论坛（待添加）
- **hostloc** - 全球主机论坛（待添加）
- **其他** - 更多论坛网站...

## 🤖 AI 功能

论坛类模块支持 AI 智能分析功能：
- AI 内容总结
- AI 智能推荐
- 关键信息提取
- 情感分析

使用阿里云通义千问 qwen-flash 模型。

## ➕ 添加新模块

### 方式 1：使用模块生成器（推荐）

```bash
python3 scripts/module_generator.py --name 新模块名 --type forum
```

### 方式 2：手动创建

参考 `linuxdo` 模块实现：
- [linuxdo/config.yaml](linuxdo/config.yaml) - 包含 AI 配置
- [linuxdo/adapter.py](linuxdo/adapter.py) - 论坛适配器
- [linuxdo/ai_analyzer.py](linuxdo/ai_analyzer.py) - AI 分析器
- [linuxdo/run.py](linuxdo/run.py) - 运行脚本

## 🔧 开发指南

详见 [模块开发指南](../../../docs/MODULE_DEVELOPMENT.md)
