#!/usr/bin/env python3
"""
检查 Render 部署配置的脚本
"""
import os
import sys

def check_config():
    """检查配置"""
    print("=" * 60)
    print("Render 部署配置检查")
    print("=" * 60)
    
    # 检查文件
    files_to_check = [
        'app.py',
        'requirements.txt',
        'gunicorn_config.py',
        'render.yaml'
    ]
    
    print("\n📁 文件检查:")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - 缺失")
    
    # 检查 requirements.txt
    print("\n📦 依赖检查:")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
            if 'gunicorn' in content:
                print("  ✅ gunicorn 已包含")
            else:
                print("  ❌ gunicorn 未找到")
    
    # 检查 app.py
    print("\n🐍 Flask 应用检查:")
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
            if 'Flask' in content and 'app = Flask' in content:
                print("  ✅ Flask 应用配置正确")
            else:
                print("  ⚠️  Flask 应用可能配置不正确")
    
    # 推荐配置
    print("\n💡 推荐的 Start Command:")
    print("  gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --worker-class sync --log-level info")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_config()

