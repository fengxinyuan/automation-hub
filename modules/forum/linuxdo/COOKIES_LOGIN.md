# Linux.do Cookies 登录指南

## 为什么需要 Cookies 登录？

Linux.do 使用 Cloudflare 进行人机验证，自动登录很容易被拦截。通过手动登录一次并导出 cookies，可以绕过这个问题。

## 使用步骤

### 1. 运行导出工具

在服务器上运行（需要图形界面或 X11 转发）：

```bash
cd /root/automation-hub
python3 tools/export_linuxdo_cookies.py
```

### 2. 手动登录

工具会打开浏览器窗口，请：

1. 等待 Cloudflare 验证通过
2. 点击右上角「登录」按钮
3. 输入邮箱和密码
4. 完成登录

### 3. 导出 Cookies

登录成功后，回到终端按回车键，工具会自动导出 cookies 到：

```
/root/automation-hub/modules/forum/linuxdo/cookies.json
```

### 4. 验证

运行自动化脚本测试：

```bash
# 测试自动阅读
bash run_auto_read.sh

# 查看日志，应该看到：
# "尝试使用保存的 cookies 登录..."
# "✓ Cookies 登录成功"
```

## Cookies 文件格式

`cookies.json` 文件包含：

```json
{
  "cookies": [
    {
      "name": "_t",
      "value": "登录token...",
      "domain": ".linux.do",
      ...
    },
    {
      "name": "cf_clearance",
      "value": "cloudflare token...",
      "domain": ".linux.do",
      ...
    }
  ],
  "exported_at": 时间戳,
  "note": "说明"
}
```

## 关键 Cookies

- **_t**: Discourse 论坛的登录 token（必需）
- **cf_clearance**: Cloudflare 验证 token（推荐）
- **__cf_bm**: Cloudflare Bot Manager（可选）

## 故障排查

### 1. Cookies 失效

如果看到日志：`Cookies 已失效，尝试常规登录...`

**原因**：
- Cookies 过期（通常30天）
- IP地址变化
- Cloudflare token 失效

**解决**：重新运行导出工具

### 2. 未检测到登录 token

导出时显示：`⚠️ 警告：未检测到登录 cookie (_t)`

**原因**：没有成功登录

**解决**：
1. 确认已经完成登录
2. 在浏览器中刷新页面，确认已登录
3. 重新按回车导出

### 3. 无法打开浏览器

错误：`Error: Could not find browser`

**解决**：
```bash
# 安装 Playwright 浏览器
playwright install chromium
```

### 4. 没有图形界面

如果服务器没有图形界面，可以：

**方案 A：在本地电脑导出**
1. 在本地电脑运行导出工具
2. 将 `cookies.json` 上传到服务器

**方案 B：使用 X11 转发**
```bash
# 在本地电脑 SSH 连接时启用 X11
ssh -X user@server
python3 tools/export_linuxdo_cookies.py
```

**方案 C：手动导出（浏览器插件）**
1. 使用浏览器插件导出 cookies（如 EditThisCookie）
2. 手动创建 `cookies.json` 文件
3. 确保包含 `_t` cookie

## Cookies 安全性

**警告**：`cookies.json` 包含你的登录凭证，请：

- ✅ 妥善保管，不要分享
- ✅ 定期更新（建议30天一次）
- ✅ 服务器被入侵后立即更改密码
- ❌ 不要提交到 Git 仓库

已添加到 `.gitignore`：
```
modules/forum/linuxdo/cookies.json
```

## 自动化工作流程

配置完成后，自动化脚本的登录流程：

```
1. 检查 cookies.json 是否存在
   ├─ 存在 → 注入 cookies
   │         ├─ 验证登录状态
   │         ├─ 成功 → 开始任务 ✓
   │         └─ 失败 → 尝试常规登录
   └─ 不存在 → 尝试常规登录（可能失败）
```

## 常见问题

**Q: Cookies 多久需要更新一次？**
A: 通常30天，建议定期检查日志，看到失效提示时重新导出。

**Q: 多个账号怎么办？**
A: 每次运行导出工具时登录不同账号，覆盖 cookies.json 即可。或者手动管理多个文件。

**Q: Cookies 和会话文件有什么区别？**
A:
- **Cookies**: 手动导出，长期有效（30天），优先使用
- **会话文件**: 自动保存，每次运行更新，作为备份

**Q: 可以在 cron 任务中使用吗？**
A: 可以！配置好 cookies 后，cron 定时任务会自动使用。
