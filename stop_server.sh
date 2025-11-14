#!/bin/bash
echo "正在停止 Flask 服务器..."
pkill -f "python.*app.py" 2>/dev/null
sleep 1
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  仍有进程在运行，强制停止..."
    pkill -9 -f "python.*app.py" 2>/dev/null
fi
echo "✅ 服务器已停止"
