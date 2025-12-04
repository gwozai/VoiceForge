# VoiceForge 2.0

🎙️ 专业的语音合成工坊 - 基于Edge-TTS的OpenAI兼容TTS API，支持10万字长文本、流式生成和多语言语音。

## 🎯 主要特性

- 🎤 **多语音支持** - 594种语音，支持中英日韩法德等多语言
- 🚀 **长文本支持** - 支持10万字长文本的流式音频生成
- 📡 **OpenAI兼容** - 兼容OpenAI TTS API接口
- 🔄 **流式传输** - 边生成边播放，无需等待
- 🐳 **Docker部署** - 完整的容器化部署方案
- 📁 **文件上传** - 支持txt/md/srt文件和URL获取

## 🚀 快速开始

### 使用Docker（推荐）

```bash
# 拉取镜像
docker pull gwozai/voiceforge:latest

# 运行容器
docker run -d \
  --name voiceforge \
  -p 8080:8080 \
  gwozai/voiceforge:latest

# 或使用docker-compose
docker-compose up -d
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
make run
# 或
python main.py
```

访问地址：http://localhost:8080

## ⚡ 快速部署到Docker Hub

项目提供了自动化部署脚本，让你能够快速将更新推送到Docker Hub：

```bash
# 最简单的方式
make quick-deploy

# 或者使用脚本
./scripts/quick-deploy.sh

# 指定版本号
make deploy VERSION=v2.1.0
```

详细使用说明请参考 [部署脚本指南](docs/DEPLOY_SCRIPTS.md)。

## 📚 文档

### 🚀 核心文档（按流程顺序）
1. [**本地开发测试**](docs/LOCAL_DEVELOPMENT.md) - 项目修改完成后的本地启动测试
2. [**Docker本地测试**](docs/DOCKER_LOCAL_TEST.md) - 项目完成后的Docker可运行测试
3. [**Docker Hub发布**](docs/DOCKERHUB_DEPLOY.md) - 全部测试好后上传Docker Hub

### 🔧 配置文档
- [部署脚本指南](docs/DEPLOY_SCRIPTS.md) - 自动化部署脚本使用说明
- [环境变量配置](docs/ENV_CONFIG.md) - 详细的配置说明
- [Git操作指南](docs/GIT_OPERATIONS.md) - Git推送和版本管理指南
- [更新日志](docs/CHANGELOG.md) - 版本更新记录

### 📋 完整导航
- [**文档目录**](docs/README.md) - 查看所有文档和使用指南

## 🛠️ 技术栈

- **后端**: Flask + Python 3.11
- **TTS引擎**: Edge-TTS
- **前端**: HTML5 + Bootstrap 5 + ES6 Modules
- **容器化**: Docker + Docker Compose
- **生产服务器**: Gunicorn

## 🎵 支持的语音

### 中文语音
- zh-CN-XiaoxiaoNeural (默认)
- zh-CN-YunxiNeural
- zh-CN-YunjianNeural
- 等多种中文语音...

### 英文语音
- en-US-AvaNeural
- en-US-BrianNeural
- en-US-ChristopherNeural
- 等多种英文语音...

### 其他语言
- 日语、韩语、法语、德语、西班牙语等

## 📊 功能特性

- ✅ 文本转语音生成
- ✅ 多种音频格式支持 (MP3, WAV, FLAC等)
- ✅ 语速调节
- ✅ 流式音频生成
- ✅ 生成历史记录
- ✅ 统计数据导出
- ✅ API接口支持

## 🔧 配置

项目支持通过环境变量进行配置，主要配置项包括：

- `API_BASE_URL` - TTS API服务器地址
- `DEFAULT_API_KEY` - 默认API密钥
- `DEFAULT_VOICE` - 默认语音
- `FLASK_PORT` - 服务端口
- `DB_PATH` - 数据库路径

详细配置说明请参考 [环境变量配置文档](doc/ENV_CONFIG.md)。

## 🐳 Docker Hub

**镜像仓库**: `gwozai/voiceforge`

```bash
# 拉取最新版本
docker pull gwozai/voiceforge:latest

# 使用docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📦 Make命令

```bash
make help          # 查看所有命令
make run           # 本地运行
make docker-build  # 构建Docker镜像
make docker-run    # 启动Docker容器
make docker-stop   # 停止Docker容器
make update-voices # 更新语音列表
```

## 📝 许可证

本项目采用 GPL-3.0 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！
