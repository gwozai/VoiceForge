# VoiceForge 开发指南

## 🚀 快速开始

### 环境要求
- Python 3.9+
- pip

### 安装运行

```bash
# 克隆项目
git clone https://github.com/gwozai/VoiceForge.git
cd VoiceForge

# 安装依赖
pip install -r requirements.txt

# 运行应用
make run
# 或
python main.py
```

访问：http://localhost:8080

## ⚙️ 环境变量配置

创建 `config/.env` 文件：

```bash
# API配置
API_BASE_URL=http://localhost:8080
DEFAULT_API_KEY=your_api_key_here

# 默认设置
DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
DEFAULT_MODEL=tts-1
DEFAULT_FORMAT=mp3
DEFAULT_SPEED=1.0
DEFAULT_LANGUAGE=zh-CN

# 服务器配置
FLASK_PORT=8080
FLASK_DEBUG=false
```

## 📁 项目结构

```
VoiceForge/
├── main.py              # 主入口
├── src/
│   ├── app.py          # Flask应用
│   ├── controllers/    # 路由控制器
│   ├── services/       # 业务逻辑
│   ├── models/         # 数据模型
│   ├── utils/          # 工具函数
│   └── config/         # 配置文件
├── static/js/          # 前端模块
├── templates/          # HTML模板
└── scripts/            # 部署脚本
```

## 🔧 开发命令

```bash
make help          # 查看所有命令
make run           # 运行应用
make clean         # 清理缓存
make update-voices # 更新语音列表
```

## 🎤 更新语音列表

```bash
make update-voices
# 或
python scripts/update_voices.py
```

语音列表保存在 `src/config/edge_tts_voices.json`
