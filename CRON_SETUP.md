# Cron Job Configuration for Auto Check-in

## 当前配置

已设置每日自动签到任务，执行时间为 **每天两次**（服务器时区）。

### Crontab 条目

```
0 9,21 * * * /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

## 时间说明

- **服务器时区**: UTC
- **执行时间**: 每天 09:00 和 21:00 UTC
- **对应北京时间**:
  - **17:00** (傍晚) - UTC 09:00
  - **05:00** (清晨) - UTC 21:00

## 日志文件

- **Cron 执行日志**: `/root/auto-checkin/logs/cron.log`
- **应用日志**: `/root/auto-checkin/logs/checkin.log`
- **截图**: `/root/auto-checkin/logs/*.png`

## 管理命令

### 查看当前配置
```bash
crontab -l
```

### 编辑配置
```bash
crontab -e
```

### 删除所有 cron 任务
```bash
crontab -r
```

### 查看 cron 服务状态
```bash
systemctl status cron
```

### 查看执行日志
```bash
tail -f /root/auto-checkin/logs/cron.log
```

## 其他执行时间示例

### 每 6 小时执行一次
```
0 */6 * * * /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

### 每天午夜执行
```
0 0 * * * /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

### 每天早上 8:30 执行
```
30 8 * * * /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

### 每天两次（早上 9:00 和晚上 21:00）
```
0 9,21 * * * /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

### 工作日执行（周一到周五 9:00）
```
0 9 * * 1-5 /root/auto-checkin/run.sh >> /root/auto-checkin/logs/cron.log 2>&1
```

## Cron 表达式格式

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0 和 7 都表示周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

## 故障排查

### 1. 检查 cron 是否执行
```bash
grep auto-checkin /var/log/syslog
```

### 2. 测试脚本是否可执行
```bash
/root/auto-checkin/run.sh
```

### 3. 检查权限
```bash
ls -l /root/auto-checkin/run.sh
# 应该显示 -rwxr-xr-x 或类似的执行权限
```

### 4. 查看最近的 cron 日志
```bash
tail -50 /root/auto-checkin/logs/cron.log
```

### 5. 手动触发执行（测试）
```bash
cd /root/auto-checkin && ./run.sh
```

## 监控建议

1. **定期检查日志**：
   ```bash
   tail -f /root/auto-checkin/logs/cron.log
   ```

2. **查看执行历史**：
   ```bash
   grep "签到完成" /root/auto-checkin/logs/checkin.log | tail -10
   ```

3. **启用邮件通知**：
   在 `config/sites.yaml` 或 `.env` 中配置邮件通知，失败时会收到邮件

## 备份配置

定期备份 crontab 配置：
```bash
crontab -l > /root/auto-checkin/crontab_backup_$(date +%Y%m%d).txt
```

## 注意事项

1. **时区差异**：注意服务器时区与本地时区的差异
2. **环境变量**：cron 执行时的环境变量可能与登录 shell 不同
3. **路径问题**：脚本中使用绝对路径
4. **权限问题**：确保脚本和日志目录有正确的权限
5. **磁盘空间**：定期清理旧日志文件

## 日志轮转

建议配置日志轮转避免日志文件过大：

创建 `/etc/logrotate.d/auto-checkin`:
```
/root/auto-checkin/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```
