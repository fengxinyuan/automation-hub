# Linux.do AI 智能分析和推荐功能 - 完整指南

## 🤖 功能概述

全新的 AI 智能分析功能，让你无需花时间浏览，即可：
1. **AI 智能总结** - 使用大语言模型理解帖子内容，生成高质量摘要
2. **个性化推荐** - AI 分析所有帖子，找出你最可能感兴趣的话题
3. **更多帖子分析** - 获取 30 个帖子（最新20 + 热门10），全面覆盖
4. **情感分析** - 判断帖子的情感倾向
5. **智能标签** - 自动提取主题关键词

## ✨ 新功能

### 1. AI 智能推荐（核心功能）
- 分析所有帖子内容和元数据
- 计算相关度分数（0-100）
- 生成推荐理由和关键标签
- 按相关度排序，优先显示最感兴趣的

### 2. AI 深度分析
- 对热门帖子进行深度阅读
- 生成一句话摘要（50字以内）
- 提取3个关键要点
- 识别主题标签
- 分析情感倾向（positive/neutral/negative）

### 3. 增强的数据收集
- 最新帖子：20个（原来10个）
- 热门帖子：10个（原来5个）
- 内容阅读：5个（原来3个）
- AI 分析：前3个热门帖子

## 🔧 配置 AI 功能

### 方式一：使用 OpenAI API（推荐）

1. **获取 API Key**
   - 访问 https://platform.openai.com/api-keys
   - 创建新的 API Key
   - 复制保存

2. **配置环境变量**

创建或编辑 `.env` 文件：

```bash
cd /root/auto-checkin
cp .env.example .env
nano .env
```

添加配置：

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# 使用的模型（可选，默认 gpt-3.5-turbo）
AI_MODEL=gpt-3.5-turbo

# 如果使用 gpt-4 获得更好效果
# AI_MODEL=gpt-4-turbo
```

### 方式二：使用国内中转服务

如果无法直接访问 OpenAI：

```bash
# API Key
OPENAI_API_KEY=your-api-key

# 中转服务端点
OPENAI_API_BASE=https://api.your-proxy.com/v1

# 模型
AI_MODEL=gpt-3.5-turbo
```

### 方式三：使用其他 AI 服务

支持任何兼容 OpenAI API 格式的服务：

```bash
AI_API_KEY=your-api-key
AI_API_BASE=https://your-ai-service.com/api
AI_MODEL=your-model-name
```

### 不配置 AI（简化模式）

如果不配置 AI API：
- ✅ 仍然可以运行
- ✅ 使用简单文本提取
- ✅ 按热度排序推荐
- ❌ 没有 AI 智能总结
- ❌ 没有深度内容分析

## 📊 输出示例

### 日志输出

```
============================================================
Linux.do 论坛智能分析报告
============================================================

【🎯 为你推荐 - 最可能感兴趣的话题】

1. 社区公约更新公告
   📊 相关度: 95% | 💬 500 | 👁️ 5k
   📝 推荐理由: 社区重要公告，与所有用户相关
   🏷️ 站务, 公告, 规则
   🔗 https://linux.do/t/xxxxx

2. 一张虚拟卡能白嫖多少大厂的服务器？
   📊 相关度: 88% | 💬 300 | 👁️ 3k
   📝 推荐理由: 实用技术分享，适合技术爱好者
   🏷️ 技术, 云服务, 白嫖
   🔗 https://linux.do/t/xxxxx

...

【🤖 AI 深度分析】

1. 请不要把互联网上的戾气带来这里！
   作者: admin | 分类: 站务
   📝 AI 摘要: 呼吁社区成员保持理性讨论，避免带入负面情绪
   🔑 关键要点:
      • 保持友善和尊重
      • 理性表达观点
      • 共同维护社区环境
   🏷️ 主题标签: 社区文化, 行为规范, 理性讨论
   💭 情感倾向: 😐 neutral
   🔗 https://linux.do/t/xxxxx

...

【📰 最新帖子】
（10个最新帖子）

【🔥 热门话题】
（10个热门帖子）

============================================================
📊 统计: 共分析 30 个帖子
🎯 为你推荐 5 个最相关话题
🤖 AI 深度分析 3 个热门帖子
============================================================
```

### 邮件推送

邮件会包含更美观的 HTML 格式：

1. **🎯 AI 推荐** - 渐变背景卡片，突出显示
   - 相关度分数
   - 推荐理由
   - 关键标签

2. **🤖 AI 深度分析** - 蓝色卡片
   - AI 生成的摘要
   - 关键要点列表
   - 主题标签和情感

3. **📰 最新帖子** - 列表显示（10个）

4. **🔥 热门话题** - 列表显示（10个）

## 🚀 使用方法

### 1. 基本使用

```bash
cd /root/auto-checkin

# 运行（自动使用 AI 如果已配置）
python3 src/main.py --site linuxdo

# 查看结果
tail -100 logs/checkin.log
```

### 2. 定时运行

```bash
crontab -e

# 每天早上 8:00 自动运行
0 8 * * * cd /root/auto-checkin && python3 src/main.py --site linuxdo >> logs/cron.log 2>&1
```

## 💰 成本估算

### OpenAI API 费用

使用 `gpt-3.5-turbo`:
- 每次运行：约 $0.01 - $0.02
- 每月运行30次：约 $0.30 - $0.60
- 非常便宜！

使用 `gpt-4-turbo`:
- 每次运行：约 $0.05 - $0.10
- 每月运行30次：约 $1.50 - $3.00
- 效果更好，但费用稍高

## 📈 AI vs 非 AI 对比

| 功能 | 不使用 AI | 使用 AI |
|------|----------|---------|
| 获取帖子数 | 15个 | 30个 |
| 内容理解 | 简单文本提取 | 深度语义理解 |
| 推荐准确度 | 按热度排序 | 智能相关度分析 |
| 摘要质量 | 截取前N字 | 语义理解后提炼 |
| 关键信息 | 提取列表项 | 智能识别要点 |
| 推荐理由 | 无 | 生成推荐理由 |
| 主题标签 | 无 | 自动生成标签 |
| 情感分析 | 无 | 识别情感倾向 |

## 🎯 推荐场景

### 适合使用 AI：
- ✅ 希望获得高质量内容摘要
- ✅ 想要个性化推荐
- ✅ 不差这点 API 费用
- ✅ 追求最佳体验

### 可以不使用 AI：
- ❌ 只想简单看看帖子标题
- ❌ 不想配置 API
- ❌ 对费用非常敏感
- ❌ 网络环境不便访问 AI 服务

## 🔧 故障排查

### 1. AI 功能未启用

检查日志是否有：
```
未配置 AI API 密钥，将使用简单文本提取
```

解决：
- 确认 `.env` 文件存在
- 确认 `OPENAI_API_KEY` 已配置
- 重新运行

### 2. API 调用失败

可能原因：
- API Key 无效
- 网络无法访问 OpenAI
- API 额度不足

解决：
- 检查 API Key 是否正确
- 检查网络连接
- 确认 OpenAI 账户余额
- 考虑使用国内中转服务

### 3. 安装依赖

如果提示缺少 `openai` 库：

```bash
pip3 install openai
```

## 📝 高级配置

### 自定义用户兴趣画像

可以在配置文件中添加用户兴趣画像，让推荐更精准：

编辑 `config/sites.yaml`：

```yaml
linuxdo:
  url: https://linux.do
  accounts:
    - username: your-email@gmail.com
      password: your-password
      enabled: true
      # 用户兴趣画像（可选）
      interests:
        - 云计算
        - Docker
        - Linux 服务器
        - 开源软件
        - 白嫖技巧
```

### 调整 AI 模型参数

编辑 `src/ai_analyzer.py`，找到模型调用部分：

```python
response = await openai.ChatCompletion.acreate(
    model=self.model,
    messages=[...],
    temperature=0.7,  # 降低=更保守，提高=更创造性
    max_tokens=500    # 响应长度限制
)
```

## 📚 相关文档

- **API 文档**: https://platform.openai.com/docs
- **模型定价**: https://openai.com/pricing
- **项目 README**: `/root/auto-checkin/README.md`
- **使用指南**: `/root/auto-checkin/docs/LINUXDO_GUIDE.md`

## 🎊 总结

AI 智能分析功能让 Linux.do 自动化体验提升到新高度：

**之前**: 获取帖子列表 + 简单文本提取
**现在**: AI 深度理解 + 智能推荐 + 个性化分析

开始使用：
```bash
# 1. 配置 AI API Key
nano .env

# 2. 运行
python3 src/main.py --site linuxdo

# 3. 享受 AI 智能分析！
```

Happy Reading! 🚀
