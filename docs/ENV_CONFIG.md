# 环境变量配置说明

## 概述

项目已经重构为使用环境变量管理配置，提高了安全性和灵活性。

## 环境变量文件

### `.env.example`
模板文件，包含所有可配置的环境变量及其默认值。

### `.env`
实际的环境变量文件，从`.env.example`复制而来，可以根据需要修改配置。

**注意**: `.env`文件已被添加到`.gitignore`中，不会被提交到版本控制系统。

## 配置变量说明

### API配置
```bash
# TTS API服务器地址
API_BASE_URL=http://117.72.56.34:5050

# API端点路径
API_ENDPOINT=/v1/audio/speech
VOICES_ENDPOINT=/voices
MODELS_ENDPOINT=/models
```

### 默认TTS设置
```bash
# 默认API密钥
DEFAULT_API_KEY=your_api_key_here

# 默认TTS模型
DEFAULT_MODEL=tts-1

# 默认语音
DEFAULT_VOICE=zh-CN-XiaoxiaoNeural

# 默认音频格式
DEFAULT_FORMAT=mp3

# 默认语速
DEFAULT_SPEED=1.0

# 默认语言
DEFAULT_LANGUAGE=zh-CN
```

### 数据库配置
```bash
# 数据库文件路径
DB_PATH=tts_stats.db
```

### Flask应用配置
```bash
# Flask运行环境
FLASK_ENV=production

# 调试模式
FLASK_DEBUG=False

# 监听地址
FLASK_HOST=0.0.0.0

# 监听端口
FLASK_PORT=8080
```

### 日志配置
```bash
# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=tts_generation.log
```

## 使用方式

### 1. 本地开发

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，修改配置
nano .env

# 启动应用
python main.py
```

### 2. Docker部署

```bash
# 确保.env文件存在
cp .env.example .env

# 编辑.env文件
nano .env

# 使用docker-compose启动
docker-compose up -d
```

### 3. 生产环境

在生产环境中，建议：

1. **设置安全的API密钥**
```bash
DEFAULT_API_KEY=your_secure_api_key_here
```

2. **关闭调试模式**
```bash
FLASK_DEBUG=False
FLASK_ENV=production
```

3. **设置适当的日志级别**
```bash
LOG_LEVEL=WARNING
```

4. **使用绝对路径**
```bash
DB_PATH=/app/data/tts_stats.db
LOG_FILE=/app/logs/tts_generation.log
```

## 安全注意事项

1. **不要提交.env文件到版本控制系统**
2. **定期更换API密钥**
3. **在生产环境中使用强密码和安全配置**
4. **限制数据库文件的访问权限**

## 环境变量优先级

1. Docker环境变量（最高优先级）
2. `.env`文件中的变量
3. 代码中的默认值（最低优先级）

## 故障排除

### 环境变量未生效
检查`.env`文件是否存在且格式正确：
```bash
# 检查文件是否存在
ls -la .env

# 检查文件内容
cat .env
```

### 应用启动失败
检查日志文件中的错误信息：
```bash
tail -f tts_generation.log
```
