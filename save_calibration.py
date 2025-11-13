#!/usr/bin/env python3
"""
保存校准后的书籍位置到book_database.py文件
"""

import re
import sys
from book_database import BookDatabase

def save_calibration_to_file(book_key, position):
    """
    将校准后的位置保存到book_database.py文件
    book_key: 书籍关键词
    position: 位置元组 (x, y, width, height)
    """
    db_file = 'book_database.py'
    
    try:
        # 读取文件
        with open(db_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建新的position字符串
        pos_str = f"({position[0]:.4f}, {position[1]:.4f}, {position[2]:.4f}, {position[3]:.4f})"
        
        # 查找并替换position
        # 匹配模式: "book_key": { ... "position": (x, y, w, h), ... }
        pattern = rf'("{re.escape(book_key)}"\s*:\s*{{[^}}]*"position":\s*)[^,)]+[^)]*\)'
        
        replacement = rf'\1{pos_str}'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content == content:
            # 如果没找到，尝试另一种模式
            pattern2 = rf'("{re.escape(book_key)}"\s*:\s*{{[^}}]*"position":\s*\([^)]+\)'
            new_content = re.sub(pattern2, f'"position": {pos_str}', new_content, flags=re.DOTALL)
        
        # 保存文件
        with open(db_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 已保存 '{book_key}' 的位置到 {db_file}")
        print(f"   新位置: {pos_str}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    """从校准工具获取位置并保存"""
    db = BookDatabase()
    
    print("当前所有书籍的位置:")
    print("="*60)
    
    for key, info in db.get_all_books().items():
        pos = info['position']
        print(f"{key:30s} -> ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f})")
    
    print("="*60)
    print("\n提示: 校准工具中的位置已保存在内存中")
    print("如需永久保存，请手动复制坐标到 book_database.py")
    print("\n或者运行校准工具时按 'q' 退出，工具会显示所有坐标")

if __name__ == "__main__":
    main()

