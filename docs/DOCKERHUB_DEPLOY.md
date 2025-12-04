# Docker Hub发布部署指南

## 🎯 适用场景

- 全部测试完成后的正式发布
- 将应用发布到Docker Hub供他人使用
- 版本管理和持续部署
- 生产环境部署

## 📋 前置要求

- 本地开发测试已完成
- Docker本地测试已通过
- Docker Hub账号：`gwozai`
- 网络连接正常（支持代理）

## 🚀 快速发布

### 步骤1：最终测试确认

在发布前，确保所有测试都已通过：

```bash
# 1. 本地功能测试
python main.py
# 访问 http://localhost:8080 测试所有功能

# 2. Docker本地测试
make dev
# 访问 http://localhost:8080 测试容器化应用
make dev-stop

# 3. 构建测试
make build
# 确保镜像构建成功
```

### 步骤2：版本管理

#### 自动版本管理（推荐）

```bash
# 增加补丁版本 (1.0.0 -> 1.0.1)
make bump-patch

# 增加次版本 (1.0.1 -> 1.1.0)
make bump-minor

# 增加主版本 (1.1.0 -> 2.0.0)
make bump-major

# 查看当前版本
make version
```

#### 手动版本管理

```bash
# 设置特定版本
./scripts/version.sh set v2.1.0

# 查看版本
./scripts/version.sh current
```

### 步骤3：更新变更日志

```bash
# 编辑变更日志
nano docs/CHANGELOG.md

# 添加新版本的变更内容，例如：
## v1.0.2 (2025-12-03)

### 🎉 新特性
- 添加了新的语音选项
- 优化了音频生成速度

### 🔧 改进
- 改进了错误处理机制
- 优化了用户界面

### 🐛 修复
- 修复了长文本处理问题
- 修复了数据库连接问题
```

### 步骤4：一键发布

#### 方式1：快速发布（最简单）

```bash
# 一键发布到Docker Hub
make quick-deploy
```

#### 方式2：完整发布流程

```bash
# 完整的构建和发布流程
make deploy
```

#### 方式3：版本+发布一步完成

```bash
# 增加版本号并发布
make release-patch  # 或 release-minor, release-major
```

## 🔧 高级发布选项

### 使用部署脚本的高级功能

#### 仅构建不发布

```bash
# 仅构建镜像，不推送到Docker Hub
./scripts/deploy.sh --build-only
```

#### 构建并测试

```bash
# 构建镜像并进行测试
./scripts/deploy.sh --test
```

#### 指定版本发布

```bash
# 发布特定版本
./scripts/deploy.sh v2.1.0
```

#### 不使用代理发布

```bash
# 如果网络良好，不使用代理
./scripts/deploy.sh --no-proxy
```

#### 发布后清理

```bash
# 发布后清理本地旧镜像
./scripts/deploy.sh --cleanup
```

## 📊 发布过程监控

### 查看发布进度

发布过程中会显示详细的进度信息：

```bash
🚀 开始快速部署...
📦 版本: v1.0.2
🌐 设置代理...
🔨 构建镜像...
[+] Building 45.2s (14/14) FINISHED
📤 推送镜像...
The push refers to repository [docker.io/gwozai/voiceforge]
✅ 部署完成!
🌐 Docker Hub: https://hub.docker.com/r/gwozai/voiceforge
```

### 验证发布结果

```bash
# 1. 检查本地镜像
docker images gwozai/voiceforge

# 2. 测试拉取发布的镜像
docker pull gwozai/voiceforge:latest

# 3. 运行发布的镜像测试
docker run -d --name test-published \
  -p 8081:8080 \
  gwozai/voiceforge:latest

# 4. 测试功能
curl -I http://localhost:8081

# 5. 清理测试容器
docker stop test-published
docker rm test-published
```

## 🌐 Docker Hub管理

### 访问Docker Hub

发布成功后，可以在以下地址查看：
- **仓库地址**: https://hub.docker.com/r/gwozai/voiceforge
- **标签管理**: https://hub.docker.com/r/gwozai/voiceforge/tags

### 镜像标签说明

每次发布会创建两个标签：
- `latest` - 最新版本
- `v1.0.2` - 具体版本号

### 镜像信息

- **仓库名**: `gwozai/voiceforge`
- **大小**: 约480MB
- **架构**: linux/amd64
- **基础镜像**: python:3.9-slim

## 👥 用户使用指南

发布后，其他用户可以这样使用你的镜像：

### 快速启动

```bash
# 拉取并运行最新版本
docker run -d \
  --name voiceforge \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  gwozai/voiceforge:latest
```

### 使用docker-compose

用户可以创建自己的docker-compose.yml：

```yaml
version: '3.8'
services:
  tts-app:
    image: gwozai/voiceforge:latest
    container_name: voiceforge
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - DEFAULT_API_KEY=user_api_key_here
    restart: unless-stopped
```

### 指定版本使用

```bash
# 使用特定版本
docker run -d \
  --name voiceforge \
  -p 8080:8080 \
  gwozai/voiceforge:v1.0.2
```

## 🔄 持续部署流程

### 日常更新流程

```bash
# 1. 完成代码修改
# 2. 本地测试
python main.py

# 3. Docker测试
make dev
make dev-stop

# 4. 更新版本并发布
make release-patch

# 5. 验证发布
docker pull gwozai/voiceforge:latest
```

### 重大版本发布

```bash
# 1. 完成重大功能开发
# 2. 全面测试
# 3. 更新文档
# 4. 发布新的主版本
make release-major

# 5. 创建发布说明
# 在GitHub或其他平台创建Release Notes
```

## 🐛 发布问题排除

### 1. Docker Hub登录问题

```bash
# 重新登录Docker Hub
docker login -u gwozai

# 检查登录状态
docker info | grep Username
```

### 2. 网络连接问题

```bash
# 使用代理发布
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
make quick-deploy

# 或使用脚本的代理功能（默认启用）
./scripts/quick-deploy.sh
```

### 3. 镜像推送失败

```bash
# 查看详细错误信息
docker push gwozai/voiceforge:latest

# 常见解决方案：
# - 检查网络连接
# - 重新登录Docker Hub
# - 检查仓库权限
# - 使用代理
```

### 4. 版本冲突

```bash
# 检查现有版本
docker images gwozai/voiceforge

# 删除本地冲突版本
docker rmi gwozai/voiceforge:v1.0.2

# 重新构建
make build
```

## 📈 发布统计和监控

### 查看下载统计

在Docker Hub页面可以查看：
- 总下载次数
- 版本下载分布
- 下载趋势图

### 监控镜像使用

```bash
# 查看镜像大小趋势
docker images gwozai/voiceforge --format "table {{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# 清理旧版本（可选）
docker rmi gwozai/voiceforge:old-version
```

## 🔒 安全考虑

### 1. 敏感信息处理

```bash
# 确保不包含敏感信息
grep -r "password\|secret\|key" . --exclude-dir=.git

# 检查环境变量文件不在镜像中
docker run --rm gwozai/voiceforge:latest ls -la /app/config/
```

### 2. 镜像安全扫描

```bash
# 使用Docker Scout扫描（如果可用）
docker scout cves gwozai/voiceforge:latest

# 或使用其他安全扫描工具
```

### 3. 最小权限原则

镜像已配置为使用非root用户运行，提高安全性。

## 📋 发布检查清单

### 发布前检查
- [ ] 本地开发测试通过
- [ ] Docker本地测试通过
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] 敏感信息已清理

### 发布过程检查
- [ ] 镜像构建成功
- [ ] 镜像推送成功
- [ ] 标签创建正确
- [ ] 发布日志无错误

### 发布后验证
- [ ] Docker Hub页面显示新版本
- [ ] 可以正常拉取新镜像
- [ ] 新镜像功能正常
- [ ] 文档链接正确

## 🎯 发布最佳实践

1. **测试优先**：发布前充分测试
2. **版本管理**：使用语义化版本号
3. **文档同步**：及时更新文档
4. **渐进发布**：先发布测试版本
5. **监控反馈**：关注用户反馈和问题

## 🔗 相关文档

- [本地开发测试指南](LOCAL_DEVELOPMENT.md)
- [Docker本地测试指南](DOCKER_LOCAL_TEST.md)
- [部署脚本详细说明](DEPLOY_SCRIPTS.md)
- [版本管理指南](VERSION_MANAGEMENT.md)
