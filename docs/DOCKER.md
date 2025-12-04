# VoiceForge Docker 部署指南

## 🚀 快速部署

### 使用 Docker Hub 镜像

```bash
# 拉取镜像
docker pull gwozai/voiceforge:latest

# 运行容器
docker run -d \
  --name voiceforge \
  -p 8080:8080 \
  gwozai/voiceforge:latest
```

### 使用 Docker Compose

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看日志
docker-compose logs -f
```

访问：http://localhost:8080

## 🔨 本地构建

### 构建镜像

```bash
# 使用 Makefile
make docker-build

# 或直接构建
docker build -t voiceforge:latest .
```

### 运行测试

```bash
# 启动容器
make docker-run

# 停止容器
make docker-stop
```

## 📤 发布到 Docker Hub

### 自动部署

```bash
# 完整部署流程
./scripts/deploy.sh

# 指定版本
./scripts/deploy.sh v2.1.0

# 仅构建不推送
./scripts/deploy.sh --build-only
```

### 手动发布

```bash
# 登录 Docker Hub
docker login -u gwozai

# 标记镜像
docker tag voiceforge:latest gwozai/voiceforge:latest
docker tag voiceforge:latest gwozai/voiceforge:v2.0.0

# 推送镜像
docker push gwozai/voiceforge:latest
docker push gwozai/voiceforge:v2.0.0
```

## ⚙️ 环境变量

Docker 容器支持以下环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| FLASK_ENV | production | 运行环境 |
| TZ | Asia/Shanghai | 时区 |
| API_BASE_URL | http://localhost:8080 | API地址 |
| DEFAULT_VOICE | zh-CN-XiaoxiaoNeural | 默认语音 |

示例：
```bash
docker run -d \
  --name voiceforge \
  -p 8080:8080 \
  -e DEFAULT_VOICE=en-US-AvaNeural \
  gwozai/voiceforge:latest
```

## 📦 Docker Compose 配置

```yaml
version: '3.8'
services:
  voiceforge:
    image: gwozai/voiceforge:latest
    container_name: voiceforge
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

## 🔍 常见问题

### 容器启动失败
```bash
# 查看日志
docker logs voiceforge

# 检查端口占用
lsof -i :8080
```

### 网络问题（国内用户）
```bash
# 使用代理构建
export https_proxy="http://127.0.0.1:7897"
docker build -t voiceforge:latest .
```
