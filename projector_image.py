"""
投影仪图片显示模块
在书架照片上高亮显示找到的书籍（白色高亮，其他地方变暗）
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import os

class ProjectorImage:
    def __init__(self, image_path: str, width=1920, height=1080, fullscreen=True):
        """
        初始化投影仪图片显示
        image_path: 书架照片路径
        width: 投影分辨率宽度
        height: 投影分辨率高度
        fullscreen: 是否全屏显示（投影仪模式）
        """
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.window_created = False
        self.window_name = 'Book Highlight - Projector'
        self.current_highlight = None
        self.highlight_duration = 5.0  # 高亮持续时间（秒）
        self.highlight_start_time = None
        
        # 加载原始图片
        self.original_image = None
        self.display_image = None
        
        if image_path and os.path.exists(image_path):
            self.load_image(image_path)
        else:
            print(f"⚠️  图片文件不存在: {image_path}")
            print("   将使用黑色背景")
            self.original_image = np.zeros((height, width, 3), dtype=np.uint8)
            self.display_image = self.original_image.copy()
    
    def load_image(self, image_path: str):
        """加载书架照片"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            # 调整图片大小以适应投影分辨率
            img_height, img_width = img.shape[:2]
            
            # 计算缩放比例，保持宽高比
            scale_w = self.width / img_width
            scale_h = self.height / img_height
            scale = min(scale_w, scale_h)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整大小
            img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # 创建黑色背景，将图片居中放置
            self.original_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            y_offset = (self.height - new_height) // 2
            x_offset = (self.width - new_width) // 2
            self.original_image[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = img_resized
            
            # 保存缩放和偏移信息，用于坐标转换
            self.scale_x = scale
            self.scale_y = scale
            self.offset_x = x_offset
            self.offset_y = y_offset
            
            self.display_image = self.original_image.copy()
            print(f"✅ 成功加载图片: {image_path}")
            print(f"   原始尺寸: {img_width}x{img_height}")
            print(f"   显示尺寸: {new_width}x{new_height} (居中)")
        except Exception as e:
            print(f"❌ 加载图片失败: {e}")
            self.original_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            self.display_image = self.original_image.copy()
    
    def _ensure_window(self):
        """确保窗口已创建（延迟创建）"""
        if not self.window_created:
            # 如果之前尝试失败过，不再重复尝试
            if hasattr(self, '_window_failed') and self._window_failed:
                return False
                
            try:
                # 创建全屏窗口（投影仪模式）
                cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                if self.fullscreen:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.resizeWindow(self.window_name, self.width, self.height)
                self.window_created = True
                print("✅ 投影窗口已创建（全屏模式）")
                return True
            except Exception as e:
                # 标记失败，避免重复尝试
                self._window_failed = True
                if not hasattr(self, '_error_printed'):
                    print(f"⚠️  无法创建OpenCV窗口: {e}")
                    print("   将使用文本输出模式")
                    self._error_printed = True
                return False
        return True
    
    def highlight_book(self, position: Tuple[float, float, float, float], 
                       book_name: str = "", highlight_text_only=True):
        """
        高亮显示书籍
        position: (x, y, width, height) 归一化坐标 (0-1)，相对于原始图片
        book_name: 书籍名称（可选）
        highlight_text_only: 是否只高亮文字区域（默认True）
        """
        import time
        
        # 转换为像素坐标（相对于显示图片）
        # 注意：position是相对于原始图片的归一化坐标
        # 需要转换为显示图片的像素坐标
        
        # 计算在显示图片中的位置
        img_height, img_width = self.original_image.shape[:2]
        
        # 如果图片被缩放和居中，需要调整坐标
        if hasattr(self, 'scale_x'):
            # 原始图片在显示区域中的实际尺寸
            display_img_width = int(img_width * self.scale_x)
            display_img_height = int(img_height * self.scale_y)
            
            # 将归一化坐标转换为显示图片中的像素坐标
            x = int(position[0] * display_img_width) + self.offset_x
            y = int(position[1] * display_img_height) + self.offset_y
            w = int(position[2] * display_img_width)
            h = int(position[3] * display_img_height)
        else:
            # 如果没有缩放信息，直接使用
            x = int(position[0] * self.width)
            y = int(position[1] * self.height)
            w = int(position[2] * self.width)
            h = int(position[3] * self.height)
        
        # 如果只高亮文字区域，缩小高亮范围
        if highlight_text_only:
            text_ratio = 0.65  # 文字区域占原区域的65%
            text_w = int(w * text_ratio)
            text_h = int(h * text_ratio)
            text_x = x + (w - text_w) // 2
            text_y = y + (h - text_h) // 3  # 稍微偏上
            
            x, y, w, h = text_x, text_y, text_w, text_h
        
        # 确保坐标在范围内
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        w = min(w, self.width - x)
        h = min(h, self.height - y)
        
        self.current_highlight = {
            'position': (x, y, w, h),
            'book_name': book_name,
            'start_time': time.time()
        }
        self.highlight_start_time = time.time()
    
    def clear_highlight(self):
        """清除高亮"""
        self.current_highlight = None
        self.highlight_start_time = None
    
    def update_display(self):
        """
        更新显示
        返回: 是否仍在显示高亮
        """
        import time
        
        # 确保窗口已创建
        if not self._ensure_window():
            # 如果窗口创建失败，使用文本输出
            if self.current_highlight is not None:
                current_time = time.time()
                elapsed = current_time - self.highlight_start_time
                if elapsed < self.highlight_duration:
                    if not hasattr(self, '_text_highlight_shown'):
                        book_name = self.current_highlight.get('book_name', '')
                        x, y, w, h = self.current_highlight['position']
                        print(f"\n{'='*60}")
                        print(f"📚 找到书籍: {book_name}")
                        print(f"📍 高亮位置: x={x}, y={y}, w={w}, h={h}")
                        print(f"{'='*60}\n")
                        self._text_highlight_shown = True
                    return True
                else:
                    self.clear_highlight()
                    if hasattr(self, '_text_highlight_shown'):
                        delattr(self, '_text_highlight_shown')
            return False
        
        # 从原始图片开始
        frame = self.original_image.copy()
        
        # 检查是否需要显示高亮
        if self.current_highlight is not None:
            current_time = time.time()
            elapsed = current_time - self.highlight_start_time
            
            # 如果还在显示时间内
            if elapsed < self.highlight_duration:
                x, y, w, h = self.current_highlight['position']
                book_name = self.current_highlight['book_name']
                
                # 创建遮罩：其他地方变暗（黑色半透明）
                overlay = frame.copy()
                
                # 将整个图片变暗
                overlay = cv2.addWeighted(overlay, 0.2, np.zeros_like(overlay), 0.8, 0)
                
                # 高亮区域保持原样（白色高亮）
                # 提取高亮区域
                highlight_region = frame[y:y+h, x:x+w].copy()
                
                # 将高亮区域变为白色（或保持原样但更亮）
                # 创建白色高亮效果
                white_highlight = np.ones((h, w, 3), dtype=np.uint8) * 255
                
                # 混合：70%白色 + 30%原图（让书籍内容可见）
                highlight_region = cv2.addWeighted(highlight_region, 0.3, white_highlight, 0.7, 0)
                
                # 将高亮区域放回
                overlay[y:y+h, x:x+w] = highlight_region
                
                # 绘制白色边框（更明显）
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), 6)
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), 2)
                
                # 显示书名（如果有）
                if book_name:
                    # 计算文字位置（在矩形上方）
                    text_y = max(40, y - 20)
                    text_x = x
                    
                    # 绘制文字背景（黑色半透明）
                    (text_width, text_height), baseline = cv2.getTextSize(
                        book_name, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3
                    )
                    text_bg = overlay.copy()
                    cv2.rectangle(
                        text_bg,
                        (text_x - 10, text_y - text_height - 10),
                        (text_x + text_width + 10, text_y + baseline + 10),
                        (0, 0, 0),
                        -1
                    )
                    overlay = cv2.addWeighted(overlay, 0.5, text_bg, 0.5, 0)
                    
                    # 绘制文字（白色）
                    cv2.putText(
                        overlay,
                        book_name,
                        (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (255, 255, 255),
                        3,
                        cv2.LINE_AA
                    )
                
                frame = overlay
                
                # 显示帧
                try:
                    cv2.imshow(self.window_name, frame)
                    return True
                except Exception as e:
                    print(f"警告: 无法更新显示: {e}")
                    return False
            else:
                # 超时，清除高亮
                self.clear_highlight()
        
        # 显示原始图片（没有高亮时）
        try:
            cv2.imshow(self.window_name, frame)
        except Exception as e:
            print(f"警告: 无法更新显示: {e}")
            self.window_created = False
        
        return False
    
    def run(self, stop_event=None):
        """
        运行显示循环（在后台线程中运行）
        stop_event: 停止事件（threading.Event）
        """
        import time
        
        if stop_event is None:
            import threading
            stop_event = threading.Event()
        
        window_opened = False
        
        while not stop_event.is_set():
            self.update_display()
            
            if self.window_created:
                if not window_opened:
                    print("📺 投影窗口已打开（全屏模式）")
                    print("   按 'q' 或 ESC 键可关闭窗口")
                    window_opened = True
                
                try:
                    # 使用非阻塞方式检查按键
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' 或 ESC 键
                        print("关闭投影窗口")
                        try:
                            cv2.destroyAllWindows()
                        except:
                            pass
                        self.window_created = False
                        break
                except Exception as e:
                    print(f"窗口操作错误: {e}")
                    self.window_created = False
            else:
                time.sleep(0.1)
            
            time.sleep(0.03)  # 约30 FPS
        
        # 清理
        if self.window_created:
            cv2.destroyAllWindows()
    
    def __del__(self):
        """清理资源"""
        cv2.destroyAllWindows()

