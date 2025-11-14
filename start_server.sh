#!/bin/bash
cd /Users/zhouyinyin/Downloads/booksearch1
echo "正在启动 Flask 服务器..."
python3 app.py > /tmp/flask_app.log 2>&1 &
sleep 2

if curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo "✅ 服务器已成功启动！"
    echo "   访问地址: http://localhost:5001"
    echo "   日志文件: /tmp/flask_app.log"
    echo ""
    echo "查看日志: tail -f /tmp/flask_app.log"
else
    echo "⚠️  服务器可能还在启动中，请稍候..."
    echo "查看日志: tail -f /tmp/flask_app.log"
fi
