"""
调试高亮位置工具
用于可视化查看和调整书籍高亮位置
"""

import cv2
import sys
from book_database import BookDatabase

def debug_book_position(image_path, book_key):
    """调试指定书籍的高亮位置"""
    db = BookDatabase()
    
    if book_key not in db.books:
        print(f"❌ 未找到书籍: {book_key}")
        print(f"可用书籍:")
        for key in list(db.books.keys())[:10]:
            print(f"  - {key}")
        return
    
    book_info = db.books[book_key]
    position = book_info["position"]
    
    # 加载图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 无法加载图片: {image_path}")
        return
    
    height, width = img.shape[:2]
    print(f"\n📸 图片尺寸: {width}x{height}")
    print(f"📚 书籍: {book_info['full_name']}")
    print(f"📍 归一化坐标: {position}")
    
    # 转换为像素坐标
    center_x = position[0] * width
    center_y = position[1] * height
    w = int(position[2] * width)
    h = int(position[3] * height)
    
    # 计算左上角坐标
    x = int(center_x - w / 2)
    y = int(center_y - h / 2)
    
    print(f"   中心点: ({center_x:.1f}, {center_y:.1f})")
    print(f"   尺寸: {w}x{h}")
    print(f"   左上角: ({x}, {y})")
    
    # 判断方向
    is_vertical = h > w
    print(f"   方向: {'竖排(书脊)' if is_vertical else '横排'}")
    
    # 计算文字区域
    if is_vertical:
        text_ratio_w = 0.80
        text_ratio_h = 0.60
        text_w = int(w * text_ratio_w)
        text_h = int(h * text_ratio_h)
        text_x = x + (w - text_w) // 2
        text_y = y + int(h * 0.15)
    else:
        text_ratio = 0.65
        text_w = int(w * text_ratio)
        text_h = int(h * text_ratio)
        text_x = x + (w - text_w) // 2
        text_y = y + int(h * 0.20)
    
    print(f"   文字区域: ({text_x}, {text_y}, {text_w}, {text_h})")
    
    # 创建调试图片
    debug_img = img.copy()
    
    # 绘制书籍区域（蓝色框）
    cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
    cv2.putText(debug_img, "Book Area", (x, max(30, y - 10)), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    # 绘制文字区域（绿色框）
    cv2.rectangle(debug_img, (text_x, text_y), (text_x + text_w, text_y + text_h), (0, 255, 0), 3)
    cv2.putText(debug_img, "Text Area", (text_x, max(30, text_y - 10)), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 绘制中心点（红色圆）
    cv2.circle(debug_img, (int(center_x), int(center_y)), 10, (0, 0, 255), -1)
    
    # 保存调试图片
    output_path = "projector_output/debug_highlight.jpg"
    import os
    os.makedirs("projector_output", exist_ok=True)
    cv2.imwrite(output_path, debug_img)
    
    print(f"\n✅ 调试图片已保存: {output_path}")
    print(f"   蓝色框 = 书籍区域")
    print(f"   绿色框 = 文字高亮区域")
    print(f"   红点 = 中心点")
    
    # 尝试打开图片
    try:
        import subprocess
        import platform
        if platform.system() == 'Darwin':
            subprocess.run(['open', output_path], check=False)
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 debug_highlight.py <图片路径> <书籍关键词>")
        print("示例: python3 debug_highlight.py bookshelf.jpg 'lean impact'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    book_key = sys.argv[2].lower().strip()
    
    debug_book_position(image_path, book_key)

