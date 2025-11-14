"""
书籍管理系统 Web 版本
提供可视化编辑书籍位置、书名和字体样式的功能
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS  # 支持跨域请求（GitHub Pages 需要）
import json
import os
import re
from book_database import BookDatabase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'

# 启用 CORS（允许 GitHub Pages 访问 API）
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 允许所有来源（生产环境可以限制为特定域名）
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 全局变量存储当前设置
display_settings = {
    'box_width': 600,
    'box_height': 180,
    'font_scale': 1.5,
    'font_thickness': 3,
    'max_lines': 3,
    'line_spacing': 8,
    'padding': 15,
    'background_opacity': 0.6,
    'white_block_opacity': 0.6
}

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/preview')
def preview_page():
    """预览页面（语音交互）"""
    return render_template('preview.html')

@app.route('/bookshelf.jpg')
def serve_image():
    """提供书架图片"""
    return send_from_directory('.', 'bookshelf.jpg')

@app.route('/api/books', methods=['GET'])
def get_books():
    """获取所有书籍"""
    # 每次请求都重新加载模块，确保获取最新数据
    import importlib
    import book_database
    importlib.reload(book_database)
    
    db = book_database.BookDatabase()
    books = {}
    for key, info in db.books.items():
        book_data = {
            'position': info['position'],
            'shelf': info['shelf'],
            'full_name': info['full_name']
        }
        # 如果有四点数据，也返回
        if 'points' in info:
            book_data['points'] = info['points']
        books[key] = book_data
    return jsonify(books)

@app.route('/api/books/<path:book_key>', methods=['PUT', 'DELETE'])
def update_book(book_key):
    """更新或删除书籍信息"""
    # URL解码
    import urllib.parse
    import os
    book_key = urllib.parse.unquote(book_key)
    
    print(f"\n{'='*60}")
    print(f"收到请求: {request.method} /api/books/{book_key}")
    print(f"{'='*60}")
    
    if request.method == 'DELETE':
        # 删除书籍
        db_file = 'book_database.py'
        if not os.path.exists(db_file):
            return jsonify({'error': '数据库文件不存在'}), 404
        
        with open(db_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 备份原文件
        backup_file = db_file + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 查找并删除书籍条目
        new_lines = []
        skip_entry = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if f'"{book_key}"' in line and ':' in line and '{' in line:
                # 找到开始，跳过整个条目
                skip_entry = True
                i += 1
                continue
            
            if skip_entry:
                # 检查是否到达条目结束
                if '},' in line or '}' in line:
                    # 检查缩进，如果缩进减少，说明条目结束
                    if line.strip().startswith('}'):
                        skip_entry = False
                        # 跳过这一行（删除）
                        i += 1
                        continue
                # 跳过当前行
                i += 1
                continue
            
            new_lines.append(line)
            i += 1
        
        # 保存文件
        with open(db_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return jsonify({'success': True})
    
    # PUT 方法：更新书籍信息
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': '请求数据格式错误，需要JSON格式'}), 400
    except Exception as e:
        print(f"❌ 解析JSON失败: {e}")
        return jsonify({'error': f'解析请求数据失败: {str(e)}'}), 400
    
    print(f"收到数据: {data}")
    
    # 读取book_database.py文件
    db_file = 'book_database.py'
    if not os.path.exists(db_file):
        print(f"❌ 数据库文件不存在: {db_file}")
        return jsonify({'error': '数据库文件不存在'}), 404
    
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_file = db_file + '.backup'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 初始化更新标志
    position_found = False
    name_found = False
    points_found = False
    
    # 更新位置（支持四点模式）
    if 'position' in data or 'points' in data:
        # 优先使用四点模式
        if 'points' in data and data['points']:
            points = data['points']
            if len(points) != 4:
                return jsonify({'error': '四点模式需要4个点'}), 400
            
            # 计算四个点的边界框（用于position字段，保持兼容性）
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            
            # 转换为矩形格式（中心点+宽高）
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min
            
            new_position = f"({center_x:.4f}, {center_y:.4f}, {width:.4f}, {height:.4f})"
            
            # 保存四个点的坐标（作为新字段）
            points_str = f"[({points[0][0]:.4f}, {points[0][1]:.4f}), ({points[1][0]:.4f}, {points[1][1]:.4f}), ({points[2][0]:.4f}, {points[2][1]:.4f}), ({points[3][0]:.4f}, {points[3][1]:.4f})]"
            
        elif 'position' in data:
            position = data['position']
            if len(position) != 4:
                return jsonify({'error': '位置数据格式错误，需要4个值 [x, y, w, h]'}), 400
            
            x, y, w, h = position
            new_position = f"({x:.4f}, {y:.4f}, {w:.4f}, {h:.4f})"
            points_str = None
        else:
            return jsonify({'error': '需要提供position或points数据'}), 400
        
        # 更精确的替换
        lines = content.split('\n')
        book_entry_start = -1
        for i, line in enumerate(lines):
            # 匹配书籍键，考虑引号和冒号
            if f'"{book_key}"' in line and ':' in line:
                book_entry_start = i
                # 在接下来的几行中查找position行
                for j in range(i, min(i+20, len(lines))):
                    if '"position"' in lines[j]:
                        old_line = lines[j]
                        # 匹配各种格式：可能是 "position": (x, y, w, h) 或 "position": (x, y, w, h),
                        pattern = r'"position":\s*\([^)]+\)'
                        new_line = re.sub(pattern, f'"position": {new_position}', old_line)
                        if new_line != old_line:
                            lines[j] = new_line
                            position_found = True
                            print(f"✅ 更新位置: {book_key}")
                            print(f"   旧值: {old_line.strip()}")
                            print(f"   新值: {new_line.strip()}")
                        else:
                            # 即使位置值相同，如果我们在更新points，也应该标记position_found为True
                            # 因为position字段需要存在（用于兼容性）
                            if points_str:
                                position_found = True
                                print(f"ℹ️  位置值未改变，但需要保持position字段: {book_key}")
                            else:
                                print(f"ℹ️  位置未改变: {book_key}")
                        
                        # 如果有四点数据，添加或更新points字段
                        if points_str:
                            # 查找是否已有points字段
                            has_points = False
                            for k in range(j, min(j+15, len(lines))):
                                if '"points"' in lines[k]:
                                    # 更新现有的points字段
                                    old_points_line = lines[k]
                                    # 使用更简单可靠的正则表达式：匹配整个points列表（包括嵌套的括号）
                                    # 使用非贪婪匹配，匹配到第一个完整的 ] 为止
                                    pattern_points = r'"points":\s*\[.*?\]'
                                    match = re.search(pattern_points, old_points_line)
                                    if match:
                                        # 找到匹配，替换整个points部分
                                        new_points_line = re.sub(pattern_points, f'"points": {points_str}', old_points_line)
                                        if new_points_line != old_points_line:
                                            lines[k] = new_points_line
                                            points_found = True
                                            print(f"✅ 更新四点: {book_key}")
                                            print(f"   旧值: {old_points_line.strip()}")
                                            print(f"   新值: {new_points_line.strip()}")
                                        else:
                                            print(f"ℹ️  四点未改变（值相同）: {book_key}")
                                            print(f"   旧值: {old_points_line.strip()}")
                                            print(f"   新值应该是: {points_str}")
                                    else:
                                        print(f"⚠️  无法匹配points行: {old_points_line.strip()}")
                                    has_points = True
                                    break
                            
                            # 如果没有points字段，在position后面添加
                            if not has_points:
                                # 在position行后面插入points行
                                indent = len(lines[j]) - len(lines[j].lstrip())
                                points_line = ' ' * indent + f'"points": {points_str},'
                                lines.insert(j + 1, points_line)
                                points_found = True
                                print(f"✅ 添加四点: {book_key}")
                        break
                break
        
        # 如果更新了位置或四点，更新内容
        if position_found or points_found:
            content = '\n'.join(lines)
            print(f"✅ 内容已更新: position_found={position_found}, points_found={points_found}")
        else:
            print(f"⚠️  未找到位置行或四点数据未改变: {book_key}")
            print(f"   调试: position_found={position_found}, points_found={points_found}, points_str={points_str if 'points_str' in locals() else 'N/A'}")
    
    # 更新书名
    if 'full_name' in data:
        full_name = data['full_name']
        # 转义引号
        escaped_name = full_name.replace('"', '\\"')
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # 匹配书籍键，考虑引号和冒号
            if f'"{book_key}"' in line and ':' in line:
                # 在接下来的几行中查找full_name行
                for j in range(i, min(i+15, len(lines))):
                    if '"full_name"' in lines[j]:
                        old_line = lines[j]
                        pattern = r'"full_name":\s*"[^"]*"'
                        new_line = re.sub(pattern, f'"full_name": "{escaped_name}"', old_line)
                        if new_line != old_line:
                            lines[j] = new_line
                            name_found = True
                            print(f"✅ 更新书名: {book_key}")
                            print(f"   旧值: {old_line.strip()}")
                            print(f"   新值: {new_line.strip()}")
                        else:
                            print(f"ℹ️  书名未改变: {book_key}")
                        break
                break
        
        if name_found:
            content = '\n'.join(lines)
        else:
            print(f"⚠️  未找到书名行: {book_key}")
    
    # 保存文件
    try:
        # 检查是否有任何更改
        if 'position' not in data and 'points' not in data and 'full_name' not in data:
            print("⚠️  没有需要更新的数据")
            return jsonify({'success': False, 'message': '没有需要更新的数据'})
        
        # 检查是否找到了要更新的内容
        position_updated = ('position' in data or 'points' in data) and (position_found or points_found)
        name_updated = 'full_name' in data and name_found
        
        if not position_updated and not name_updated:
            print("⚠️  未找到要更新的内容")
            print(f"   调试信息: position_found={position_found}, points_found={points_found}, name_found={name_found}")
            return jsonify({'success': False, 'message': '未找到要更新的书籍或内容未改变'})
        
        # 验证文件内容是否有效
        try:
            # 尝试重新加载验证语法
            compile(content, db_file, 'exec')
        except SyntaxError as e:
            print(f"❌ 文件语法错误: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'文件语法错误: {str(e)}'}), 500
        
        # 保存文件
        with open(db_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 验证文件是否真的保存了
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file)
            print(f"✅ 文件已保存: {db_file} (大小: {file_size} 字节)")
            
            # 重新加载 book_database 模块，确保下次读取时使用最新数据
            import importlib
            import book_database
            importlib.reload(book_database)
            print(f"✅ 已重新加载 book_database 模块")
            
            print(f"{'='*60}\n")
            return jsonify({
                'success': True, 
                'message': '书籍更新成功', 
                'file_size': file_size,
                'position_updated': position_updated,
                'name_updated': name_updated,
                'points_updated': points_found
            })
        else:
            print(f"❌ 文件保存后不存在: {db_file}")
            print(f"{'='*60}\n")
            return jsonify({'error': '文件保存失败'}), 500
            
    except Exception as e:
        import traceback
        print(f"❌ 保存文件失败: {e}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': f'保存失败: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    import traceback
    traceback.print_exc()
    return jsonify({'error': '服务器内部错误'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/settings', methods=['GET', 'PUT'])
def settings():
    """获取或更新显示设置"""
    global display_settings
    
    if request.method == 'GET':
        return jsonify(display_settings)
    else:
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': '请求数据格式错误'}), 400
            display_settings.update(data)
            return jsonify(display_settings)
        except Exception as e:
            return jsonify({'error': f'更新设置失败: {str(e)}'}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """搜索书籍（用于语音识别）"""
    # 每次搜索前都重新加载book_database，确保使用最新数据
    import importlib
    import book_database
    importlib.reload(book_database)
    
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': '查询内容为空'}), 400
    
    db = book_database.BookDatabase()
    book_key, book_info = db.search_book(query)
    
    if book_info:
        result = {
            'success': True,
            'book_key': book_key,
            'book_name': book_info['full_name'],
            'position': book_info['position']
        }
        # 如果有四点数据，也返回
        if 'points' in book_info:
            result['points'] = book_info['points']
        return jsonify(result)
    else:
        return jsonify({
            'success': False,
            'error': f'未找到匹配的书籍: {query}'
        })

@app.route('/api/preview', methods=['POST'])
def preview():
    """预览效果（生成高亮图片）"""
    # 每次预览前都重新加载book_database，确保使用最新数据
    import importlib
    import book_database
    importlib.reload(book_database)
    
    from projector_simple import ProjectorSimple
    
    data = request.json
    book_key = data.get('book_key')
    image_path = data.get('image_path', 'bookshelf.jpg')
    
    if not os.path.exists(image_path):
        return jsonify({'error': '图片文件不存在'}), 404
    
    db = book_database.BookDatabase()
    if book_key not in db.books:
        return jsonify({'error': '书籍不存在'}), 404
    
    book_info = db.books[book_key]
    
    # 生成预览（优先使用四点定位）
    projector = ProjectorSimple(image_path=image_path, output_dir='./projector_output')
    points = book_info.get('points')  # 获取四点数据（如果存在）
    if points and len(points) == 4:
        # 使用四点定位
        projector.highlight_book(book_info['position'], book_info['full_name'], points=points)
    else:
        # 使用矩形定位（兼容旧格式）
        projector.highlight_book(book_info['position'], book_info['full_name'])
    
    # 返回预览URL（优先返回GIF，因为预览页面直接显示GIF）
    gif_path = os.path.join('projector_output', 'highlight.gif')
    if os.path.exists(gif_path):
        return jsonify({
            'success': True,
            'preview_url': '/projector_output/highlight.gif'
        })
    else:
        html_path = os.path.join('projector_output', 'highlight_viewer.html')
        if os.path.exists(html_path):
            return jsonify({
                'success': True,
                'preview_url': '/projector_output/highlight_viewer.html'
            })
        else:
            jpg_path = os.path.join('projector_output', 'highlight.jpg')
            if os.path.exists(jpg_path):
                return jsonify({
                    'success': True,
                    'preview_url': '/projector_output/highlight.jpg'
                })
            else:
                return jsonify({'error': '预览文件未生成'}), 500

@app.route('/projector_output/<filename>')
def serve_preview(filename):
    """提供预览文件"""
    return send_from_directory('projector_output', filename)

if __name__ == '__main__':
    # 从环境变量获取端口，默认5001（本地开发）或5000（生产环境）
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

