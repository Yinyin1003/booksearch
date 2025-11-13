# 语音交互书籍搜索系统

一个基于语音识别的智能书籍搜索系统，可以通过说出书名来在投影仪上高亮显示对应的书籍。

## 功能特点

- 🎤 **语音识别**：支持中文语音输入，自动识别书名
- 📚 **智能搜索**：模糊匹配书名，支持部分匹配
- 🎯 **投影高亮**：在投影区域高亮显示找到的书籍
- 🔊 **语音反馈**：找到书籍后提供语音提示

## 系统要求

- Python 3.7+
- 麦克风设备
- 投影仪或显示器（用于高亮显示）

## 安装步骤

1. **克隆或下载项目**

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装系统依赖**

   - **macOS**: 
     ```bash
     brew install portaudio
     ```
   
   - **Linux (Ubuntu/Debian)**:
     ```bash
     sudo apt-get install portaudio19-dev python3-pyaudio
     ```
   
   - **Windows**: 
     PyAudio 应该可以通过 pip 直接安装

## 使用方法

### 基本使用

1. **启动系统**
```bash
python main.py
```

2. **说出书名**
   - 系统会自动监听你的语音输入
   - 说出书名，例如："rethinking users" 或 "设计思维"
   - 系统会自动搜索并高亮显示对应的书籍

3. **退出系统**
   - 按 `Ctrl+C` 退出程序
   - 或在投影窗口按 `q` 键

### 测试模式

如果语音识别有问题，可以使用文本输入模式进行测试：

```bash
python main.py --test
```

在测试模式下，你可以直接输入书名进行测试，无需使用麦克风。

## 配置书籍位置

编辑 `book_database.py` 文件来配置你的书籍位置：

```python
self.books = {
    "书名关键词": {
        "position": (x, y, width, height),  # 归一化坐标 (0-1)
        "shelf": 0,  # 0 = 上排, 1 = 下排
        "full_name": "完整书名"
    },
    # ... 更多书籍
}
```

**坐标说明**：
- `x, y`: 书籍在投影区域的中心位置（0-1之间）
- `width, height`: 书籍的宽度和高度（0-1之间）
- 例如：`(0.5, 0.25, 0.15, 0.12)` 表示书籍位于投影区域中心偏上，宽度占15%，高度占12%

## 项目结构

```
booksearch/
├── main.py                 # 主程序入口
├── voice_recognition.py    # 语音识别模块
├── book_database.py        # 书籍数据库
├── projector_highlight.py # 投影仪高亮显示模块
├── requirements.txt        # Python依赖
└── README.md              # 说明文档
```

## 工作原理

1. **语音识别**：使用 Google Speech Recognition API 将语音转换为文本
2. **书籍匹配**：在数据库中搜索匹配的书籍（支持模糊匹配）
3. **高亮显示**：使用 OpenCV 在投影区域绘制高亮框和书名

## 故障排除

### 麦克风无法识别

- 检查麦克风权限（macOS/Linux）
- 尝试调整系统音量
- 使用 `--test` 模式进行测试

### 投影显示问题

- 确保显示器/投影仪已连接
- 检查分辨率设置（默认 1920x1080）
- 尝试调整 `projector_highlight.py` 中的分辨率参数

### 语音识别不准确

- 确保环境安静
- 说话清晰，语速适中
- 可以尝试使用英文书名（修改 `language='en-US'`）

## 扩展功能

可以添加的功能：
- 📷 摄像头实时识别书籍位置
- 🗄️ 数据库存储书籍信息
- 📊 使用统计和分析
- 🌐 Web界面控制
- 🎨 更多高亮效果和动画

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

