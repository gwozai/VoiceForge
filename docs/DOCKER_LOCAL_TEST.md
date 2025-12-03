# Docker本地测试指南

## 🎯 适用场景

- 项目完成后的容器化测试
- 模拟生产环境运行
- 验证Docker配置正确性
- 测试部署前的最终验证

## 📋 前置要求

- Docker Desktop 已安装并运行
- 项目代码已完成本地测试
- 网络连接正常（用于拉取基础镜像）

## 🚀 快速开始

### 步骤1：环境检查

```bash
# 1. 检查Docker状态
docker --version
docker info

# 2. 确保Docker服务运行
# 启动Docker Desktop应用

# 3. 检查项目结构
ls -la
# 应该看到：docker/ scripts/ src/ config/ 等目录
```

### 步骤2：配置环境变量

```bash
# 1. 确保环境变量文件存在
ls -la config/.env

# 2. 如果不存在，复制模板
cp .env.example config/.env

# 3. 编辑Docker环境配置
nano config/.env
```

Docker环境推荐配置：

```bash
# TTS API配置
API_BASE_URL=http://117.72.56.34:5050
DEFAULT_API_KEY=your_api_key_here

# Flask生产配置
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# 容器内路径
DB_PATH=/app/data/tts_stats.db
LOG_LEVEL=INFO
LOG_FILE=/app/logs/tts_generation.log
```

### 步骤3：构建Docker镜像

#### 方式1：使用Make命令（推荐）

```bash
# 仅构建镜像
make build

# 构建并测试
make test
```

#### 方式2：使用脚本

```bash
# 仅构建，不推送
./scripts/deploy.sh --build-only

# 构建并测试
./scripts/deploy.sh --test
```

#### 方式3：直接使用Docker命令

```bash
# 构建镜像
docker build -f docker/Dockerfile -t tts-website-test .

# 查看构建的镜像
docker images tts-website-test
```

### 步骤4：启动Docker容器

#### 方式1：使用Docker Compose（推荐）

```bash
# 启动开发环境
make dev

# 或直接使用docker-compose
cd docker
docker-compose up -d
```

#### 方式2：直接运行容器

```bash
# 创建数据和日志目录
mkdir -p data logs

# 运行容器
docker run -d \
  --name tts-website-test \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file config/.env \
  tts-website-test
```

### 步骤5：验证容器运行

```bash
# 1. 检查容器状态
docker ps

# 2. 查看容器日志
docker logs tts-website-test

# 3. 检查健康状态
docker inspect tts-website-test | grep -A 5 "Health"
```

## 🧪 功能测试

### 1. 基础连接测试

```bash
# 测试应用是否响应
curl -I http://localhost:8080

# 应该返回 HTTP/1.1 200 OK
```

### 2. 页面加载测试

```bash
# 访问主页
curl -s http://localhost:8080/ | head -10

# 或在浏览器中打开
open http://localhost:8080  # Mac
# 或 start http://localhost:8080  # Windows
```

### 3. API功能测试

```bash
# 测试API连接
curl -X POST "http://localhost:8080/api/test_connection" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"test"}'

# 测试语音列表
curl -X GET "http://localhost:8080/api/voices"

# 测试模型列表
curl -X GET "http://localhost:8080/api/models"
```

### 4. TTS生成测试

```bash
# 测试语音生成（小文本）
curl -X POST "http://localhost:8080/api/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你好，这是Docker测试",
    "voice": "zh-CN-XiaoxiaoNeural",
    "response_format": "mp3"
  }' \
  --output test_audio.mp3

# 检查生成的音频文件
ls -la test_audio.mp3
```

## 📊 监控和调试

### 查看容器日志

```bash
# 实时查看日志
docker logs -f tts-website-test

# 查看最近的日志
docker logs --tail 50 tts-website-test

# 查看特定时间的日志
docker logs --since "2024-01-01T00:00:00" tts-website-test
```

### 进入容器调试

```bash
# 进入容器
docker exec -it tts-website-test bash

# 在容器内检查
ls -la /app
cat /app/data/tts_stats.db
tail /app/logs/tts_generation.log
exit
```

### 检查资源使用

```bash
# 查看容器资源使用
docker stats tts-website-test

# 查看容器详细信息
docker inspect tts-website-test
```

## 🔧 高级测试

### 1. 压力测试

```bash
# 使用ab工具进行压力测试（需要安装apache2-utils）
ab -n 100 -c 10 http://localhost:8080/

# 或使用curl进行并发测试
for i in {1..10}; do
  curl -X POST "http://localhost:8080/api/speech" \
    -H "Content-Type: application/json" \
    -d '{"input":"测试'$i'","voice":"zh-CN-XiaoxiaoNeural"}' &
done
wait
```

### 2. 数据持久化测试

```bash
# 1. 生成一些数据
curl -X POST "http://localhost:8080/api/speech" \
  -H "Content-Type: application/json" \
  -d '{"input":"持久化测试","voice":"zh-CN-XiaoxiaoNeural"}'

# 2. 重启容器
docker restart tts-website-test

# 3. 检查数据是否保持
curl -X GET "http://localhost:8080/api/stats"
```

### 3. 网络测试

```bash
# 测试容器网络连接
docker exec tts-website-test ping -c 3 google.com

# 测试API连接
docker exec tts-website-test curl -I http://117.72.56.34:5050
```

## 🐛 常见问题排除

### 1. 容器启动失败

```bash
# 查看详细错误信息
docker logs tts-website-test

# 常见原因和解决方案：
# - 端口被占用：更改端口映射 -p 8081:8080
# - 环境变量错误：检查 config/.env 文件
# - 权限问题：检查目录权限 chmod 755 data logs
```

### 2. 镜像构建失败

```bash
# 查看构建日志
docker build -f docker/Dockerfile -t tts-website-test . --no-cache

# 常见原因：
# - 网络问题：使用代理或更换网络
# - Dockerfile路径错误：确保在项目根目录执行
# - 依赖安装失败：检查requirements.txt
```

### 3. 应用无法访问

```bash
# 检查端口映射
docker port tts-website-test

# 检查防火墙设置
# Mac: 系统偏好设置 -> 安全性与隐私 -> 防火墙
# Windows: Windows Defender 防火墙

# 检查容器内应用状态
docker exec tts-website-test ps aux | grep python
```

### 4. 数据不持久化

```bash
# 检查卷挂载
docker inspect tts-website-test | grep -A 10 "Mounts"

# 确保目录存在且有正确权限
ls -la data/ logs/
chmod 755 data logs
```

## 📋 测试检查清单

### 构建阶段
- [ ] Docker镜像构建成功
- [ ] 镜像大小合理（<500MB）
- [ ] 构建过程无错误

### 启动阶段
- [ ] 容器启动成功
- [ ] 应用进程正常运行
- [ ] 端口映射正确
- [ ] 环境变量加载正确

### 功能测试
- [ ] 主页面正常加载
- [ ] API接口响应正常
- [ ] TTS功能正常工作
- [ ] 数据库读写正常
- [ ] 日志记录正常

### 性能测试
- [ ] 响应时间合理（<2秒）
- [ ] 内存使用正常（<512MB）
- [ ] CPU使用正常
- [ ] 并发处理正常

### 持久化测试
- [ ] 数据库数据持久化
- [ ] 日志文件持久化
- [ ] 容器重启后数据保持

## 🔄 测试完成后清理

```bash
# 停止并删除容器
docker stop tts-website-test
docker rm tts-website-test

# 或使用docker-compose
make dev-stop

# 清理测试镜像（可选）
docker rmi tts-website-test

# 清理测试文件
rm -f test_audio.mp3
```

## 📈 性能基准

### 正常指标
- **启动时间**: < 5秒
- **内存使用**: < 512MB
- **响应时间**: < 2秒
- **TTS生成**: < 10秒（短文本）

### 异常指标
- 启动时间 > 30秒
- 内存使用 > 1GB
- 响应时间 > 5秒
- 频繁重启或崩溃

## 🎯 测试最佳实践

1. **逐步测试**：先基础功能，再高级功能
2. **保留日志**：测试过程中保存日志用于分析
3. **模拟真实环境**：使用生产环境配置
4. **压力测试**：验证系统稳定性
5. **清理资源**：测试完成后及时清理

## 🔗 相关文档

- [本地开发测试指南](LOCAL_DEVELOPMENT.md)
- [Docker Hub发布指南](DOCKERHUB_DEPLOY.md)
- [环境变量配置](ENV_CONFIG.md)
- [部署脚本指南](DEPLOY_SCRIPTS.md)
