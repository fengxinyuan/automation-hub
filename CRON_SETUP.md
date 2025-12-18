# 定时任务配置说明

## 已配置的定时任务

项目已配置以下定时任务，每天自动运行：

### 1. AnyRouter 自动签到
- **运行时间**: 每天早上 8:00
- **执行脚本**: `modules/checkin/anyrouter/run.py`
- **日志文件**: `logs/anyrouter_cron.log`
- **功能**: 自动为配置的 3 个账号执行签到，获取账户余额

### 2. Linux.do 论坛分析
- **运行时间**: 每天早上 9:00
- **执行脚本**: `modules/forum/linuxdo/run.py`
- **日志文件**: `logs/linuxdo_cron.log`
- **功能**: 
  - 获取最新帖子和热门帖子
  - AI 智能分析和推荐
  - 生成论坛动态报告
  - 发送邮件通知

## Crontab 配置

```bash
# 查看当前定时任务
crontab -l

# 当前配置
0 8 * * * /usr/bin/python3 modules/checkin/anyrouter/run.py >> logs/anyrouter_cron.log 2>&1
0 9 * * * /usr/bin/python3 modules/forum/linuxdo/run.py >> logs/linuxdo_cron.log 2>&1
```

## 邮件通知

两个任务完成后都会自动发送邮件通知到配置的邮箱 (`3070915889@qq.com`)：

- **AnyRouter**: 包含签到结果和账户余额信息
- **Linux.do**: 包含 AI 推荐帖子、深度分析、最新帖子和热门话题

## 查看日志

```bash
# 查看 AnyRouter 日志
tail -f /root/test/automation-hub/logs/anyrouter_cron.log

# 查看 Linux.do 日志
tail -f /root/test/automation-hub/logs/linuxdo_cron.log
```

## 手动运行

如需手动测试，可以直接运行：

```bash
# 进入项目目录
cd /root/test/automation-hub

# 运行 AnyRouter 签到
python3 modules/checkin/anyrouter/run.py

# 运行 Linux.do 论坛分析
python3 modules/forum/linuxdo/run.py
```

## 修改运行时间

如需修改定时任务的运行时间，编辑 crontab：

```bash
crontab -e
```

时间格式说明：
- `0 8 * * *` = 每天早上 8:00
- `0 9 * * *` = 每天早上 9:00
- `0 20 * * *` = 每天晚上 8:00
- `0 */6 * * *` = 每 6 小时运行一次

## 停用定时任务

如需临时停用，可以在对应行前加 `#` 注释：

```bash
crontab -e

# 注释掉某个任务
# 0 8 * * * /usr/bin/python3 modules/checkin/anyrouter/run.py >> logs/anyrouter_cron.log 2>&1
```

---

生成时间: 2025-12-19
