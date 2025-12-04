# 更新日志

## v1.0.2 (2025-12-03)

### 🎉 新特性
- 

### 🔧 改进
- 

### 🐛 修复
- 

### 📁 文件变更
- 

## v1.0.1 (2025-12-03)

### 🎉 新特性
- 

### 🔧 改进
- 

### 🐛 修复
- 

### 📁 文件变更
- 

## v2.0 (2025-12-03)

### 🎉 新特性
- **环境变量配置**: 重构项目使用环境变量管理所有配置
- **Docker Hub镜像**: 更新镜像到v2.0版本
- **生产环境优化**: 改进生产环境配置管理

### 🔧 改进
- 添加`.env`文件支持，提高配置灵活性
- 更新`docker-compose.yml`支持环境变量文件
- 改进健康检查配置，使用Python内置urllib
- 添加详细的环境变量配置文档

### 📁 新增文件
- `.env.example` - 环境变量模板文件
- `.env` - 实际环境变量配置文件
- `ENV_CONFIG.md` - 环境变量配置说明文档
- `CHANGELOG.md` - 版本更新日志

### 🔄 修改文件
- `app.py` - 添加环境变量加载和使用
- `requirements.txt` - 添加python-dotenv依赖
- `docker-compose.yml` - 支持环境变量文件
- `.dockerignore` - 排除环境变量文件
- `DOCKER_README.md` - 更新部署说明

### 🎯 环境变量支持
- `API_BASE_URL` - TTS API服务器地址
- `DEFAULT_API_KEY` - 默认API密钥
- `DEFAULT_MODEL` - 默认TTS模型
- `DEFAULT_VOICE` - 默认语音
- `FLASK_ENV` - Flask运行环境
- `FLASK_DEBUG` - 调试模式
- `FLASK_HOST` - 监听地址
- `FLASK_PORT` - 监听端口
- `DB_PATH` - 数据库文件路径
- `LOG_LEVEL` - 日志级别
- `LOG_FILE` - 日志文件路径

### 🚀 Docker Hub镜像
- **镜像ID**: `68aabee9696f`
- **标签**: `gwozai/voiceforge:v2.0`, `gwozai/voiceforge:latest`
- **大小**: 约67MB

## v1.0 (2025-12-03)

### 🎉 初始版本
- 基础TTS网站功能
- Docker容器化部署
- SQLite数据库支持
- 多语音支持
- 流式音频生成
- 统计数据功能

### 📦 Docker Hub镜像
- **镜像ID**: `6249de6c27b3`
- **标签**: `gwozai/voiceforge:v1.0`
