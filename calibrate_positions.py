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
        
        # 记录已修改的书籍（用于保存时只保存修改过的）
        self.modified_books = set()
        
        # 鼠标状态
        self.drawing = False
        self.start_point = None
        self.end_point = None
        
        # 旋转矩形模式：使用4个点定义旋转矩形
        self.rotation_mode = False  # False=普通矩形, True=旋转矩形（4点模式）
        self.rotation_points = []  # 存储4个角点
        
        print(f"📸 图片尺寸: {self.width}x{self.height}")
        print("\n使用说明:")
        print("【普通模式（默认）】:")
        print("  1. 点击并拖拽选择书籍位置（红色框）")
        print("  2. 按 's' 保存当前书籍的位置")
        print("  3. 按 'n' 下一个书籍")
        print("  4. 按 'p' 上一个书籍")
        print("  5. 按 'q' 退出并保存")
        print("  6. 按 'r' 重置当前选择")
        print("\n【旋转矩形模式（支持倾斜）】:")
        print("  1. 按 't' 切换到旋转矩形模式")
        print("  2. 依次点击4个角点（左上、右上、右下、左下）")
        print("  3. 按 's' 保存位置")
        print("  4. 按 't' 切换回普通模式")
    
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
    
    def normalize_rotated_position(self, points):
        """
        将旋转矩形的4个角点转换为归一化坐标
        返回: (center_x, center_y, width, height, angle)
        angle: 旋转角度（度）
        """
        if len(points) != 4:
            raise ValueError("需要4个点来定义旋转矩形")
        
        # 计算中心点
        center_x = sum(p[0] for p in points) / 4.0 / self.width
        center_y = sum(p[1] for p in points) / 4.0 / self.height
        
        # 计算宽度和高度（使用对角线的平均值）
        import math
        # 计算相邻两点的距离
        dist1 = math.sqrt((points[0][0] - points[1][0])**2 + (points[0][1] - points[1][1])**2)
        dist2 = math.sqrt((points[1][0] - points[2][0])**2 + (points[1][1] - points[2][1])**2)
        
        width = max(dist1, dist2) / self.width
        height = min(dist1, dist2) / self.height
        
        # 计算旋转角度（使用第一条边）
        dx = points[1][0] - points[0][0]
        dy = points[1][1] - points[0][1]
        angle = math.degrees(math.atan2(dy, dx))
        
        return (center_x, center_y, width, height, angle)
    
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
        
        if self.rotation_mode:
            # 旋转矩形模式：点击4个角点
            if event == cv2.EVENT_LBUTTONDOWN:
                # 如果已经有4个点，重置
                if len(self.rotation_points) >= 4:
                    print("🔄 重置，重新选择4个点")
                    self.rotation_points = []
                self.rotation_points.append((x, y))
                print(f"点 {len(self.rotation_points)}: ({x}, {y})")
                if len(self.rotation_points) >= 4:
                    print("✅ 已收集4个角点，可以按 's' 保存")
                self.update_display()
        else:
            # 普通模式：拖拽选择矩形
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
        if self.rotation_mode:
            # 旋转矩形模式：显示4个角点
            if len(self.rotation_points) > 0:
                for i, pt in enumerate(self.rotation_points):
                    cv2.circle(self.display_image, pt, 5, (0, 0, 255), -1)
                    cv2.putText(self.display_image, str(i+1), (pt[0]+10, pt[1]), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # 如果有点，绘制连线
                if len(self.rotation_points) >= 2:
                    for i in range(len(self.rotation_points)):
                        pt1 = self.rotation_points[i]
                        pt2 = self.rotation_points[(i+1) % len(self.rotation_points)]
                        cv2.line(self.display_image, pt1, pt2, (0, 0, 255), 2)
                # 如果4个点都有了，绘制完整矩形
                if len(self.rotation_points) == 4:
                    pts = np.array(self.rotation_points, np.int32)
                    cv2.polylines(self.display_image, [pts], True, (0, 0, 255), 2)
        elif self.start_point and self.end_point:
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
        if self.rotation_mode:
            mode_text = f"旋转模式 | 已选点: {len(self.rotation_points)}/4 | 's': Save | 't': 切换模式 | 'r': 重置 | 'q': Quit"
        else:
            mode_text = "普通模式 | Click & Drag: Select | 's': Save | 't': 旋转模式 | 'n': Next | 'q': Quit"
        cv2.putText(self.display_image, mode_text,
                   (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
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
        # 确保窗口在前台显示
        try:
            cv2.setWindowProperty('Book Position Calibrator', cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty('Book Position Calibrator', cv2.WND_PROP_TOPMOST, 0)
        except:
            pass
    
    def save_position(self):
        """保存当前选择的位置"""
        if not self.current_book:
            print("❌ 没有选中的书籍")
            return False
        
        if self.rotation_mode:
            # 旋转矩形模式
            print(f"\n📝 尝试保存旋转矩形位置...")
            print(f"   当前点数: {len(self.rotation_points)}")
            if len(self.rotation_points) != 4:
                print(f"❌ 旋转矩形模式需要4个角点，当前只有 {len(self.rotation_points)} 个")
                print("   请依次点击4个角点（左上、右上、右下、左下）")
                print("   提示：如果已经点击了4个点，请检查窗口是否获得焦点")
                return False
            
            try:
                # 转换为归一化坐标（包含角度）
                pos = self.normalize_rotated_position(self.rotation_points)
                print(f"✅ 旋转矩形位置: center=({pos[0]:.4f}, {pos[1]:.4f}), size=({pos[2]:.4f}, {pos[3]:.4f}), angle={pos[4]:.2f}°")
                
                # 注意：当前数据库格式只支持 (x, y, w, h)，不支持角度
                # 使用旋转矩形的轴对齐边界框（AABB）来保存
                # 计算4个点的边界框
                import math
                points_norm = [(p[0] / self.width, p[1] / self.height) for p in self.rotation_points]
                x_coords = [p[0] for p in points_norm]
                y_coords = [p[1] for p in points_norm]
                
                x_min = min(x_coords)
                x_max = max(x_coords)
                y_min = min(y_coords)
                y_max = max(y_coords)
                
                # 计算中心点和尺寸
                center_x = (x_min + x_max) / 2.0
                center_y = (y_min + y_max) / 2.0
                w = x_max - x_min
                h = y_max - y_min
                
                pos_normalized = (center_x, center_y, w, h)
                print(f"   转换为边界框: center=({center_x:.4f}, {center_y:.4f}), size=({w:.4f}, {h:.4f})")
            except Exception as e:
                print(f"❌ 计算旋转矩形位置时出错: {e}")
                import traceback
                traceback.print_exc()
                return False
            
        else:
            # 普通矩形模式
            if not self.start_point or not self.end_point:
                print("❌ 请先选择书籍位置")
                return False
            
            # 转换为归一化坐标
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            pos_normalized = self.normalize_position(x1, y1, x2, y2)
        
        # 更新数据库
        book_info = self.db.books[self.current_book]
        old_pos = book_info['position']
        book_info['position'] = pos_normalized
        
        # 记录已修改的书籍
        self.modified_books.add(self.current_book)
        
        print(f"✅ 已保存 '{self.current_book}' 的位置: {pos_normalized}")
        print(f"   旧位置: {old_pos}")
        print(f"   新位置: {pos_normalized}")
        if self.rotation_mode:
            print(f"   旋转角度: {pos[4]:.2f}° (已转换为外接矩形)")
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
        print("💡 窗口应该已经显示，如果没有看到，请检查是否被其他窗口遮挡")
        
        self.update_display()
        
        # 确保窗口显示（多次尝试）
        for _ in range(5):
            cv2.waitKey(100)
            cv2.imshow(window_name, self.display_image)
        
        # 保存初始预览图片
        preview_path = os.path.join(os.path.dirname(self.image_path), 'calibration_preview.jpg')
        cv2.imwrite(preview_path, self.display_image)
        print(f"📸 预览图片已保存: {preview_path}")
        
        while True:
            # 持续更新显示
            self.update_display()
            
            key = cv2.waitKey(30) & 0xFF  # 增加等待时间，确保窗口响应
            
            if key == ord('q'):
                # 保存所有更改
                print("\n" + "="*60)
                print("退出并保存更改...")
                print("="*60)
                if self.modified_books:
                    print(f"📝 检测到 {len(self.modified_books)} 本书籍被修改:")
                    for book in self.modified_books:
                        print(f"   - {book}")
                else:
                    print("⚠️  警告：没有检测到任何修改！")
                    print("   提示：请确保在校准后按 's' 保存每个书籍的位置")
                self.save_to_file()
                # 保存最终预览图片
                final_preview_path = os.path.join(os.path.dirname(self.image_path), 'calibration_final.jpg')
                cv2.imwrite(final_preview_path, self.display_image)
                print(f"\n📸 最终预览图片已保存: {final_preview_path}")
                break
            
            elif key == ord('s'):
                # 保存当前位置
                print(f"\n按下了 's' 键，尝试保存...")
                print(f"   当前模式: {'旋转矩形' if self.rotation_mode else '普通矩形'}")
                print(f"   当前书籍: {self.current_book}")
                if self.rotation_mode:
                    print(f"   旋转点数: {len(self.rotation_points)}")
                else:
                    print(f"   选择框: {self.start_point} -> {self.end_point}")
                
                if self.save_position():
                    print("✅ 保存成功！")
                    self.update_display()
                else:
                    print("❌ 保存失败，请检查上面的错误信息")
            
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
                if self.rotation_mode:
                    self.rotation_points = []
                    print("🔄 已重置旋转矩形的点")
                else:
                    self.start_point = None
                    self.end_point = None
                    print("🔄 已重置选择")
                self.update_display()
            
            elif key == ord('t'):
                # 切换旋转矩形模式
                self.rotation_mode = not self.rotation_mode
                if self.rotation_mode:
                    print("\n🔄 切换到旋转矩形模式")
                    print("   请依次点击4个角点（左上、右上、右下、左下）")
                    self.rotation_points = []
                    self.start_point = None
                    self.end_point = None
                else:
                    print("\n🔄 切换到普通矩形模式")
                    self.rotation_points = []
                self.update_display()
            
            self.update_display()
        
        cv2.destroyAllWindows()
        print("✅ 校准完成！")
    
    def save_to_file(self):
        """保存到文件（自动更新book_database.py）"""
        db_file = "book_database.py"
        if not os.path.exists(db_file):
            print(f"❌ 找不到文件: {db_file}")
            return
        
        print("\n" + "="*60)
        print("正在保存校准后的位置到文件...")
        print("="*60)
        
        # 读取文件
        with open(db_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 备份原文件
        backup_file = db_file + ".backup"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"📝 已备份原文件到: {backup_file}")
        
        # 更新每个校准的书籍位置
        import re
        updated_count = 0
        all_books = self.db.get_all_books()
        
        # 只保存实际修改过的书籍
        books_to_save = self.modified_books if self.modified_books else self.books_to_calibrate
        
        if not books_to_save:
            print("⚠️  没有修改任何书籍位置")
            return
        
        print(f"\n📝 准备保存 {len(books_to_save)} 本书籍的位置:")
        for book_key in books_to_save:
            print(f"   - {book_key}")
        
        for book_key in books_to_save:
            if book_key not in all_books:
                print(f"⚠️  跳过: {book_key}（不在数据库中）")
                continue
            
            position = all_books[book_key]['position']
            x, y, w, h = position
            new_position = f"({x:.4f}, {y:.4f}, {w:.4f}, {h:.4f})"
            
            # 查找并替换位置
            found = False
            for i, line in enumerate(lines):
                if f'"{book_key}"' in line and ':' in line and '{' in line:
                    # 在接下来的几行中查找position行
                    for j in range(i, min(i+10, len(lines))):
                        if '"position"' in lines[j]:
                            old_line = lines[j]
                            pattern = r'"position":\s*\([^)]+\)'
                            new_line = re.sub(pattern, f'"position": {new_position}', old_line)
                            if new_line != old_line:
                                lines[j] = new_line
                                updated_count += 1
                                found = True
                                print(f"✅ 更新: {book_key} -> {new_position}")
                            else:
                                print(f"ℹ️  跳过: {book_key}（位置未改变）")
                            break
                    break
            
            if not found:
                print(f"⚠️  未找到: {book_key}，可能需要手动更新")
        
        # 保存更新后的文件
        if updated_count > 0:
            with open(db_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n✅ 已更新 {updated_count} 本书籍的位置到 {db_file}")
            print("   请重启主程序以使用新位置")
        else:
            print("⚠️  没有更新任何书籍位置")

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

