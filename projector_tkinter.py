"""
使用Tkinter的投影仪显示模块（更可靠的GUI方案）
在书架照片上高亮显示找到的书籍
"""

try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
    import numpy as np
    import cv2
    TKINTER_AVAILABLE = True
except ImportError as e:
    TKINTER_AVAILABLE = False
    print(f"Tkinter不可用: {e}")

class ProjectorTkinter:
    def __init__(self, image_path: str, width=1920, height=1080):
        """
        初始化Tkinter投影显示
        image_path: 书架照片路径
        width: 窗口宽度
        height: 窗口高度
        """
        if not TKINTER_AVAILABLE:
            raise ImportError("Tkinter不可用")
        
        self.image_path = image_path
        self.width = width
        self.height = height
        self.current_highlight = None
        self.highlight_duration = 5.0
        self.highlight_start_time = None
        
        # 加载图片
        self.original_image = None
        self.display_image = None
        self.photo = None
        
        if image_path:
            self.load_image(image_path)
        
        # 窗口将在run方法中创建
        self.root = None
        self.canvas = None
        self.running = False
    
    def load_image(self, image_path: str):
        """加载图片"""
        try:
            # 使用OpenCV加载
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            print(f"📸 原始图片尺寸: {img.shape[1]}x{img.shape[0]}")
            
            # 转换为RGB（OpenCV使用BGR）
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 调整大小以适应窗口
            img_height, img_width = img_rgb.shape[:2]
            scale_w = self.width / img_width
            scale_h = self.height / img_height
            scale = min(scale_w, scale_h)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            print(f"📐 缩放后尺寸: {new_width}x{new_height}, 缩放比例: {scale:.2f}")
            
            img_resized = cv2.resize(img_rgb, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # 创建黑色背景
            self.original_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            y_offset = (self.height - new_height) // 2
            x_offset = (self.width - new_width) // 2
            
            print(f"📍 图片位置: x={x_offset}, y={y_offset}")
            
            # 确保索引在范围内
            y_end = min(y_offset + new_height, self.height)
            x_end = min(x_offset + new_width, self.width)
            actual_h = y_end - y_offset
            actual_w = x_end - x_offset
            
            self.original_image[y_offset:y_end, x_offset:x_end] = img_resized[:actual_h, :actual_w]
            
            self.scale_x = scale
            self.scale_y = scale
            self.offset_x = x_offset
            self.offset_y = y_offset
            
            self.display_image = self.original_image.copy()
            print(f"✅ 成功加载图片: {image_path}")
            print(f"   显示区域: {self.width}x{self.height}")
        except Exception as e:
            import traceback
            print(f"❌ 加载图片失败: {e}")
            traceback.print_exc()
            # 创建黑色背景
            self.original_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            self.display_image = self.original_image.copy()
    
    def highlight_book(self, position, book_name="", highlight_text_only=True):
        """高亮显示书籍"""
        import time
        
        # 转换坐标
        if hasattr(self, 'scale_x'):
            display_img_width = int(self.width * self.scale_x / self.width * self.width)
            display_img_height = int(self.height * self.scale_y / self.height * self.height)
            x = int(position[0] * display_img_width) + self.offset_x
            y = int(position[1] * display_img_height) + self.offset_y
            w = int(position[2] * display_img_width)
            h = int(position[3] * display_img_height)
        else:
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
            text_y = y + (h - text_h) // 3  # 稍微偏上，因为文字通常在书籍上部
            
            x, y, w, h = text_x, text_y, text_w, text_h
        
        self.current_highlight = {
            'position': (x, y, w, h),
            'book_name': book_name,
            'start_time': time.time()
        }
        self.highlight_start_time = time.time()
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        import time
        
        if self.canvas is None or self.original_image is None:
            return
        
        # 从原始图片开始
        frame = self.original_image.copy()
        
        if self.current_highlight:
            current_time = time.time()
            elapsed = current_time - self.highlight_start_time
            
            if elapsed < self.highlight_duration:
                x, y, w, h = self.current_highlight['position']
                
                # 变暗其他区域
                overlay = frame.copy()
                overlay = (overlay * 0.2).astype(np.uint8)
                
                # 高亮区域（白色）
                highlight_region = frame[y:y+h, x:x+w].copy()
                white_highlight = np.ones((h, w, 3), dtype=np.uint8) * 255
                highlight_region = (highlight_region * 0.3 + white_highlight * 0.7).astype(np.uint8)
                overlay[y:y+h, x:x+w] = highlight_region
                
                # 白色边框
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 255), 6)
                
                frame = overlay
        
        # 确保frame是uint8类型
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        # 转换为RGB（PIL需要RGB格式）
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            # 已经是RGB格式（之前已经转换过）
            frame_rgb = frame
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL Image
        try:
            pil_image = Image.fromarray(frame_rgb)
            # 调整大小以适应窗口（如果需要）
            pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image=pil_image)
            
            # 更新canvas
            self.canvas.delete("all")
            # 居中显示图片
            self.canvas.create_image(self.width//2, self.height//2, image=self.photo, anchor=tk.CENTER)
            
            # 如果有高亮，绘制书名
            if self.current_highlight:
                current_time = time.time()
                elapsed = current_time - self.highlight_start_time
                if elapsed < self.highlight_duration:
                    book_name = self.current_highlight.get('book_name', '')
                    if book_name:
                        x, y, w, h = self.current_highlight['position']
                        text_x = x
                        text_y = max(40, y - 20)
                        self.canvas.create_text(
                            text_x, text_y,
                            text=book_name,
                            fill='white',
                            font=('Arial', 24, 'bold'),
                            anchor='nw'
                        )
        except Exception as e:
            print(f"更新显示错误: {e}")
            # 如果出错，至少显示一个黑色背景
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill='black')
    
    def _create_window_main_thread(self, stop_event=None):
        """在主线程中创建窗口（非阻塞模式）"""
        import time
        
        if stop_event is None:
            import threading
            stop_event = threading.Event()
        
        # 创建窗口（必须在主线程）
        self.root = tk.Tk()
        self.root.title("Book Highlight - Projector")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # 创建canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定退出键
        self.root.bind('<Escape>', lambda e: self._close_window())
        self.root.bind('<q>', lambda e: self._close_window())
        
        self.running = True
        self.stop_event = stop_event
        print("✅ Tkinter投影窗口已创建（全屏模式）")
        print("   按 ESC 或 q 键关闭窗口")
        
        # 初始显示
        self.update_display()
        
        # 使用after方法定期更新（非阻塞）
        self._schedule_update()
    
    def _schedule_update(self):
        """安排下一次更新"""
        if self.running and (not self.stop_event or not self.stop_event.is_set()):
            self.update_display()
            self.root.after(30, self._schedule_update)  # 约30 FPS
        else:
            self._close_window()
    
    def _close_window(self):
        """关闭窗口"""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
    
    def run(self, stop_event=None):
        """运行显示循环（必须在主线程调用）"""
        self._create_window_main_thread(stop_event)
        # 非阻塞主循环
        try:
            while self.running and (not stop_event or not stop_event.is_set()):
                self.root.update_idletasks()
                self.root.update()
                import time
                time.sleep(0.01)  # 短暂休眠，避免CPU占用过高
        except:
            pass
        finally:
            self._close_window()

