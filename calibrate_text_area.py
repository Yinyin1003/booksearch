#!/usr/bin/env python3
"""
文字区域校准工具
直接选择书籍的文字区域，保存后直接用于高亮显示
"""

import cv2
import numpy as np
import re
import sys
from book_database import BookDatabase

class TextAreaCalibrator:
    def __init__(self, image_path, book_key=None):
        """初始化文字区域校准工具"""
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
        
        # 书籍列表
        if book_key:
            # 检查是否支持部分匹配
            matching_books = [k for k in self.db.books.keys() if book_key.lower() in k.lower()]
            if matching_books:
                self.books_to_calibrate = matching_books
                print(f"✅ 找到匹配的书籍: {matching_books}")
            else:
                print(f"❌ 未找到匹配的书籍: {book_key}")
                print("可用书籍:")
                for k in list(self.db.books.keys())[:10]:
                    print(f"  - {k}")
                sys.exit(1)
        else:
            self.books_to_calibrate = list(self.db.books.keys())
        
        self.current_book_index = 0
        self.current_book = self.books_to_calibrate[0]
        
        # 已校准的书籍（存储文字区域的坐标）
        self.calibrated = {}
        
        print(f"\n📸 图片尺寸: {self.width}x{self.height}")
        print(f"📚 需要校准 {len(self.books_to_calibrate)} 本书")
        print("\n" + "="*60)
        print("🎯 重要提示：")
        print("="*60)
        print("请直接选择书籍的**文字区域**（书名部分）")
        print("不要选择整本书，只选择能看到文字的部分")
        print("="*60)
        print("\n操作说明:")
        print("  1. 点击并拖拽选择文字区域（红色框）")
        print("  2. 按 's' 保存当前文字区域")
        print("  3. 按 'n' 下一本书")
        print("  4. 按 'p' 上一本书")
        print("  5. 按 'r' 重置当前选择")
        print("  6. 按 'q' 保存所有更改并退出")
        print("="*60)
        print(f"\n当前书籍: {self.current_book}")
        print(f"  完整书名: {self.db.books[self.current_book]['full_name']}")
        
        # 创建窗口
        cv2.namedWindow('Text Area Calibrator', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Text Area Calibrator', self.mouse_callback)
        
        # 调整窗口大小
        max_width = 1920
        max_height = 1080
        scale = min(max_width / self.width, max_height / self.height, 1.0)
        self.display_scale = scale
        
        if scale < 1.0:
            display_width = int(self.width * scale)
            display_height = int(self.height * scale)
            cv2.resizeWindow('Text Area Calibrator', display_width, display_height)
        else:
            self.display_scale = 1.0
    
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
            print(f"开始选择文字区域: ({x}, {y})")
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
        self.display_image = self.original_image.copy()
        
        # 显示当前书籍信息
        book_info = self.db.books[self.current_book]
        info_text = f"Book: {self.current_book} ({self.current_book_index + 1}/{len(self.books_to_calibrate)})"
        cv2.putText(self.display_image, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # 显示完整书名
        full_name = book_info['full_name']
        # 如果书名太长，截断
        if len(full_name) > 50:
            full_name = full_name[:47] + "..."
        cv2.putText(self.display_image, full_name, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示当前选择（红色框）
        if self.start_point and self.end_point:
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # 显示坐标信息
            pos = self.normalize_position(x1, y1, x2, y2)
            coord_text = f"Area: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}, {pos[3]:.4f})"
            cv2.putText(self.display_image, coord_text, (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 显示已保存的文字区域（绿色框）
        if self.current_book in self.calibrated:
            pos = self.calibrated[self.current_book]
            center_x = int(pos[0] * self.width)
            center_y = int(pos[1] * self.height)
            w = int(pos[2] * self.width)
            h = int(pos[3] * self.height)
            x = center_x - w // 2
            y = center_y - h // 2
            cv2.rectangle(self.display_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(self.display_image, "Saved", (x, max(30, y - 10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 显示操作提示
        cv2.putText(self.display_image, 
                   "Click & Drag: Select Text Area | 's': Save | 'n': Next | 'p': Prev | 'q': Quit",
                   (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 调整窗口大小以适应屏幕
        if hasattr(self, 'display_scale') and self.display_scale < 1.0:
            display_width = int(self.width * self.display_scale)
            display_height = int(self.height * self.display_scale)
            display_img = cv2.resize(self.display_image, (display_width, display_height))
        else:
            display_img = self.display_image
        
        cv2.imshow('Text Area Calibrator', display_img)
    
    def save_position(self):
        """保存当前选择的文字区域"""
        if not self.start_point or not self.end_point:
            print("❌ 请先选择文字区域")
            return False
        
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        # 转换为归一化坐标
        pos = self.normalize_position(x1, y1, x2, y2)
        
        # 保存到校准字典
        self.calibrated[self.current_book] = pos
        
        print(f"✅ 已保存 '{self.current_book}' 的文字区域: {pos}")
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
                    print(f"✅ 已更新 '{book_key}' 的文字区域位置")
                else:
                    # 尝试更精确的匹配
                    pattern2 = rf'("{re.escape(book_key)}"\s*:\s*{{[^}}]*"position":\s*)[^,)]+[^)]*\)'
                    replacement2 = rf'\1{pos_str}'
                    new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
                    if new_content != content:
                        content = new_content
                        print(f"✅ 已更新 '{book_key}' 的文字区域位置")
                    else:
                        print(f"⚠️  无法找到 '{book_key}' 的位置定义，请手动更新")
            
            # 保存文件
            with open(db_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ 所有更改已保存到 {db_file}")
            print(f"   共更新了 {len(self.calibrated)} 本书的文字区域位置")
            print(f"\n💡 提示：现在这些坐标直接指向文字区域，不需要再做缩小计算")
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """运行校准工具"""
        self.update_display()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_position()
                self.update_display()
            elif key == ord('n'):
                self.current_book_index = (self.current_book_index + 1) % len(self.books_to_calibrate)
                self.current_book = self.books_to_calibrate[self.current_book_index]
                self.start_point = None
                self.end_point = None
                print(f"\n切换到: {self.current_book}")
                print(f"  完整书名: {self.db.books[self.current_book]['full_name']}")
                self.update_display()
            elif key == ord('p'):
                self.current_book_index = (self.current_book_index - 1) % len(self.books_to_calibrate)
                self.current_book = self.books_to_calibrate[self.current_book_index]
                self.start_point = None
                self.end_point = None
                print(f"\n切换到: {self.current_book}")
                print(f"  完整书名: {self.db.books[self.current_book]['full_name']}")
                self.update_display()
            elif key == ord('r'):
                self.start_point = None
                self.end_point = None
                print("重置选择")
                self.update_display()
        
        cv2.destroyAllWindows()
        
        # 保存到文件
        if self.calibrated:
            print("\n" + "="*60)
            save = input("是否保存所有更改到 book_database.py? (y/n): ").strip().lower()
            if save == 'y':
                self.save_to_file()
            else:
                print("未保存更改")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 calibrate_text_area.py <图片路径> [书籍关键词]")
        print("示例: python3 calibrate_text_area.py bookshelf.jpg")
        print("示例: python3 calibrate_text_area.py bookshelf.jpg 'lean impact'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    book_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        calibrator = TextAreaCalibrator(image_path, book_key)
        calibrator.run()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

