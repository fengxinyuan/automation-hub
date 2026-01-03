# Linux.do 论坛自动化模块

> 智能获取 Linux.do 论坛内容并进行 AI 分析，生成个性化推荐

## ✨ 功能特性

- 🔐 自动登录，会话持久化
- 📰 获取最新帖子、热门话题
- 🎯 智能过滤，基于分类和质量评分
- 🤖 AI 分析和内容摘要
- 💡 个性化推荐
- 📧 邮件通知
- 💾 缓存优化，7天有效期

## 🚀 快速开始

### 1. 配置

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入账号和配置
```

### 2. 配置 AI（可选）

```bash
# 获取阿里云 API Key: https://dashscope.console.aliyun.com/apiKey
echo "DASHSCOPE_API_KEY=sk-your-key" > /root/automation-hub/.env
```

### 3. 运行

```bash
python3 run.py              # 正常运行
python3 run.py --debug      # 调试模式
python3 run.py --dry-run    # 模拟运行
```

## 📋 主要配置

```yaml
content:
  latest_topics_limit: 20    # 最新帖子数量
  hot_topics_limit: 10       # 热门帖子数量
  read_content_limit: 5      # 深度阅读数量
  ai_analysis_limit: 3       # AI 分析数量

filter:
  exclude_categories:        # 排除的分类
    - 公告
    - 站务
  priority_categories:       # 优先技术分类
    - Linux
    - Docker
    - DevOps

ai:
  enabled: true
  api_key: ${DASHSCOPE_API_KEY}
  model: qwen-flash
  user_interests:            # 兴趣画像
    - Linux 服务器管理
    - Docker 容器
```

## 📊 输出结果

运行后生成：
- `storage/data/linuxdo_summary_*.txt` - 可读文本摘要
- `storage/data/linuxdo_summary_*.json` - 完整JSON数据
- `storage/cache/` - 帖子分析缓存
- 邮件报告（如启用）

## 🔧 故障排查

**登录失败**
- 检查用户名密码
- 使用 `--debug` 查看详细日志

**AI 未生效**
- 检查 `.env` 中的 `DASHSCOPE_API_KEY`
- 确认配置 `ai.enabled: true`

**内容获取失败**
- 清理会话重新登录：`rm -rf storage/sessions/linuxdo_*`

## 🔄 定时任务

```bash
# 每天12点运行
0 12 * * * cd /root/automation-hub/modules/forum/linuxdo && python3 run.py
```

---

详细配置说明见 [config.yaml.example](config.yaml.example)
