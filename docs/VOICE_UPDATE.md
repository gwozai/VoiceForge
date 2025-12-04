# Edge-TTS语音更新指南

## 概述

VoiceForge现在支持动态获取所有Edge-TTS语音，包含594个语音，覆盖153种语言！

## 快速开始

### 1. 更新语音列表

```bash
# 使用Makefile（推荐）
make update-voices

# 或直接运行脚本
python scripts/update_voices.py
```

### 2. 运行面向对象版本

```bash
# 使用Makefile
make run-oop

# 或直接运行
python main.py
```

## 语音统计

更新后的语音列表包含：

- **总语音数**: 594个
- **语言数量**: 153种
- **主要语言**:
  - 中文(简体): 31个语音
  - English (US): 76个语音
  - Deutsch (German): 19个语音
  - Français (French): 19个语音
  - Español (Spanish): 22个语音
  - 日本語 (Japanese): 9个语音
  - 한국어 (Korean): 12个语音

## 支持的语言

### 主要语言
- **中文**: 简体中文、繁体中文(台湾)、繁体中文(香港)、粤语、吴语等方言
- **英语**: 美国、英国、澳大利亚、加拿大、印度、南非等
- **欧洲语言**: 德语、法语、西班牙语、意大利语、葡萄牙语、俄语等
- **亚洲语言**: 日语、韩语、泰语、越南语、印地语、阿拉伯语等

### 特色语言
- **非洲语言**: 南非荷兰语、祖鲁语、斯瓦希里语、索马里语
- **小众语言**: 威尔士语、爱尔兰语、巴斯克语、加泰罗尼亚语
- **地区方言**: 中国各地方言、西班牙各国变体

## 文件结构

```
src/config/
├── complete_edge_voices.json    # 完整语音列表（594个）
├── edge_tts_voices.json        # 基础语音列表（备用）
└── edge_voices_constants.py    # Python常量文件（可选）

scripts/
├── update_voices.py            # 简化更新脚本
└── fetch_edge_voices.py        # 完整获取脚本
```

## 语音格式

每个语音包含以下信息：

```json
{
  "name": "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)",
  "short_name": "zh-CN-XiaoxiaoNeural", 
  "gender": "Female",
  "locale": "zh-CN"
}
```

## 使用方法

### 1. 在界面中使用

1. 点击"加载所有语音"按钮
2. 从下拉列表中选择语音（显示性别信息）
3. 点击"试听"预览语音效果
4. 生成语音

### 2. 在代码中使用

```python
from src.services.voice_service import VoiceService

# 创建语音服务
voice_service = VoiceService()

# 获取所有语音
voices = voice_service.get_all_voices()

# 按语言查看
for language, voice_list in voices.items():
    print(f"{language}: {len(voice_list)} 个语音")
```

## 自动更新

### 定期更新

建议定期更新语音列表以获取最新的Edge-TTS语音：

```bash
# 每周更新一次
crontab -e
# 添加: 0 0 * * 0 cd /path/to/VoiceForge && make update-voices
```

### CI/CD集成

在GitHub Actions中自动更新：

```yaml
- name: Update Edge-TTS Voices
  run: |
    pip install edge-tts
    make update-voices
    git add src/config/complete_edge_voices.json
    git commit -m "Auto-update Edge-TTS voices" || exit 0
```

## 故障排除

### 1. 网络问题

如果更新失败，检查网络连接：

```bash
# 测试网络连接
ping speech.platform.bing.com
```

### 2. 依赖问题

确保安装了edge-tts：

```bash
pip install edge-tts
```

### 3. 权限问题

确保有写入权限：

```bash
chmod +w src/config/
```

### 4. 回退方案

如果更新失败，系统会自动使用默认语音列表，包含：
- OpenAI语音（6个）
- 基础中文语音（4个）
- 基础英语语音（4个）

## 高级功能

### 1. 自定义过滤

可以修改`update_voices.py`来过滤特定语音：

```python
# 只保留中文和英文语音
filtered_voices = {}
for language, voices in grouped_voices.items():
    if any(keyword in language for keyword in ['中文', 'English', 'Chinese']):
        filtered_voices[language] = voices
```

### 2. 语音质量检测

可以添加语音质量检测：

```python
# 检测语音是否可用
async def test_voice_quality(voice_name):
    try:
        communicate = edge_tts.Communicate("测试", voice_name)
        await communicate.save("test.mp3")
        return True
    except:
        return False
```

## 贡献

欢迎提交PR来改进语音更新功能：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本功能遵循项目的GPL-3.0许可证。
