# Linux.do 阅读和总结功能 - 快速开始

## 🎯 功能特点

**不用花时间浏览，也能知道论坛的最新进度和热门话题！**

### 自动化完成的事情：
1. ✅ 登录 Linux.do 论坛
2. ✅ 获取最新10条帖子信息
3. ✅ 获取热门5条话题信息
4. ✅ **自动阅读前3个热门帖子的内容**
5. ✅ **提取关键信息点**
6. ✅ **生成内容摘要**
7. ✅ 推送到邮件（包含完整摘要）

### 你获得的内容：
- 📰 **最新帖子列表** - 标题、作者、分类、回复数、浏览数
- 🔥 **热门话题列表** - 同上
- 📖 **热门帖子内容精选** - 摘要 + 关键点（无需点击即可了解内容）

## 🚀 开始使用

### 1. 配置已完成
你的账号已配置好：
- 用户名: `happyfengxy@gmail.com`
- 密码: `9876543210fxy`
- 状态: ✅ 已启用

### 2. 立即运行
```bash
cd /root/auto-checkin
python3 src/main.py --site linuxdo
```

**运行时间**: 约90秒
- 获取帖子列表：10秒
- 读取3个热门帖子内容：60秒
- 生成摘要：<1秒

### 3. 查看结果

#### 方式1：查看日志
```bash
tail -100 /root/auto-checkin/logs/checkin.log
```

你会看到完整的摘要，包括：
- 最新帖子列表
- 热门话题列表
- **热门帖子内容精选**（新增！）
  - 帖子摘要（前200字）
  - 关键信息点

#### 方式2：邮件推送（推荐）

如果启用了邮件通知，你会收到HTML格式的邮件，包含：
- 📰 最新帖子（可点击）
- 🔥 热门话题（可点击）
- 📖 **热门帖子内容精选**（新增！）
  - 美观的HTML格式
  - 内容摘要
  - 关键信息点
  - 可点击链接深入阅读

### 4. 设置定时任务

每天自动运行，无需手动操作：

```bash
crontab -e

# 添加以下行：每天早上 8:00 自动运行
0 8 * * * cd /root/auto-checkin && python3 src/main.py --site linuxdo >> logs/cron.log 2>&1
```

## 📧 配置邮件推送（强烈推荐）

要接收邮件推送，编辑 `config/sites.yaml`:

```yaml
notifications:
  email:
    enabled: true  # 改为 true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    use_tls: true
    username: your-email@gmail.com  # 你的邮箱
    password: your-app-password     # Gmail应用专用密码
    to_addresses:
      - your-email@gmail.com  # 接收邮件的地址
```

**Gmail 应用专用密码设置**：
1. 访问 https://myaccount.google.com/security
2. 启用两步验证
3. 生成应用专用密码
4. 将密码填入配置文件

## 📊 示例输出

### 摘要示例
```
============================================================
Linux.do 论坛最新动态
============================================================

【最新帖子】
1. 被阻断2周，L站怎么样了？
   作者: username | 分类: 话题 | 回复: 53.5k | 浏览: 1.8k
   链接: https://linux.do/t/xxxxx

【热门话题】
1. 请不要把互联网上的戾气带来这里！
   作者: admin | 分类: 站务 | 回复: 257k | 浏览: 3.4k
   链接: https://linux.do/t/xxxxx

【热门帖子内容精选】

1. 请不要把互联网上的戾气带来这里！
   链接: https://linux.do/t/xxxxx
   摘要: 最近发现论坛氛围有所变化，出现了一些不友善的言论。
   希望大家能保持理性讨论，互相尊重，共同维护良好的社区环境...
   关键点:
     • 保持理性讨论
     • 互相尊重
     • 维护社区环境

2. ...
============================================================
```

## 🎯 使用价值

### 之前
- 需要打开浏览器
- 需要登录论坛
- 需要逐个浏览帖子
- 花费 5-10 分钟/天

### 现在
- ✅ 自动完成所有操作
- ✅ 直接收到摘要推送
- ✅ 无需点击即可了解内容
- ✅ 花费 0 分钟/天

## 💡 高级技巧

### 1. 调整读取数量

编辑 `src/adapters/linuxdo.py`，找到 `checkin()` 方法：

```python
# 读取热门帖子内容（修改这里的数字）
for i, topic in enumerate(hot_topics[:3], 1):  # 改为 [:5] 读取5个
    ...
```

### 2. 调整摘要长度

在同一文件中，找到 `get_topic_content()` 方法：

```python
# 截取前800字符（修改这里的数字）
if firstPostText.length > 800:
    firstPostText = firstPostText.substring(0, 800) + '...';
```

### 3. 只获取列表不读取内容

如果想快速运行，可以暂时注释掉内容读取部分：

```python
# 注释掉这部分
# topics_with_content = []
# for i, topic in enumerate(hot_topics[:3], 1):
#     ...
```

## 📝 常见问题

### Q: 运行时间太长？
A: 默认读取3个帖子内容约需60秒。可以减少数量或跳过内容读取。

### Q: 如何只看摘要不看帖子列表？
A: 邮件推送和日志都包含"热门帖子内容精选"部分，直接看那部分即可。

### Q: 可以读取更多帖子吗？
A: 可以，但会增加运行时间。每个帖子约20秒。

### Q: 摘要不够详细？
A: 可以调整字符数限制（默认800字符）或增加关键点数量（默认3个）。

## 🔗 相关文档

- 详细功能说明: `READING_SUMMARY_FEATURE.md`
- 完整使用指南: `docs/LINUXDO_GUIDE.md`
- 项目README: `README.md`

## 🎊 开始体验

```bash
# 现在就运行！
cd /root/auto-checkin
python3 src/main.py --site linuxdo

# 等待90秒后查看结果
tail -100 logs/checkin.log
```

祝使用愉快！🚀
