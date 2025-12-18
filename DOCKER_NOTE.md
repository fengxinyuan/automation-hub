# Docker 支持说明

⚠️ **注意：Docker 支持已暂停维护**

## 为什么不推荐使用 Docker？

本项目当前**不推荐使用 Docker**，原因如下：

### 1. 资源占用大
- Playwright 浏览器需要大量系统依赖
- Docker 镜像体积会超过 1GB
- 容器运行时额外的内存和 CPU 开销

### 2. 部署复杂度高
- 需要配置多个卷挂载（sessions、logs、data、cache）
- 环境变量管理复杂
- Cron 定时任务需要额外配置

### 3. 调试不便
- 需要进入容器查看日志
- 文件修改需要重新构建镜像
- 浏览器 headless 模式问题排查困难

### 4. 当前方案更优
- 本地 Cron + Python 直接运行
- 资源占用少，速度快
- 调试方便，维护简单
- 已稳定运行，无故障

## 推荐方案：Cron 定时任务

详见：[AUTO_RUN_GUIDE.md](AUTO_RUN_GUIDE.md)

## Docker 配置文件

过时的 Docker 配置文件已重命名：
- `Dockerfile.deprecated` - 旧的 Dockerfile（路径已过时）
- `docker-compose.yml.deprecated` - 旧的 Docker Compose 配置

如需使用 Docker，需要：
1. 更新 Dockerfile 以支持新的模块化架构
2. 添加 Cron 支持到容器
3. 配置完整的卷挂载和环境变量
4. 测试 Playwright 在容器中的运行

**建议：如无特殊需求，继续使用 Cron 方案即可。**

---

## 何时需要 Docker？

以下场景可考虑使用 Docker：

1. **多服务器部署** - 需要在多台服务器上快速部署
2. **隔离环境** - 需要完全隔离的运行环境
3. **CI/CD 集成** - 需要在自动化流程中运行
4. **版本管理** - 需要严格控制依赖版本

如有以上需求，请提 Issue 讨论 Docker 支持的实现方案。
