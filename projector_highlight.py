"""
投影仪高亮显示模块
使用OpenCV在投影区域显示高亮框
"""

import cv2
import numpy as np
from typing import Tuple, Optional

class ProjectorHighlight:
    def __init__(self, width=1920, height=1080, fullscreen=False):
        """
        初始化投影仪显示
        width: 投影分辨率宽度
        height: 投影分辨率高度
        fullscreen: 是否全屏显示（默认False，避免阻塞界面）
        """
        self.width = width
        self.height = height
        self.current_highlight = None
        self.highlight_duration = 3.0  # 高亮持续时间（秒）
        self.highlight_start_time = None
        self.fullscreen = fullscreen
        self.window_created = False
        self.window_name = 'Book Highlight'
        
        # 延迟创建窗口，避免阻塞
        # 窗口将在第一次显示高亮时创建
        
        # 创建黑色背景
        self.background = np.zeros((height, width, 3), dtype=np.uint8)
    
    def _ensure_window(self):
        """确保窗口已创建（延迟创建）"""
        if not self.window_created:
            try:
                # 创建窗口（默认可调整大小，不全屏）
                cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                if self.fullscreen:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    # 设置窗口大小为屏幕的80%
                    try:
                        cv2.resizeWindow(self.window_name, int(self.width * 0.8), int(self.height * 0.8))
                    except:
                        # 如果resize失败，继续使用默认大小
                        pass
                self.window_created = True
            except Exception as e:
                print(f"警告: 无法创建投影窗口: {e}")
                print("将使用文本输出代替图形显示")
                self.window_created = False
                return False
        return True
    
    def highlight_book(self, position: Tuple[float, float, float, float], 
                      book_name: str = ""):
        """
        高亮显示书籍
        position: (x, y, width, height) 归一化坐标 (0-1)
        book_name: 书籍名称（可选，用于显示）
        """
        import time
        
        # 转换为像素坐标
        # 注意：position存储的是 (center_x, center_y, width, height) 归一化坐标
        # 需要转换为左上角坐标用于绘制
        center_x = position[0] * self.width
        center_y = position[1] * self.height
        w = int(position[2] * self.width)
        h = int(position[3] * self.height)
        
        # 计算左上角坐标
        x = int(center_x - w / 2)
        y = int(center_y - h / 2)
        
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
        
        # 只有在有高亮时才创建窗口
        if self.current_highlight is None and not self.window_created:
            return False
        
        # 确保窗口已创建
        if self.current_highlight is not None:
            if not self._ensure_window():
                # 如果窗口创建失败，使用文本输出
                if self.current_highlight:
                    book_name = self.current_highlight.get('book_name', '')
                    x, y, w, h = self.current_highlight['position']
                    shelf = "上排" if y < 0.5 else "下排"
                    print(f"\n{'='*60}")
                    print(f"📚 找到书籍: {book_name}")
                    print(f"📍 位置: {shelf} (坐标: x={x:.2f}, y={y:.2f})")
                    print(f"{'='*60}\n")
                return False
        
        # 创建背景副本
        frame = self.background.copy()
        
        # 检查是否需要显示高亮
        if self.current_highlight is not None:
            current_time = time.time()
            elapsed = current_time - self.highlight_start_time
            
            # 如果还在显示时间内
            if elapsed < self.highlight_duration:
                x, y, w, h = self.current_highlight['position']
                book_name = self.current_highlight['book_name']
                
                # 计算闪烁效果（可选）
                alpha = 0.7 + 0.3 * np.sin(elapsed * 4)  # 闪烁效果
                
                # 绘制高亮矩形（红色边框，半透明填充）
                overlay = frame.copy()
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), 8)
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.3 * alpha, frame, 1 - 0.3 * alpha, 0, frame)
                
                # 绘制边框（更明显）
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 8)
                
                # 显示书名（如果有）
                if book_name:
                    # 计算文字位置（在矩形上方）
                    text_y = max(30, y - 10)
                    text_x = x
                    
                    # 绘制文字背景
                    (text_width, text_height), baseline = cv2.getTextSize(
                        book_name, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2
                    )
                    cv2.rectangle(
                        frame,
                        (text_x - 5, text_y - text_height - 5),
                        (text_x + text_width + 5, text_y + baseline + 5),
                        (0, 0, 0),
                        -1
                    )
                    
                    # 绘制文字
                    cv2.putText(
                        frame,
                        book_name,
                        (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 255, 255),
                        2,
                        cv2.LINE_AA
                    )
                
                # 显示帧（非阻塞）
                try:
                    cv2.imshow(self.window_name, frame)
                    return True
                except Exception as e:
                    print(f"警告: 无法更新显示: {e}")
                    return False
            else:
                # 超时，清除高亮
                self.clear_highlight()
        
        # 显示空白背景（如果有窗口）
        if self.window_created:
            try:
                cv2.imshow(self.window_name, frame)
            except Exception as e:
                print(f"警告: 无法更新显示: {e}")
                self.window_created = False
        return False
    
    def run(self, stop_event=None):
        """
        运行显示循环（在后台线程中运行，不阻塞主程序）
        stop_event: 停止事件（threading.Event）
        """
        import time
        
        if stop_event is None:
            import threading
            stop_event = threading.Event()
        
        # 不在初始化时打印，避免干扰
        window_opened = False
        
        while not stop_event.is_set():
            self.update_display()
            
            # 只在窗口创建后检查按键
            if self.window_created:
                try:
                    if not window_opened:
                        print("投影窗口已打开。点击窗口后按 'q' 或 ESC 键可关闭窗口")
                        window_opened = True
                    
                    # 使用非阻塞方式检查按键（waitKey(1) 只等待1ms）
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
                    # 如果窗口操作失败，重置状态
                    print(f"窗口操作错误: {e}")
                    self.window_created = False
            else:
                # 没有窗口时，减少CPU使用
                time.sleep(0.1)
            
            time.sleep(0.03)  # 约30 FPS
        
        # 清理
        if self.window_created:
            cv2.destroyAllWindows()
    
    def __del__(self):
        """清理资源"""
        cv2.destroyAllWindows()

