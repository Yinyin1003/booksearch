#!/usr/bin/env python3
"""
书籍位置校准工具
帮助用户可视化调整书籍在照片中的位置坐标
"""

import cv2
import numpy as np
import json
import os
import sys
from book_database import BookDatabase

class PositionCalibrator:
    def __init__(self, image_path, book_key=None):
        """
        初始化校准工具
        image_path: 书架照片路径
        book_key: 要校准的书籍关键词（如果为None，显示所有书籍）
        """
        self.image_path = image_path
        self.book_key = book_key
        self.db = BookDatabase()
        
        # 加载图片
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"无法加载图片: {image_path}")
        
        self.display_image = self.original_image.copy()
        self.width = self.original_image.shape[1]
        self.height = self.original_image.shape[0]
        
        # 当前选中的书籍
        self.current_book = None
        self.books_to_calibrate = []
        
        # 鼠标状态
        self.drawing = False
        self.start_point = None
        self.end_point = None
        
        print(f"📸 图片尺寸: {self.width}x{self.height}")
        print("\n使用说明:")
        print("1. 点击并拖拽选择书籍位置（红色框）")
        print("2. 按 's' 保存当前书籍的位置")
        print("3. 按 'n' 下一个书籍")
        print("4. 按 'p' 上一个书籍")
        print("5. 按 'q' 退出并保存")
        print("6. 按 'r' 重置当前选择")
    
    def get_books_list(self):
        """获取要校准的书籍列表"""
        all_books = self.db.get_all_books()
        if self.book_key:
            # 支持部分匹配
            matching_books = []
            book_key_lower = self.book_key.lower()
            
            # 精确匹配
            if book_key_lower in all_books:
                matching_books.append(book_key_lower)
            else:
                # 部分匹配
                for key in all_books.keys():
                    if book_key_lower in key or key in book_key_lower:
                        matching_books.append(key)
            
            if matching_books:
                print(f"✅ 找到匹配的书籍: {matching_books}")
                return matching_books
            else:
                print(f"⚠️  未找到匹配的书籍 '{self.book_key}'")
                print(f"   可用的书籍关键词:")
                for i, key in enumerate(list(all_books.keys())[:10], 1):
                    print(f"   {i}. {key}")
                if len(all_books) > 10:
                    print(f"   ... 还有 {len(all_books) - 10} 本书")
                return []
        else:
            # 校准所有书籍
            return list(all_books.keys())
    
    def normalize_position(self, x1, y1, x2, y2):
        """
        将像素坐标转换为归一化坐标 (0-1)
        返回: (center_x, center_y, width, height)
        """
        # 确保坐标顺序正确
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
    
    def pixel_to_normalized(self, x, y, w, h):
        """将像素坐标转换为归一化坐标"""
        return (
            x / self.width,
            y / self.height,
            w / self.width,
            h / self.height
        )
    
    def normalized_to_pixel(self, pos):
        """将归一化坐标转换为像素坐标"""
        x, y, w, h = pos
        px = int(x * self.width)
        py = int(y * self.height)
        pw = int(w * self.width)
        ph = int(h * self.height)
        return (px, py, pw, ph)
    
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        # 调整坐标（如果图片被缩放显示）
        if hasattr(self, 'display_scale') and self.display_scale < 1.0:
            x = int(x / self.display_scale)
            y = int(y / self.display_scale)
            x = min(x, self.width - 1)
            y = min(y, self.height - 1)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            print(f"开始选择: ({x}, {y})")
            self.update_display()
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                self.update_display()
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)
            print(f"结束选择: ({x}, {y})")
            if self.start_point and self.end_point:
                x1, y1 = self.start_point
                x2, y2 = self.end_point
                pos = self.normalize_position(x1, y1, x2, y2)
                print(f"归一化坐标: {pos}")
            self.update_display()
    
    def update_display(self):
        """更新显示"""
        # 从原始图片开始
        self.display_image = self.original_image.copy()
        
        # 显示所有已校准的书籍位置（绿色）
        all_books = self.db.get_all_books()
        for key, info in all_books.items():
            if key != self.current_book:
                px, py, pw, ph = self.normalized_to_pixel(info['position'])
                x1 = px - pw // 2
                y1 = py - ph // 2
                x2 = px + pw // 2
                y2 = py + ph // 2
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 显示书名
                cv2.putText(self.display_image, key, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 显示当前选中的书籍位置（蓝色，如果已存在）
        if self.current_book and self.current_book in all_books:
            px, py, pw, ph = self.normalized_to_pixel(all_books[self.current_book]['position'])
            x1 = px - pw // 2
            y1 = py - ph // 2
            x2 = px + pw // 2
            y2 = py + ph // 2
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # 显示当前正在绘制的选择框（红色）
        if self.start_point and self.end_point:
            cv2.rectangle(self.display_image, self.start_point, self.end_point, (0, 0, 255), 2)
        
        # 显示当前书籍信息
        if self.current_book:
            book_info = all_books.get(self.current_book, {})
            info_text = f"当前书籍: {self.current_book}"
            if book_info:
                pos = book_info['position']
                info_text += f" | 位置: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}, {pos[3]:.3f})"
            cv2.putText(self.display_image, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示操作提示
        cv2.putText(self.display_image, "Click & Drag: Select | 's': Save | 'n': Next | 'q': Quit",
                   (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 调整窗口大小以适应屏幕
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
        
        cv2.imshow('Book Position Calibrator', display_img)
    
    def save_position(self):
        """保存当前选择的位置"""
        if not self.start_point or not self.end_point:
            print("❌ 请先选择书籍位置")
            return False
        
        if not self.current_book:
            print("❌ 没有选中的书籍")
            return False
        
        # 转换为归一化坐标
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        pos = self.normalize_position(x1, y1, x2, y2)
        
        # 更新数据库
        book_info = self.db.books[self.current_book]
        book_info['position'] = pos
        
        print(f"✅ 已保存 '{self.current_book}' 的位置: {pos}")
        return True
    
    def run(self):
        """运行校准工具"""
        # 获取书籍列表
        self.books_to_calibrate = self.get_books_list()
        if not self.books_to_calibrate:
            print("❌ 没有要校准的书籍")
            return
        
        print(f"\n📚 找到 {len(self.books_to_calibrate)} 本书需要校准")
        
        # 创建窗口
        window_name = 'Book Position Calibrator'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # 设置窗口属性，确保可以交互
        try:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        except:
            pass
        
        # 从第一本书开始
        book_index = 0
        self.current_book = self.books_to_calibrate[book_index]
        
        print(f"\n当前书籍: {self.current_book}")
        print("请点击并拖拽选择书籍位置...")
        print("提示: 确保窗口获得焦点，然后点击图片开始拖拽")
        
        self.update_display()
        
        # 确保窗口显示
        cv2.waitKey(100)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                # 保存所有更改
                print("\n保存更改...")
                self.save_to_file()
                break
            
            elif key == ord('s'):
                # 保存当前位置
                if self.save_position():
                    self.update_display()
            
            elif key == ord('n'):
                # 下一个书籍
                if self.save_position():
                    book_index = (book_index + 1) % len(self.books_to_calibrate)
                    self.current_book = self.books_to_calibrate[book_index]
                    self.start_point = None
                    self.end_point = None
                    print(f"\n当前书籍: {self.current_book}")
                    self.update_display()
            
            elif key == ord('p'):
                # 上一个书籍
                if self.save_position():
                    book_index = (book_index - 1) % len(self.books_to_calibrate)
                    self.current_book = self.books_to_calibrate[book_index]
                    self.start_point = None
                    self.end_point = None
                    print(f"\n当前书籍: {self.current_book}")
                    self.update_display()
            
            elif key == ord('r'):
                # 重置当前选择
                self.start_point = None
                self.end_point = None
                self.update_display()
            
            self.update_display()
        
        cv2.destroyAllWindows()
        print("✅ 校准完成！")
    
    def save_to_file(self):
        """保存到文件"""
        print("\n" + "="*60)
        print("校准后的书籍位置坐标:")
        print("="*60)
        
        all_books = self.db.get_all_books()
        for key in self.books_to_calibrate:
            if key in all_books:
                pos = all_books[key]['position']
                print(f'\n"{key}": {{')
                print(f'    "position": ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f}),')
                print(f'    "shelf": {all_books[key]["shelf"]},')
                print(f'    "full_name": "{all_books[key]["full_name"]}"')
                print('},')
        
        print("="*60)
        print("\n📝 请将上面的坐标复制到 book_database.py 文件中")
        print("   或者使用以下命令查看所有坐标:")
        print("   python3 save_calibration.py")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 calibrate_positions.py <图片路径> [书籍关键词]")
        print("示例: python3 calibrate_positions.py bookshelf.jpg")
        print("示例: python3 calibrate_positions.py bookshelf.jpg rethinking")
        return
    
    image_path = sys.argv[1]
    book_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    try:
        calibrator = PositionCalibrator(image_path, book_key)
        calibrator.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

