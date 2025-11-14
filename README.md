# 📚 智能书籍搜索系统

一个基于语音识别和图像高亮的智能书籍管理系统，支持通过语音搜索书籍并在图片上高亮显示位置。

## ✨ 功能特性

- 🎤 **语音搜索**: 使用语音识别快速搜索书籍
- 📍 **位置高亮**: 在书架图片上高亮显示书籍位置
- 🎨 **可视化编辑**: Web界面编辑书籍位置、书名和显示样式
- 🔄 **四点定位**: 支持倾斜书籍的精确定位
- ✨ **动画效果**: GIF动画闪烁和光晕效果
- 🌐 **Web界面**: 现代化的Web管理界面

## 🚀 快速开始

### 本地运行

1. **克隆仓库**
   ```bash
   git clone https://github.com/你的用户名/booksearch.git
   cd booksearch
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **准备书架图片**
   - 将书架照片命名为 `bookshelf.jpg` 放在项目根目录
   - 或通过Web界面上传

4. **启动Web服务**
   ```bash
   python3 app.py
   ```

5. **访问**
   - 管理界面: http://localhost:5001
   - 语音预览: http://localhost:5001/preview

### 部署到云端

本项目支持多种部署平台，详见 [DEPLOY.md](DEPLOY.md)

**推荐平台：**
- 🚂 [Railway](https://railway.app) - 免费，简单易用
- 🎨 [Render](https://render.com) - 免费tier
- ⚡ [Vercel](https://vercel.com) - 免费，快速

## 📖 使用说明

### Web管理界面

1. **访问管理界面**
   - 打开 http://localhost:5001
   - 上传书架图片（如果还没有）

2. **编辑书籍位置**
   - 点击左侧书籍列表中的书籍
   - 在图片上点击四个角点设置位置
   - 调整书名和显示设置
   - 点击"更新书籍"保存

3. **语音搜索预览**
   - 点击"🎤 语音搜索预览"按钮
   - 在新页面中点击麦克风图标
   - 说出书名进行搜索
   - 系统会自动高亮显示书籍位置

### 命令行模式

```bash
# 交互模式测试
python3 main.py --image bookshelf.jpg --test

# 语音识别模式
python3 main.py --image bookshelf.jpg
```

## 📁 项目结构

```
booksearch/
├── app.py                 # Flask Web应用
├── main.py                # 命令行主程序
├── book_database.py       # 书籍数据库
├── projector_simple.py    # 图片高亮模块
├── voice_recognition.py   # 语音识别模块
├── templates/             # HTML模板
│   ├── index.html         # 管理界面
│   └── preview.html       # 语音预览界面
├── static/                # 静态文件
│   ├── css/
│   └── js/
└── requirements.txt       # Python依赖
```

## 🛠️ 技术栈

- **后端**: Python 3.10+, Flask
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **图像处理**: OpenCV, Pillow
- **语音识别**: Web Speech API, SpeechRecognition
- **部署**: Railway/Render/Heroku/Vercel

## 📝 配置说明

### 环境变量

- `PORT`: 服务端口（默认: 5001）
- `FLASK_DEBUG`: 调试模式（默认: False）

### 书籍数据格式

书籍数据存储在 `book_database.py` 中，格式：

```python
{
    "book_key": {
        "position": (x, y, width, height),  # 归一化坐标
        "points": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],  # 四点定位
        "full_name": "完整书名",
        "shelf": 0  # 书架编号
    }
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- OpenCV 图像处理库
- Flask Web框架
- Web Speech API

## 📞 支持

如有问题，请：
1. 查看 [DEPLOY.md](DEPLOY.md) 了解部署详情
2. 提交 Issue 描述问题
3. 查看项目 Wiki（如有）

---

⭐ 如果这个项目对你有帮助，请给个 Star！
