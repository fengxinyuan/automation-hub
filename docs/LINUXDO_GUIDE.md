# Linux.do 论坛自动化使用指南

## 功能简介

Linux.do 自动化脚本可以帮助你：
- 🔐 自动登录 Linux.do 论坛
- 📰 获取最新帖子列表（默认10条）
- 🔥 获取热门话题列表（默认5条）
- 📧 将论坛动态通过邮件推送给你
- 💾 保存登录会话，无需每次重复登录

这样你就不用花时间浏览论坛，也能及时了解最新的讨论和热门话题！

## 配置步骤

### 1. 修改配置文件

编辑 `config/sites.yaml` 文件：

```yaml
sites:
  linuxdo:
    url: https://linux.do
    accounts:
      - username: your_email@example.com  # 你的 Linux.do 用户名或邮箱
        password: your_password            # 你的密码
        enabled: true                      # 改为 true 以启用
```

### 2. 配置邮件通知（可选但推荐）

如果想收到邮件推送，配置邮件通知：

```yaml
notifications:
  email:
    enabled: true  # 启用邮件通知
    smtp_server: smtp.gmail.com
    smtp_port: 587
    use_tls: true
    username: your-email@gmail.com
    password: your-app-password  # Gmail 需要使用应用专用密码
    to_addresses:
      - notify@example.com  # 接收通知的邮箱
```

**Gmail 应用专用密码设置**：
1. 访问 https://myaccount.google.com/security
2. 启用两步验证
3. 生成应用专用密码
4. 将生成的密码填入配置文件

详细说明请参考：[docs/QQ_EMAIL_SETUP.md](docs/QQ_EMAIL_SETUP.md)（QQ邮箱类似）

## 使用方法

### 测试运行

首次运行建议使用测试模式，确保配置正确：

```bash
cd /root/auto-checkin
python3 src/main.py --site linuxdo --dry-run
```

### 正常运行

执行脚本获取 Linux.do 最新动态：

```bash
python3 src/main.py --site linuxdo
```

### 调试模式

如果遇到问题，使用调试模式查看详细信息：

```bash
python3 src/main.py --site linuxdo --debug
```

注意：服务器环境需要使用无头模式（默认），`--debug` 会尝试显示浏览器窗口。

### 定时执行

使用 cron 定时任务每天自动获取论坛动态：

```bash
# 编辑 crontab
crontab -e

# 添加以下行，每天早上 8:00 执行
0 8 * * * cd /root/auto-checkin && /usr/bin/python3 src/main.py --site linuxdo >> logs/cron.log 2>&1
```

更多定时任务配置请参考：[CRON_SETUP.md](CRON_SETUP.md)

## 输出说明

### 日志输出

执行后会在 `logs/checkin.log` 中记录详细日志：

```
============================================================
开始执行自动签到
============================================================

处理站点: linuxdo
开始处理 1 个账号（最大并发: 2）
  ✓ your@example.com: 成功获取论坛最新动态

============================================================
签到完成
成功: 1, 失败: 0
============================================================
```

### 帖子摘要

日志中会包含完整的帖子摘要：

```
============================================================
Linux.do 论坛最新动态
============================================================

【最新帖子】
1. 帖子标题
   作者: username | 分类: 技术讨论 | 回复: 42 | 浏览: 1.2k
   链接: https://linux.do/t/xxxxx

2. ...

【热门话题】
1. ...
============================================================
```

### 邮件推送

如果启用了邮件通知，你会收到格式化的邮件，包含：
- 📰 最新帖子（前5条，带链接）
- 🔥 热门话题（全部，带链接）
- 每个帖子的作者、分类、回复数、浏览数

邮件是 HTML 格式，可以直接点击链接查看感兴趣的帖子。

## 文件说明

```
auto-checkin/
├── src/
│   ├── adapters/
│   │   ├── linuxdo.py          # Linux.do 适配器
│   │   ├── anyrouter.py        # 其他站点适配器
│   │   └── base_adapter.py     # 适配器基类
│   ├── notifiers/
│   │   ├── email.py            # 邮件通知（已增强）
│   │   └── logger.py           # 日志通知
│   ├── main.py                 # 主程序
│   └── browser_manager.py      # 浏览器管理
├── config/
│   └── sites.yaml              # 站点配置
├── storage/
│   └── sessions/               # 保存的登录会话
│       └── linuxdo_*/          # Linux.do 会话数据
├── logs/
│   ├── checkin.log             # 运行日志
│   └── linuxdo_*.png           # 调试截图
└── explore_linuxdo.py          # 探索脚本（可选）
```

## 常见问题

### 1. 登录失败

**原因**：可能是用户名/密码错误，或者 Linux.do 页面结构变化

**解决**：
1. 确认配置文件中的用户名和密码正确
2. 查看 `logs/` 目录下的截图文件，了解登录失败的原因
3. 如果是页面结构变化，可能需要更新适配器代码

### 2. 获取不到帖子

**原因**：可能需要登录才能查看帖子，或者选择器不匹配

**解决**：
1. 确保已成功登录
2. 查看日志中的错误信息
3. 查看截图 `logs/linuxdo_latest_topics.png` 和 `logs/linuxdo_hot_topics.png`

### 3. 邮件发送失败

**原因**：SMTP 配置错误或密码不正确

**解决**：
1. 检查 SMTP 服务器和端口配置
2. 确认使用了应用专用密码（不是登录密码）
3. 查看日志中的详细错误信息

## 高级配置

### 修改获取数量

编辑 `src/adapters/linuxdo.py`：

```python
async def checkin(self) -> CheckinResult:
    # 修改这里的 limit 参数
    latest_topics = await self.get_latest_topics(limit=20)  # 默认 10
    hot_topics = await self.get_hot_topics(limit=10)        # 默认 5
```

### 同时运行多个站点

```bash
# 运行所有启用的站点
python3 src/main.py

# 只运行 Linux.do
python3 src/main.py --site linuxdo

# 只运行 anyrouter
python3 src/main.py --site anyrouter
```

## 安全建议

1. **保护配置文件**：配置文件包含敏感信息，请设置适当的权限
   ```bash
   chmod 600 config/sites.yaml
   ```

2. **使用应用专用密码**：邮件通知建议使用应用专用密码，而不是账号主密码

3. **定期更新密码**：定期更改 Linux.do 和邮箱密码

4. **检查会话文件**：会话文件保存在 `storage/sessions/` 目录，包含登录凭证，请妥善保管

## 贡献与反馈

如果你发现问题或有改进建议：
1. 查看日志文件 `logs/checkin.log`
2. 检查截图文件了解页面状态
3. 提供详细的错误信息

## 更新日志

### 2024-12-14
- ✅ 添加 Linux.do 论坛支持
- ✅ 实现自动登录功能
- ✅ 实现获取最新帖子和热门话题
- ✅ 增强邮件通知，支持帖子摘要推送
- ✅ 支持会话保存，避免重复登录

---

祝使用愉快！🎉
