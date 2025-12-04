# 本地开发环境启动测试指南

## 🎯 适用场景

- 项目代码修改后的本地测试
- 功能开发和调试
- 快速验证代码更改

## 📋 前置要求

- Python 3.9+
- Conda（推荐）或 pip
- Git（可选）

## 🚀 快速开始

### 步骤1：环境准备

#### 方式1：使用Conda（推荐）

```bash
# 1. 创建conda环境
conda create -n tts-env python=3.9 -y

# 2. 激活环境
conda activate tts-env

# 3. 验证Python版本
python --version  # 应该显示 Python 3.9.x
```

#### 方式2：使用系统Python

```bash
# 1. 检查Python版本
python3 --version  # 确保是3.9+

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv tts-venv
source tts-venv/bin/activate  # Linux/Mac
# 或 tts-venv\Scripts\activate  # Windows
```

### 步骤2：项目设置

```bash
# 1. 进入项目目录
cd tts的单页网站

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example config/.env

# 4. 编辑配置文件（重要！）
nano config/.env  # 或使用你喜欢的编辑器
```

### 步骤3：配置环境变量

编辑 `config/.env` 文件，设置以下关键配置：

```bash
# TTS API配置
API_BASE_URL=http://117.72.56.34:5050
DEFAULT_API_KEY=your_api_key_here

# Flask开发配置
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# 数据库和日志
DB_PATH=tts_stats.db
LOG_LEVEL=DEBUG
LOG_FILE=tts_generation.log
```

### 步骤4：启动应用

```bash
# 方式1：直接运行
python main.py

# 方式2：使用Make命令
make run

# 启动成功后会看到类似输出：
# * Serving Flask app 'app'
# * Debug mode: on
# * Running on http://0.0.0.0:8080
```

### 步骤5：验证功能

1. **访问应用**
   ```
   浏览器打开：http://localhost:8080
   ```

2. **检查基本功能**
   - 页面是否正常加载
   - 语音选择是否可用
   - 文本输入框是否正常

3. **测试TTS功能**
   - 输入测试文本："你好，这是一个测试"
   - 选择语音：zh-CN-XiaoxiaoNeural
   - 点击生成按钮
   - 检查是否能正常生成音频

## 🔧 开发调试

### 查看日志

```bash
# 实时查看日志
tail -f tts_generation.log

# 查看最近的日志
tail -20 tts_generation.log
```

### 数据库检查

```bash
# 检查数据库文件
ls -la tts_stats.db

# 使用SQLite命令行工具查看数据（可选）
sqlite3 tts_stats.db
.tables
SELECT * FROM generation_logs LIMIT 5;
.quit
```

### 重启应用

```bash
# 停止应用：Ctrl+C
# 重新启动：
python main.py
```

## 🐛 常见问题排除

### 1. 端口被占用

```bash
# 查看端口占用
lsof -i :8080

# 解决方案1：杀死占用进程
kill -9 <PID>

# 解决方案2：更改端口
# 在 config/.env 中修改：
FLASK_PORT=8081
```

### 2. 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### 3. 环境变量未生效

```bash
# 检查文件是否存在
ls -la config/.env

# 检查文件内容
cat config/.env

# 确保没有语法错误，格式为：
# KEY=value（等号两边不要有空格）
```

### 4. 模板文件找不到

```bash
# 检查模板文件是否存在
ls -la src/templates/index.html

# 如果文件不存在，检查项目结构是否正确
```

### 5. API连接失败

```bash
# 测试API连接
curl -X POST "http://localhost:8080/api/test_connection" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"test"}'

# 检查API配置
echo "API_BASE_URL: $API_BASE_URL"
```

## 📝 开发工作流程

### 日常开发流程

```bash
# 1. 激活环境
conda activate tts-env

# 2. 拉取最新代码（如果使用Git）
git pull origin main

# 3. 启动应用
python main.py

# 4. 进行开发...
# 5. 测试功能
# 6. 提交代码（如果使用Git）
git add .
git commit -m "描述你的更改"
```

### 功能测试检查清单

- [ ] 应用正常启动，无错误日志
- [ ] 主页面正常加载
- [ ] 语音选择功能正常
- [ ] TTS生成功能正常
- [ ] 音频播放功能正常
- [ ] 历史记录功能正常
- [ ] 统计功能正常
- [ ] 数据库正常写入

## 🔄 代码修改后的测试流程

### 1. 前端修改测试

```bash
# 修改 src/templates/index.html 后
# 刷新浏览器页面即可看到更改
```

### 2. 后端修改测试

```bash
# 修改 app.py 后需要重启应用
# Ctrl+C 停止应用
python main.py  # 重新启动
```

### 3. 配置修改测试

```bash
# 修改 config/.env 后需要重启应用
# Ctrl+C 停止应用
python main.py  # 重新启动
```

### 4. 依赖修改测试

```bash
# 修改 requirements.txt 后
pip install -r requirements.txt
python main.py  # 重新启动
```

## 📊 性能监控

### 监控应用状态

```bash
# 查看进程
ps aux | grep python

# 查看端口监听
netstat -an | grep 8080

# 查看内存使用
top -p $(pgrep -f "python main.py")
```

### 日志分析

```bash
# 查看错误日志
grep -i error tts_generation.log

# 查看最近的生成记录
grep -i "生成" tts_generation.log | tail -10

# 统计请求数量
grep -c "POST /api/speech" tts_generation.log
```

## 🎯 开发最佳实践

1. **使用Conda环境**：避免依赖冲突
2. **开启调试模式**：便于问题排查
3. **实时查看日志**：及时发现问题
4. **定期备份数据**：避免数据丢失
5. **版本控制**：使用Git管理代码变更

## 🔗 相关文档

- [Docker本地测试指南](DOCKER_LOCAL_TEST.md)
- [Docker Hub发布指南](DOCKERHUB_DEPLOY.md)
- [环境变量配置](ENV_CONFIG.md)
- [故障排除指南](TROUBLESHOOTING.md)
