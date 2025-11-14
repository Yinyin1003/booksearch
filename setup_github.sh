#!/bin/bash

# GitHub 部署快速设置脚本

echo "🚀 智能书籍搜索系统 - GitHub 部署设置"
echo "========================================"
echo ""

# 检查是否已初始化 Git
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库已初始化"
else
    echo "✅ Git 仓库已存在"
fi

# 添加所有文件
echo ""
echo "📝 添加文件到 Git..."
git add .
echo "✅ 文件已添加"

# 检查是否有未提交的更改
if git diff --staged --quiet; then
    echo "⚠️  没有需要提交的更改"
else
    echo ""
    echo "💾 提交更改..."
    git commit -m "Initial commit: 智能书籍搜索系统"
    echo "✅ 更改已提交"
fi

echo ""
echo "========================================"
echo "📋 下一步操作："
echo ""
echo "1. 在 GitHub 创建新仓库："
echo "   - 访问 https://github.com/new"
echo "   - 仓库名: booksearch（或你喜欢的名字）"
echo "   - 选择 Public 或 Private"
echo "   - 不要初始化 README"
echo ""
echo "2. 添加远程仓库并推送："
echo "   git remote add origin https://github.com/你的用户名/booksearch.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. 部署到云端："
echo "   - Railway: https://railway.app (推荐)"
echo "   - Render: https://render.com"
echo "   - 详细步骤请查看 SETUP_GITHUB.md"
echo ""
echo "========================================"
echo "📖 更多信息请查看："
echo "   - SETUP_GITHUB.md - GitHub 部署详细步骤"
echo "   - DEPLOY.md - 云端部署指南"
echo "   - README.md - 项目说明"
echo ""

