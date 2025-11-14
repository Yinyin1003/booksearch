# 项目文件结构说明

## 核心文件（必需）

### Web应用
- `app.py` - Flask web应用主文件
- `templates/` - HTML模板目录
  - `index.html` - 主页面
  - `preview.html` - 语音预览页面
- `static/` - 静态文件目录
  - `css/style.css` - 样式文件
  - `js/app.js` - 前端JavaScript

### 主程序
- `main.py` - 语音识别主程序
- `voice_recognition.py` - 语音识别模块
- `book_database.py` - 书籍数据库

### 投影仪模块
- `projector_simple.py` - 简单模式（生成GIF）
- `projector_highlight.py` - 高亮模式
- `projector_tkinter.py` - Tkinter GUI模式

### 工具
- `calibrate_positions.py` - 位置校准工具

### 配置文件
- `requirements.txt` - Python依赖
- `bookshelf.jpg` - 书架图片
- `.gitignore` - Git忽略文件

### 部署配置
- `Procfile` - 部署平台配置
- `runtime.txt` - Python版本
- `gunicorn_config.py` - Gunicorn配置
- `railway.json` - Railway配置
- `render.yaml` - Render配置
- `vercel.json` - Vercel配置
- `api/index.py` - Vercel Serverless入口

### 文档
- `README.md` - 项目说明文档
- `DEPLOY.md` - 部署指南

### 脚本
- `restart_server.sh` - 重启服务器脚本
- `start_server.sh` - 启动服务器脚本
- `stop_server.sh` - 停止服务器脚本

## 目录结构

```
booksearch1/
├── api/                    # Vercel Serverless函数
│   └── index.py
├── docs/                   # GitHub Pages静态文件
│   ├── index.html
│   └── static/
│       └── js/
├── projector_output/       # 输出目录（生成的高亮图片/GIF）
├── static/                 # Flask静态文件
│   ├── css/
│   └── js/
├── templates/              # Flask模板
│   ├── index.html
│   └── preview.html
└── [核心文件]
```

## 已删除的文件

- 备份文件（*.backup）
- Python缓存（__pycache__/, *.pyc）
- 测试文件（test_*.py, debug_*.py）
- 多余的校准工具
- 临时图片（calibration_*.jpg）
- 重复的部署文档
- 中文说明文档（已整合到README.md）
- 重复的脚本文件

