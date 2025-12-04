# VoiceForge 2.0 - 面向对象重构版本

## 🎯 重构目标

将VoiceForge从单体应用重构为面向对象、模块化的现代架构，提升代码的可维护性、可扩展性和可测试性。

## 🏗️ 架构特点

### 后端架构
- **分层架构**: Controllers → Services → Models → Utils
- **依赖注入**: 通过配置管理实现松耦合
- **单例模式**: 数据库管理器、配置管理器
- **工厂模式**: Flask应用创建
- **蓝图模式**: 路由模块化管理

### 前端架构
- **ES6模块化**: 使用import/export语法
- **面向对象**: 每个功能都有对应的类
- **事件驱动**: 统一的事件管理机制
- **组件化**: 可复用的UI组件

## 📁 目录结构

```
VoiceForge/
├── main.py                     # 新的主入口（面向对象版本）
├── app.py                      # 旧的入口（保持兼容）
├── src/                        # 源代码
│   ├── app.py                 # Flask应用工厂
│   ├── config/                # 配置管理
│   ├── models/                # 数据模型
│   ├── services/              # 业务逻辑
│   ├── controllers/           # 控制器
│   └── utils/                 # 工具类
├── static/js/                  # 前端模块
│   ├── main.js               # 主应用类
│   └── modules/              # 功能模块
└── templates/                  # 模板文件
```

## 🚀 使用方法

### 启动面向对象版本
```bash
# 使用新的主入口
python main.py

# 或者设置环境变量
export FLASK_ENV=development
python main.py
```

### 启动原版本（兼容性）
```bash
# 使用原来的入口
python app.py
```

## 🔧 核心类介绍

### 后端核心类

#### 1. Config (配置管理)
```python
from src.config.settings import get_config

config = get_config('development')
api_key = config.get('DEFAULT_API_KEY')
```

#### 2. DatabaseManager (数据库管理)
```python
from src.utils.database import DatabaseManager

db = DatabaseManager(config)
db.log_generation(text_length=100, voice='zh-CN', ...)
```

#### 3. TTSRequest (请求模型)
```python
from src.models.tts_request import TTSRequest

request = TTSRequest(
    input="Hello World",
    voice="zh-CN-XiaoxiaoNeural",
    format="mp3"
)
```

### 前端核心类

#### 1. VoiceForgeApp (主应用)
```javascript
// 自动初始化，可通过 window.voiceForgeApp 访问
const app = window.voiceForgeApp;
```

#### 2. AudioManager (音频管理)
```javascript
const audioManager = new AudioManager();
audioManager.cleanupAllAudio();
audioManager.createAudioPlayer(container, audioUrl);
```

#### 3. NotificationManager (通知管理)
```javascript
const notificationManager = new NotificationManager();
notificationManager.show('操作成功', 'success');
```

## 🎨 设计模式应用

### 1. 单例模式
- `DatabaseManager`: 确保全局只有一个数据库连接管理器
- `Config`: 配置管理器单例

### 2. 工厂模式
- `create_app()`: Flask应用工厂函数
- `get_config()`: 配置对象工厂

### 3. 策略模式
- 不同环境的配置策略 (Development/Production/Test)
- 不同TTS引擎的处理策略

### 4. 观察者模式
- 前端事件系统
- 音频播放器状态管理

## 🔄 迁移指南

### 从原版本迁移到面向对象版本

1. **配置迁移**
   ```python
   # 原版本
   API_BASE_URL = os.getenv('API_BASE_URL')
   
   # 新版本
   config = get_config()
   api_base_url = config.get('API_BASE_URL')
   ```

2. **数据库操作迁移**
   ```python
   # 原版本
   def log_generation(...):
       with sqlite3.connect(DB_PATH) as conn:
           # ...
   
   # 新版本
   db_manager = DatabaseManager(config)
   db_manager.log_generation(...)
   ```

3. **前端代码迁移**
   ```javascript
   // 原版本
   function generateSpeech() { ... }
   
   // 新版本
   class VoiceForgeApp {
       async handleGenerateSpeech() { ... }
   }
   ```

## 🧪 测试

```bash
# 运行测试（待实现）
python -m pytest tests/

# 测试特定模块
python -m pytest tests/test_models.py
```

## 📈 性能优化

### 1. 内存管理
- 音频播放器自动清理
- 数据库连接池管理
- 配置对象缓存

### 2. 代码分割
- 前端模块按需加载
- 后端蓝图模块化

### 3. 缓存策略
- 配置缓存
- 语音列表缓存

## 🔮 未来计划

### 阶段1: 基础架构 ✅
- [x] 目录结构设计
- [x] 配置管理系统
- [x] 数据库管理器
- [x] 基础模型类

### 阶段2: 核心功能重构 (进行中)
- [ ] TTS服务类完整实现
- [ ] 语音管理服务
- [ ] 文件处理服务
- [ ] 流式传输重构

### 阶段3: 高级功能
- [ ] 插件系统
- [ ] 多TTS引擎支持
- [ ] 用户认证系统
- [ ] API限流和缓存

### 阶段4: 部署和监控
- [ ] Docker容器化
- [ ] 健康检查
- [ ] 性能监控
- [ ] 日志分析

## 🤝 贡献指南

1. 遵循面向对象设计原则
2. 每个类都应该有单一职责
3. 使用类型提示 (Python) 和 JSDoc (JavaScript)
4. 编写单元测试
5. 更新文档

## 📝 注意事项

- 当前版本是重构的基础框架，核心TTS功能还需要完整实现
- 保持与原版本的兼容性，可以并行运行
- 新功能优先在面向对象版本中实现
- 逐步迁移现有功能到新架构
