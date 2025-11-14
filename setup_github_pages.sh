#!/bin/bash

# GitHub Pages 设置脚本

echo "🚀 设置 GitHub Pages 部署"
echo "========================================"
echo ""

# 检查是否已初始化 Git
if [ ! -d ".git" ]; then
    echo "❌ 错误: 请先初始化 Git 仓库"
    echo "运行: git init"
    exit 1
fi

# 创建 docs 目录
echo "📁 创建 docs 目录..."
mkdir -p docs

# 复制静态文件
echo "📋 复制静态文件..."
cp -r static docs/
cp -r templates docs/

# 复制图片（如果存在）
if [ -f bookshelf.jpg ]; then
    echo "📸 复制书架图片..."
    cp bookshelf.jpg docs/
fi

# 创建简化的 index.html（如果需要）
if [ ! -f docs/index.html ]; then
    echo "📄 创建 index.html..."
    cp templates/index.html docs/index.html 2>/dev/null || echo "⚠️  请手动创建 docs/index.html"
fi

echo ""
echo "✅ 文件准备完成！"
echo ""
echo "📋 下一步："
echo ""
echo "1. 修改 docs/static/js/app.js 中的 API 地址"
echo "   将后端 URL 改为你的部署地址"
echo ""
echo "2. 提交文件到 Git："
echo "   git add docs/"
echo "   git commit -m 'Add GitHub Pages files'"
echo "   git push"
echo ""
echo "3. 在 GitHub 仓库设置中："
echo "   Settings → Pages → Source: /docs"
echo ""
echo "4. 访问：https://你的用户名.github.io/booksearch/"
echo ""
echo "⚠️  注意：GitHub Pages 只支持静态文件，"
echo "   后端 API 需要单独部署到 Railway/Render"
echo ""

