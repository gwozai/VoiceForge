# 文档目录

本目录包含TTS语音合成网站的核心技术文档。

## 📚 核心文档（按使用流程）

### 🚀 部署流程文档
1. [**LOCAL_DEVELOPMENT.md**](LOCAL_DEVELOPMENT.md) - 本地开发测试
   - 项目修改完成后的本地启动测试
   - Conda环境设置和项目配置

2. [**DOCKER_LOCAL_TEST.md**](DOCKER_LOCAL_TEST.md) - Docker本地测试
   - 项目完成后的Docker可运行测试
   - 容器化测试和验证

3. [**DOCKERHUB_DEPLOY.md**](DOCKERHUB_DEPLOY.md) - Docker Hub发布
   - 全部测试好后上传Docker Hub
   - 版本管理和一键发布

### 🔧 技术配置文档
- [**DEPLOY_SCRIPTS.md**](DEPLOY_SCRIPTS.md) - 自动化部署脚本使用说明
- [**ENV_CONFIG.md**](ENV_CONFIG.md) - 环境变量配置详解

### 📋 项目信息
- [**CHANGELOG.md**](CHANGELOG.md) - 版本更新日志

## 🚀 使用指南

### 开发者工作流程
```bash
# 1. 本地开发测试
conda activate tts-env
python app.py

# 2. Docker本地测试  
make build && make dev

# 3. 发布到Docker Hub
make quick-deploy
```

### 快速查找
- **开发问题**: 查看 LOCAL_DEVELOPMENT.md
- **Docker问题**: 查看 DOCKER_LOCAL_TEST.md  
- **发布问题**: 查看 DOCKERHUB_DEPLOY.md
- **脚本问题**: 查看 DEPLOY_SCRIPTS.md
- **配置问题**: 查看 ENV_CONFIG.md
