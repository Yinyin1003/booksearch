#!/usr/bin/env python3
"""
精确书籍位置校准工具（改进版）
可以精确选择书籍的文字区域，并自动保存到book_database.py
"""

import cv2
import numpy as np
import re
import os
import sys
from book_database import BookDatabase

class PreciseCalibrator:
    def __init__(self, image_path):
        """初始化精确校准工具"""
        self.image_path = image_path
        self.db = BookDatabase()
        
        # 加载图片
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"无法加载图片: {image_path}")
        
        self.display_image = self.original_image.copy()
        self.width = self.original_image.shape[1]
        self.height = self.original_image.shape[0]
        
        # 鼠标状态
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.current_book = None
        self.book_index = 0
        self.all_books = list(self.db.get_all_books().keys())
        
        # 已校准的书籍
        self.calibrated = {}
        
        print(f"📸 图片尺寸: {self.width}x{self.height}")
        print(f"📚 找到 {len(self.all_books)} 本书需要校准")
        print("\n" + "="*60)
        print("使用说明:")
        print("="*60)
        print("1. 点击并拖拽选择书籍的**文字区域**（不是整本书）")
        print("2. 选择完成后，按 's' 保存当前位置")
        print("3. 按 'n' 切换到下一本书")
        print("4. 按 'p' 切换到上一本书")
        print("5. 按 'r' 重置当前选择")
        print("6. 按 'q' 保存所有更改并退出")
        print("="*60)
        print("\n💡 提示: 只选择书籍的标题文字部分，不要选择整本书")
    
    def normalize_position(self, x1, y1, x2, y2):
        """将像素坐标转换为归一化坐标"""
        x_min = min(x1, x2)
        x_max = max(x1, x2)
        y_min = min(y1, y2)
        y_max = max(y1, y2)
        
        # 计算中心点和尺寸（归一化）
        center_x = (x_min + x_max) / 2.0 / self.width
        center_y = (y_min + y_max) / 2.0 / self.height
        width = (x_max - x_min) / self.width
        height = (y_max - y_min) / self.height
        
        return (center_x, center_y, width, height)
    
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        if hasattr(self, 'display_scale') and self.display_scale < 1.0:
            x = int(x / self.display_scale)
            y = int(y / self.display_scale)
            x = min(x, self.width - 1)
            y = min(y, self.height - 1)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            self.update_display()
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                self.update_display()
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)
            if self.start_point and self.end_point:
                x1, y1 = self.start_point
                x2, y2 = self.end_point
                pos = self.normalize_position(x1, y1, x2, y2)
                print(f"   选择区域: ({x1}, {y1}) -> ({x2}, {y2})")
                print(f"   归一化坐标: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f})")
            self.update_display()
    
    def update_display(self):
        """更新显示"""
        self.display_image = self.original_image.copy()
        
        # 显示所有已校准的书籍（绿色）
        for key, pos in self.calibrated.items():
            px, py, pw, ph = self.normalized_to_pixel(pos)
            x1 = px - pw // 2
            y1 = py - ph // 2
            x2 = px + pw // 2
            y2 = py + ph // 2
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(self.display_image, key[:20], (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 显示当前书籍的已保存位置（蓝色）
        if self.current_book:
            book_info = self.db.get_all_books().get(self.current_book)
            if book_info:
                px, py, pw, ph = self.normalized_to_pixel(book_info['position'])
                x1 = px - pw // 2
                y1 = py - ph // 2
                x2 = px + pw // 2
                y2 = py + ph // 2
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # 显示当前正在绘制的选择框（红色，粗线）
        if self.start_point and self.end_point:
            cv2.rectangle(self.display_image, self.start_point, self.end_point, (0, 0, 255), 4)
            # 显示坐标信息
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            info = f"W:{w} H:{h}"
            cv2.putText(self.display_image, info, (min(x1, x2), min(y1, y2) - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示当前书籍信息
        if self.current_book:
            book_info = self.db.get_all_books().get(self.current_book, {})
            info_text = f"Book {self.book_index + 1}/{len(self.all_books)}: {self.current_book}"
            if book_info:
                pos = book_info['position']
                info_text += f" | Current: ({pos[0]:.3f}, {pos[1]:.3f})"
            if self.current_book in self.calibrated:
                pos = self.calibrated[self.current_book]
                info_text += f" | New: ({pos[0]:.3f}, {pos[1]:.3f})"
            
            cv2.putText(self.display_image, info_text, (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(self.display_image, book_info.get('full_name', '')[:60], (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # 显示操作提示
        tips = [
            "Click & Drag: Select TEXT area | 's': Save | 'n': Next | 'p': Prev | 'r': Reset | 'q': Quit",
            "IMPORTANT: Select only the TEXT/TITLE area, not the whole book!"
        ]
        for i, tip in enumerate(tips):
            cv2.putText(self.display_image, tip, (10, self.height - 40 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # 调整窗口大小
        max_width = 1920
        max_height = 1080
        scale = min(max_width / self.width, max_height / self.height, 1.0)
        self.display_scale = scale
        
        if scale < 1.0:
            display_width = int(self.width * scale)
            display_height = int(self.height * scale)
            display_img = cv2.resize(self.display_image, (display_width, display_height))
        else:
            display_img = self.display_image
            self.display_scale = 1.0
        
        cv2.imshow('Precise Book Position Calibrator', display_img)
    
    def normalized_to_pixel(self, pos):
        """将归一化坐标转换为像素坐标"""
        x, y, w, h = pos
        px = int(x * self.width)
        py = int(y * self.height)
        pw = int(w * self.width)
        ph = int(h * self.height)
        return (px, py, pw, ph)
    
    def save_position(self):
        """保存当前位置"""
        if not self.start_point or not self.end_point:
            print("❌ 请先选择书籍的文字区域")
            return False
        
        if not self.current_book:
            return False
        
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        pos = self.normalize_position(x1, y1, x2, y2)
        
        self.calibrated[self.current_book] = pos
        print(f"✅ 已保存 '{self.current_book}' 的位置: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f})")
        return True
    
    def save_to_file(self):
        """保存所有校准结果到book_database.py"""
        if not self.calibrated:
            print("⚠️  没有需要保存的更改")
            return
        
        db_file = 'book_database.py'
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新每个校准的书籍
            for book_key, pos in self.calibrated.items():
                pos_str = f"({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f})"
                
                # 匹配模式：找到该书籍的position行
                pattern = rf'("{re.escape(book_key)}"\s*:\s*{{[^}}]*"position":\s*\([^)]+\))'
                replacement = f'"position": {pos_str}'
                
                # 替换
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                if new_content != content:
                    content = new_content
                    print(f"✅ 已更新 '{book_key}' 的位置")
                else:
                    # 尝试更精确的匹配
                    pattern2 = rf'("{re.escape(book_key)}"\s*:\s*{{[^}}]*"position":\s*)[^,)]+[^)]*\)'
                    replacement2 = rf'\1{pos_str}'
                    new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
                    if new_content != content:
                        content = new_content
                        print(f"✅ 已更新 '{book_key}' 的位置")
                    else:
                        print(f"⚠️  无法找到 '{book_key}' 的位置定义，请手动更新")
            
            # 保存文件
            with open(db_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ 所有更改已保存到 {db_file}")
            print(f"   共更新了 {len(self.calibrated)} 本书的位置")
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            import traceback
            traceback.print_exc()
            print("\n请手动复制以下坐标到 book_database.py:")
            for book_key, pos in self.calibrated.items():
                print(f'\n"{book_key}": {{')
                print(f'    "position": ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f}),')
    
    def run(self):
        """运行校准工具"""
        if not self.all_books:
            print("❌ 没有找到书籍")
            return
        
        window_name = 'Precise Book Position Calibrator'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # 从第一本书开始
        self.current_book = self.all_books[0]
        print(f"\n📖 当前书籍: {self.current_book}")
        print("   请点击并拖拽选择书籍的**文字/标题区域**（不是整本书）")
        
        self.update_display()
        cv2.waitKey(100)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                if self.calibrated:
                    print("\n保存更改...")
                    self.save_to_file()
                break
            
            elif key == ord('s'):
                if self.save_position():
                    self.update_display()
            
            elif key == ord('n'):
                # 保存当前位置并切换到下一本
                if self.start_point and self.end_point:
                    self.save_position()
                self.book_index = (self.book_index + 1) % len(self.all_books)
                self.current_book = self.all_books[self.book_index]
                self.start_point = None
                self.end_point = None
                print(f"\n📖 当前书籍 ({self.book_index + 1}/{len(self.all_books)}): {self.current_book}")
                self.update_display()
            
            elif key == ord('p'):
                # 保存当前位置并切换到上一本
                if self.start_point and self.end_point:
                    self.save_position()
                self.book_index = (self.book_index - 1) % len(self.all_books)
                self.current_book = self.all_books[self.book_index]
                self.start_point = None
                self.end_point = None
                print(f"\n📖 当前书籍 ({self.book_index + 1}/{len(self.all_books)}): {self.current_book}")
                self.update_display()
            
            elif key == ord('r'):
                self.start_point = None
                self.end_point = None
                print("   已重置选择")
                self.update_display()
            
            self.update_display()
        
        cv2.destroyAllWindows()
        print("\n✅ 校准完成！")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 calibrate_precise.py <图片路径>")
        print("示例: python3 calibrate_precise.py bookshelf.jpg")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    try:
        calibrator = PreciseCalibrator(image_path)
        calibrator.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

