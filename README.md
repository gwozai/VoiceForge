# VoiceForge

🎙️ 专业的语音合成工坊 - 基于Flask的文字转语音(TTS)平台，支持多种语音选择和自定义配置，提供流式音频生成功能。

## 🎯 主要特性

- 🎤 **多语音支持** - 支持中文、英文、日文等多种语言语音
- 🚀 **流式生成** - 支持长文本的流式音频生成
- 📊 **统计功能** - 详细的生成统计和历史记录
- 🐳 **Docker部署** - 完整的容器化部署方案
- ⚙️ **环境变量配置** - 灵活的配置管理
- 🔒 **生产就绪** - 适合生产环境的安全配置

## 🚀 快速开始

### 使用Docker Hub镜像（推荐）

```bash
# 拉取镜像
docker pull gwozai/tts-website:latest

# 运行容器
docker run -d \
  --name tts-website \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  gwozai/tts-website:latest
```

### 本地开发

#### 方式1：使用Conda环境（推荐）

```bash
# 创建conda环境
conda create -n tts-env python=3.9 -y
conda activate tts-env

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example config/.env
# 编辑config/.env文件设置你的配置

# 启动应用
python app.py
```

#### 方式2：使用系统Python

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example config/.env
# 编辑config/.env文件设置你的配置

# 启动应用
python app.py
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
- [更新日志](docs/CHANGELOG.md) - 版本更新记录

### 📋 完整导航
- [**文档目录**](docs/README.md) - 查看所有文档和使用指南

## 🛠️ 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite
- **前端**: HTML5 + Bootstrap + JavaScript
- **容器化**: Docker + Docker Compose
- **配置管理**: python-dotenv

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

**镜像仓库**: `gwozai/tts-website`

- `latest` - 最新版本（v2.0）
- `v2.0` - 环境变量配置版本（推荐）
- `v1.0` - 初始版本

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如果你在使用过程中遇到问题，请查看文档或提交Issue。
