# 代理配置指南

本项目支持通过 Clash 等代理工具访问需要梯子的网站（如 linux.do 和 anyrouter.top）。

## 🎯 快速开始

### 1. 配置 Clash 订阅（推荐）

使用项目提供的订阅转换脚本 `clash-config-parser.js`，它会自动为每个地区创建：

- **{地区}-自动**：自动测速选最快节点（推荐日常使用）
- **{地区}-故障**：节点挂了自动切换（推荐不稳定时使用）
- **{地区}-手动**：手动选择节点

#### 配置示例

生成的代理组结构：
```
地区选择
├── DIRECT
├── 新加坡
│   ├── 新加坡-自动 ← 推荐
│   ├── 新加坡-故障 ← 节点不稳定时使用
│   └── 新加坡-手动
├── 美国
│   ├── 美国-自动
│   ├── 美国-故障
│   └── 美国-手动
...
```

#### 健康检查机制

```javascript
const HEALTH_CHECK = {
  url: "http://www.gstatic.com/generate_204",
  interval: 300,        // 每 5 分钟测速一次
  tolerance: 50,        // 延迟差 50ms 以内不切换
  timeout: 5000,        // 5 秒超时判定节点不可用
};
```

### 2. 设置系统代理环境变量

#### Linux/macOS

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
# Clash 代理配置
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export ALL_PROXY="socks5://127.0.0.1:7891"
export NO_PROXY="localhost,127.0.0.1,*.local"
```

然后重新加载配置：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

#### 仅为脚本临时设置代理

```bash
# 运行 anyrouter 签到
HTTP_PROXY=http://127.0.0.1:7890 python3 modules/checkin/anyrouter/run.py

# 运行 linuxdo 论坛
HTTP_PROXY=http://127.0.0.1:7890 python3 modules/forum/linuxdo/run.py
```

#### Crontab 定时任务

编辑 crontab：
```bash
crontab -e
```

添加环境变量：
```bash
# Clash 代理
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# 每天早上 8 点运行 anyrouter 签到
0 8 * * * cd /root/automation-hub && python3 modules/checkin/anyrouter/run.py

# 每天早上 9 点运行 linuxdo 论坛
0 9 * * * cd /root/automation-hub && python3 modules/forum/linuxdo/run.py
```

### 3. 验证代理是否生效

运行脚本时会自动打印代理信息：

```
[BrowserManager] 检测到代理: http://127.0.0.1:7890
[BrowserManager] 使用代理: http://127.0.0.1:7890
```

## 🔧 Clash 配置说明

### 端口配置

确保 Clash 配置文件中启用了 HTTP 和 SOCKS5 代理：

```yaml
# Clash 配置
port: 7890              # HTTP 代理端口
socks-port: 7891        # SOCKS5 代理端口
allow-lan: false        # 仅本机使用
mode: rule              # 规则模式
log-level: info
```

### 混合端口（推荐）

如果 Clash 支持混合端口：

```yaml
mixed-port: 7890        # HTTP + SOCKS5 混合端口
```

然后使用：
```bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
```

## 🚀 推荐配置

### 日常使用

1. **主代理组**选择：`新加坡`（或你常用的地区）
2. **地区策略**选择：`新加坡-自动`
3. Clash 会每 5 分钟自动测速，始终使用最快节点

### 节点不稳定时

1. **地区策略**切换为：`新加坡-故障`
2. 当前节点挂了会立即切换到下一个可用节点

### 需要固定节点时

1. **地区策略**切换为：`新加坡-手动`
2. 手动选择具体的节点

## ⚠️ 故障排查

### 1. 脚本无法访问外网

检查 Clash 是否运行：
```bash
# 测试 Clash 是否可用
curl -x http://127.0.0.1:7890 https://www.google.com
```

检查环境变量：
```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 2. 节点频繁切换

调整 `clash-config-parser.js` 中的 `tolerance` 值：

```javascript
const HEALTH_CHECK = {
  tolerance: 100,  // 从 50 改为 100，减少切换频率
};
```

### 3. Clash 日志查看

```bash
# Clash 日志通常在
tail -f ~/.config/clash/logs/clash.log
```

## 📝 高级配置

### 为不同站点使用不同节点

修改 Clash 规则，针对特定域名使用特定代理组：

```yaml
rules:
  # linux.do 使用新加坡节点
  - DOMAIN-SUFFIX,linux.do,新加坡-自动

  # anyrouter.top 使用香港节点
  - DOMAIN-SUFFIX,anyrouter.top,香港-自动

  # 其他规则
  - RULE-SET,proxy,地区选择
```

### 负载均衡（可选）

如果流量较大，可以添加负载均衡组：

```javascript
// 在 clash-config-parser.js 中添加
const load_balance_group = {
  name: `${region.name}-负载`,
  type: "load-balance",
  strategy: "round-robin",  // 轮询
  proxies: proxy_names,
  url: HEALTH_CHECK.url,
  interval: HEALTH_CHECK.interval,
};
```

## 🔒 安全建议

1. **不要把 Clash 代理暴露到公网**（`allow-lan: false`）
2. **定期更新订阅**，确保节点可用
3. **启用 DNS 防泄漏**：

```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - 223.5.5.5
    - 119.29.29.29
  fallback:
    - 8.8.8.8
    - 1.1.1.1
```

## 📚 相关资源

- [Clash 官方文档](https://github.com/Dreamacro/clash/wiki)
- [Clash Verge 客户端](https://github.com/zzzgydi/clash-verge)
- [Loyalsoldier 规则集](https://github.com/Loyalsoldier/clash-rules)
