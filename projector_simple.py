"""
简单的投影显示方案：保存高亮图片到文件
用户可以用任何图片查看器打开并全屏显示
"""

import cv2
import numpy as np
import os
from typing import Tuple

class ProjectorSimple:
    def __init__(self, image_path: str, output_dir="./projector_output"):
        """
        初始化简单投影显示
        image_path: 书架照片路径
        output_dir: 输出目录
        """
        self.image_path = image_path
        self.output_dir = output_dir
        self.current_highlight = None
        self.highlight_duration = 5.0
        self.highlight_start_time = None
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 加载原始图片
        self.original_image = None
        self.load_image(image_path)
        
        print(f"✅ 简单投影模式已初始化")
        print(f"   高亮图片将保存到: {output_dir}/highlight.jpg")
        print(f"   可以用任何图片查看器打开并全屏显示")
    
    def load_image(self, image_path: str):
        """加载图片"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            print(f"📸 原始图片尺寸: {img.shape[1]}x{img.shape[0]}")
            
            # 保持原始尺寸（或调整到合适大小）
            # 投影仪通常是1920x1080，但我们可以保持原图比例
            self.original_image = img.copy()
            self.width = img.shape[1]
            self.height = img.shape[0]
            
            print(f"✅ 成功加载图片: {image_path}")
        except Exception as e:
            print(f"❌ 加载图片失败: {e}")
            self.original_image = None
    
    def highlight_book(self, position: Tuple[float, float, float, float], 
                       book_name: str = ""):
        """
        高亮显示书籍并保存图片
        position: (x, y, width, height) 归一化坐标 (0-1)
        book_name: 书籍名称
        """
        import time
        
        if self.original_image is None:
            print("❌ 图片未加载")
            return
        
        # 转换为像素坐标
        x = int(position[0] * self.width)
        y = int(position[1] * self.height)
        w = int(position[2] * self.width)
        h = int(position[3] * self.height)
        
        # 只高亮文字区域（缩小到65%，并稍微偏上）
        text_ratio = 0.65  # 文字区域占原区域的65%
        text_w = int(w * text_ratio)
        text_h = int(h * text_ratio)
        text_x = x + (w - text_w) // 2  # 居中
        text_y = y + (h - text_h) // 3  # 稍微偏上，因为文字通常在书籍上部
        
        # 确保坐标在范围内
        text_x = max(0, min(text_x, self.width - 1))
        text_y = max(0, min(text_y, self.height - 1))
        text_w = min(text_w, self.width - text_x)
        text_h = min(text_h, self.height - text_y)
        
        # 使用文字区域的坐标
        x, y, w, h = text_x, text_y, text_w, text_h
        
        # 创建显示图片
        frame = self.original_image.copy()
        
        # 变暗其他区域
        overlay = frame.copy()
        overlay = cv2.addWeighted(overlay, 0.2, np.zeros_like(overlay), 0.8, 0)
        
        # 高亮文字区域（白色）
        highlight_region = frame[y:y+h, x:x+w].copy()
        white_highlight = np.ones((h, w, 3), dtype=np.uint8) * 255
        highlight_region = cv2.addWeighted(highlight_region, 0.3, white_highlight, 0.7, 0)
        overlay[y:y+h, x:x+w] = highlight_region
        
        # 白色边框（只围绕文字区域）
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), 6)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), 2)
        
        # 显示书名
        if book_name:
            # 计算文字位置
            text_y = max(40, y - 20)
            text_x = x
            
            # 绘制文字背景
            (text_width, text_height), baseline = cv2.getTextSize(
                book_name, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3
            )
            cv2.rectangle(
                overlay,
                (text_x - 10, text_y - text_height - 10),
                (text_x + text_width + 10, text_y + baseline + 10),
                (0, 0, 0),
                -1
            )
            
            # 绘制文字（白色）
            cv2.putText(
                overlay,
                book_name,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (255, 255, 255),
                3,
                cv2.LINE_AA
            )
        
        frame = overlay
        
        # 保存图片
        output_path = os.path.join(self.output_dir, "highlight.jpg")
        cv2.imwrite(output_path, frame)
        
        print(f"\n{'='*60}")
        print(f"📚 找到书籍: {book_name}")
        print(f"✅ 高亮图片已保存: {output_path}")
        print(f"   请用图片查看器打开并全屏显示（按F键全屏）")
        print(f"{'='*60}\n")
        
        # 尝试自动打开（macOS）
        try:
            import subprocess
            subprocess.run(['open', output_path], check=False)
            print("   已自动打开图片查看器")
        except:
            pass
        
        self.current_highlight = {
            'position': (x, y, w, h),
            'book_name': book_name,
            'start_time': time.time()
        }
        self.highlight_start_time = time.time()
    
    def clear_highlight(self):
        """清除高亮，恢复原图"""
        if self.original_image is not None:
            output_path = os.path.join(self.output_dir, "highlight.jpg")
            cv2.imwrite(output_path, self.original_image)
            print("📸 已恢复原图")
        self.current_highlight = None
    
    def run(self, stop_event=None):
        """运行（简单模式不需要持续运行）"""
        pass
    
    def update_display(self):
        """更新显示（简单模式不需要）"""
        pass

