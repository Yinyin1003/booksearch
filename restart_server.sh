#!/bin/bash
# 停止现有的 Flask 服务器
echo "正在停止 Flask 服务器..."
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# 启动 Flask 服务器
echo "正在启动 Flask 服务器..."
cd /Users/zhouyinyin/Downloads/booksearch1
python3 app.py > /tmp/flask_app.log 2>&1 &
sleep 2

# 检查服务器是否启动成功
if curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo "✅ 服务器已成功启动！"
    echo "   访问地址: http://localhost:5001"
    echo "   日志文件: /tmp/flask_app.log"
else
    echo "⚠️  服务器可能还在启动中，请稍候..."
fi
