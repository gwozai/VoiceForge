# VoiceForge 文档

## 📚 文档列表

| 文档 | 说明 |
|------|------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | 本地开发指南 |
| [DOCKER.md](DOCKER.md) | Docker部署指南 |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新日志 |

## 🚀 快速开始

### 本地开发
```bash
pip install -r requirements.txt
make run
```

### Docker部署
```bash
docker pull gwozai/voiceforge:latest
docker run -d -p 8080:8080 gwozai/voiceforge:latest
```

访问：http://localhost:8080
