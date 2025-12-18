# ✅ 自动运行配置完成指南

## 📋 已完成的配置

### 1. 自动运行脚本
- **位置**: `/root/automation-hub/run_daily.sh`
- **功能**:
  - AnyRouter 自动签到
  - Linux.do 论坛智能总结
  - 自动清理30天前的日志

### 2. 定时任务（Cron）
- **配置文件**: `/root/automation-hub/crontab.txt`
- **执行时间**: 每天北京时间 9:00 AM
- **查看任务**: `crontab -l`

### 3. 日志系统
- **日志目录**: `/root/automation-hub/storage/logs/`
- **每日日志**: `daily_YYYYMMDD.log`
- **Cron日志**: `cron.log`
- **自动清理**: 保留最近30天

---

## 📧 邮箱配置（待完成）

### 配置步骤：

1. **编辑配置文件**
   ```bash
   nano /root/automation-hub/modules/forum/linuxdo/config.yaml
   ```

2. **修改 notifications 部分**
   ```yaml
   notifications:
     email:
       enabled: true  # 改为 true
       smtp_server: smtp.gmail.com
       smtp_port: 587
       use_tls: true
       username: your-email@gmail.com  # 你的邮箱
       password: your-app-password     # 应用专用密码
       to_addresses:
         - your-email@gmail.com  # 接收邮箱
   ```

3. **获取 Gmail 应用专用密码**
   - 访问：https://myaccount.google.com/apppasswords
   - 选择"邮件" → "Linux 电脑"
   - 生成并复制 16 位密码

4. **测试邮件发送**
   ```bash
   cd /root/automation-hub
   python3 modules/forum/linuxdo/run.py
   ```

📖 **详细配置说明**: 查看 `/root/automation-hub/EMAIL_SETUP.md`

---

## 🕐 运行时间说明

当前配置：**每天北京时间 9:00 AM**

### 修改运行时间：

1. **编辑 crontab 文件**
   ```bash
   nano /root/automation-hub/crontab.txt
   ```

2. **修改时间**（格式：分 时 日 月 周）
   ```
   # 每天北京时间 8:00 AM（UTC 0:00）
   0 0 * * * /root/automation-hub/run_daily.sh >> /root/automation-hub/storage/logs/cron.log 2>&1

   # 每天北京时间 21:00 PM（UTC 13:00）
   0 13 * * * /root/automation-hub/run_daily.sh >> /root/automation-hub/storage/logs/cron.log 2>&1

   # 每天两次：9:00 和 21:00
   0 1,13 * * * /root/automation-hub/run_daily.sh >> /root/automation-hub/storage/logs/cron.log 2>&1
   ```

3. **应用新配置**
   ```bash
   crontab /root/automation-hub/crontab.txt
   ```

### 时区对照表
| 北京时间 | UTC 时间 | Cron 时间 |
|---------|---------|----------|
| 08:00   | 00:00   | 0 0      |
| 09:00   | 01:00   | 0 1      |
| 12:00   | 04:00   | 0 4      |
| 18:00   | 10:00   | 0 10     |
| 21:00   | 13:00   | 0 13     |

---

## 🧪 测试命令

### 手动运行一次
```bash
/root/automation-hub/run_daily.sh
```

### 查看最新日志
```bash
tail -f /root/automation-hub/storage/logs/cron.log
```

### 查看今天的日志
```bash
cat /root/automation-hub/storage/logs/daily_$(date +%Y%m%d).log
```

### 查看论坛总结
```bash
ls -lt /root/automation-hub/storage/data/ | head -5
```

---

## 📊 运行结果

每次运行后会生成：

1. **日志文件** (`storage/logs/daily_*.log`)
   - 包含签到和论坛总结的详细日志
   - 记录成功/失败状态

2. **论坛总结文件** (`storage/data/`)
   - `linuxdo_summary_*.txt` - 可读的文本总结
   - `linuxdo_summary_*.json` - 完整的 JSON 数据

3. **邮件通知**（如果已配置）
   - 自动发送到你的邮箱
   - 包含推荐帖子和最新动态

---

## 🔧 常用命令

```bash
# 查看 cron 任务
crontab -l

# 查看 cron 服务状态
systemctl status cron

# 重启 cron 服务
systemctl restart cron

# 查看最近的日志
tail -50 /root/automation-hub/storage/logs/cron.log

# 手动测试运行
/root/automation-hub/run_daily.sh

# 查看磁盘使用情况
du -sh /root/automation-hub/storage/
```

---

## ❓ 故障排查

### 问题1: Cron 没有执行
```bash
# 检查 cron 服务状态
systemctl status cron

# 如果未启动，启动服务
systemctl start cron

# 设置开机自启
systemctl enable cron

# 检查 cron 日志
grep CRON /var/log/syslog | tail -20
```

### 问题2: 脚本执行失败
```bash
# 检查脚本权限
ls -l /root/automation-hub/run_daily.sh

# 如果没有执行权限，添加权限
chmod +x /root/automation-hub/run_daily.sh

# 手动运行测试
bash -x /root/automation-hub/run_daily.sh
```

### 问题3: Python 环境问题
```bash
# 检查 Python 版本
python3 --version

# 检查依赖包
pip3 list | grep playwright

# 重新安装依赖
pip3 install -r /root/automation-hub/requirements.txt
```

---

## 🎉 配置完成！

一切配置完成后，系统会：
- ✅ 每天自动签到 AnyRouter
- ✅ 每天自动总结 Linux.do 论坛
- ✅ 自动生成推荐列表（根据你的兴趣）
- ✅ 发送邮件通知（如果已配置）
- ✅ 自动清理旧日志

**下一步**: 配置邮箱通知，查看 `EMAIL_SETUP.md` 文件。

**明天早上 9:00** 检查你的邮箱和日志文件，看看自动化是否正常运行！ 🚀
