# VoiceForge 架构设计

## 📁 项目结构

```
VoiceForge/
├── app.py                      # 主应用入口（保持向后兼容）
├── main.py                     # 新的主应用入口
├── requirements.txt            # 依赖管理
├── config/                     # 配置文件
│   ├── .env                   # 环境变量
│   └── deploy.config          # 部署配置
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── app.py                 # Flask应用工厂
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py           # 基础模型类
│   │   ├── tts_request.py    # TTS请求模型
│   │   ├── voice.py          # 语音模型
│   │   └── history.py        # 历史记录模型
│   ├── services/              # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── tts_service.py    # TTS核心服务
│   │   ├── voice_service.py  # 语音管理服务
│   │   ├── file_service.py   # 文件处理服务
│   │   └── history_service.py # 历史记录服务
│   ├── controllers/           # 控制器（路由处理）
│   │   ├── __init__.py
│   │   ├── main_controller.py # 主页控制器
│   │   ├── api_controller.py  # API控制器
│   │   └── voice_controller.py # 语音相关控制器
│   ├── utils/                 # 工具类
│   │   ├── __init__.py
│   │   ├── database.py       # 数据库工具
│   │   ├── logger.py         # 日志工具
│   │   ├── validators.py     # 验证工具
│   │   └── helpers.py        # 辅助函数
│   └── config/               # 配置管理
│       ├── __init__.py
│       ├── settings.py       # 配置类
│       └── constants.py      # 常量定义
├── static/                    # 静态资源
│   ├── js/                   # JavaScript模块
│   │   ├── main.js          # 主模块
│   │   ├── modules/         # 功能模块
│   │   │   ├── audio-manager.js
│   │   │   ├── tts-client.js
│   │   │   ├── ui-manager.js
│   │   │   └── notification.js
│   │   └── utils/           # 工具模块
│   │       ├── api.js
│   │       ├── storage.js
│   │       └── validators.js
│   ├── css/                 # 样式文件
│   │   ├── main.css
│   │   └── components/
│   └── images/              # 图片资源
├── templates/               # 模板文件
│   ├── base.html           # 基础模板
│   ├── index.html          # 主页模板
│   └── components/         # 组件模板
└── tests/                  # 测试文件
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_controllers.py
```

## 🏛️ 架构设计原则

### 1. 分层架构
- **表现层**: Controllers + Templates
- **业务逻辑层**: Services
- **数据访问层**: Models + Utils
- **配置层**: Config

### 2. 面向对象设计
- 每个功能模块都有对应的类
- 使用继承和多态提高代码复用
- 依赖注入提高可测试性

### 3. 模块化设计
- 前端JavaScript模块化
- 后端功能模块化
- 配置和常量集中管理

### 4. 设计模式应用
- **工厂模式**: Flask应用创建
- **单例模式**: 数据库连接、配置管理
- **策略模式**: 不同TTS引擎支持
- **观察者模式**: 事件通知系统

## 🔧 核心类设计

### TTSService (TTS核心服务)
```python
class TTSService:
    def __init__(self, config, db_service, voice_service)
    def generate_speech(self, request: TTSRequest) -> TTSResponse
    def generate_streaming_speech(self, request: TTSRequest) -> Iterator
    def validate_request(self, request: TTSRequest) -> bool
```

### VoiceService (语音管理服务)
```python
class VoiceService:
    def get_available_voices(self) -> List[Voice]
    def get_voice_by_id(self, voice_id: str) -> Voice
    def preview_voice(self, voice_id: str, text: str) -> bytes
```

### AudioManager (前端音频管理器)
```javascript
class AudioManager {
    constructor()
    createPlayer(container, options)
    cleanupAllPlayers()
    registerPlayer(player)
}
```

## 🚀 重构计划

1. **阶段1**: 创建基础架构和配置管理
2. **阶段2**: 重构后端为面向对象
3. **阶段3**: 重构前端为模块化
4. **阶段4**: 添加测试和文档
5. **阶段5**: 性能优化和部署
