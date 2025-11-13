"""
摄像头和投影仪模块
使用摄像头实时捕获书架画面，并在投影仪上高亮显示书籍
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import time

class CameraProjector:
    def __init__(self, camera_index=0, projector_display=1):
        """
        初始化摄像头和投影仪
        camera_index: 摄像头设备索引（0为默认摄像头）
        projector_display: 投影仪显示器编号（1为第二个显示器）
        """
        self.camera_index = camera_index
        self.projector_display = projector_display
        self.cap = None
        self.current_highlight = None
        self.highlight_duration = 5.0  # 高亮持续时间（秒）
        self.highlight_start_time = None
        self.running = False
        
    def initialize_camera(self):
        """初始化摄像头"""
        try:
            print(f"正在初始化摄像头（设备 {self.camera_index}）...")
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise Exception(f"无法打开摄像头 {self.camera_index}")
            
            # 设置摄像头分辨率（可选）
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            # 测试读取一帧
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("无法从摄像头读取画面")
            
            print(f"✅ 摄像头初始化成功")
            print(f"   分辨率: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            return True
            
        except Exception as e:
            print(f"❌ 摄像头初始化失败: {e}")
            print("   提示: 请检查摄像头是否已连接")
            return False
    
    def highlight_book(self, position: Tuple[float, float, float, float], 
                      book_name: str = ""):
        """
        高亮显示书籍
        position: (x, y, width, height) 归一化坐标 (0-1)
        book_name: 书籍名称（可选，用于显示）
        """
        self.current_highlight = {
            'position': position,
            'book_name': book_name,
            'start_time': time.time()
        }
        self.highlight_start_time = time.time()
        print(f"📚 高亮显示: {book_name}")
    
    def clear_highlight(self):
        """清除高亮"""
        self.current_highlight = None
        self.highlight_start_time = None
    
    def draw_highlight(self, frame):
        """在画面上绘制高亮框"""
        if self.current_highlight is None:
            return frame
        
        current_time = time.time()
        elapsed = current_time - self.highlight_start_time
        
        # 如果超过显示时间，清除高亮
        if elapsed > self.highlight_duration:
            self.clear_highlight()
            return frame
        
        # 获取画面尺寸
        h, w = frame.shape[:2]
        
        # 转换为像素坐标
        x = int(self.current_highlight['position'][0] * w)
        y = int(self.current_highlight['position'][1] * h)
        width = int(self.current_highlight['position'][2] * w)
        height = int(self.current_highlight['position'][3] * h)
        
        # 确保坐标在范围内
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = min(width, w - x)
        height = min(height, h - y)
        
        # 计算闪烁效果
        alpha = 0.7 + 0.3 * np.sin(elapsed * 4)
        
        # 创建高亮覆盖层
        overlay = frame.copy()
        
        # 绘制半透明红色填充
        cv2.rectangle(overlay, (x, y), (x + width, y + height), (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.3 * alpha, frame, 1 - 0.3 * alpha, 0, frame)
        
        # 绘制红色边框（更明显）
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 8)
        
        # 绘制书名
        if self.current_highlight['book_name']:
            book_name = self.current_highlight['book_name']
            
            # 计算文字大小和位置
            font_scale = max(1.0, min(w, h) / 800)
            thickness = max(2, int(font_scale * 2))
            
            (text_width, text_height), baseline = cv2.getTextSize(
                book_name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )
            
            # 文字位置（在矩形上方）
            text_x = x
            text_y = max(text_height + 10, y - 10)
            
            # 绘制文字背景
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
                font_scale,
                (0, 255, 255),
                thickness,
                cv2.LINE_AA
            )
        
        return frame
    
    def run(self, stop_event=None):
        """
        运行摄像头和投影仪显示循环
        stop_event: 停止事件（threading.Event）
        """
        import threading
        
        if stop_event is None:
            stop_event = threading.Event()
        
        if not self.initialize_camera():
            print("无法启动摄像头，退出显示循环")
            return
        
        self.running = True
        
        # 创建显示窗口
        window_name = 'Book Highlight - Projector'
        window_created = False
        
        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            window_created = True
            
            # 尝试全屏显示（投影仪）
            try:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                print("✅ 投影窗口已设置为全屏模式")
            except:
                print("⚠️  无法设置全屏，使用窗口模式")
                try:
                    cv2.resizeWindow(window_name, 1920, 1080)
                except:
                    pass
        except Exception as e:
            print(f"⚠️  无法创建OpenCV窗口: {e}")
            print("   将使用替代显示方案（保存图像文件）")
            window_created = False
        
        print("\n" + "="*60)
        print("📹 摄像头和投影仪已启动")
        print("="*60)
        if window_created:
            print("操作说明:")
            print("- 摄像头画面会实时显示在投影仪上")
            print("- 找到书籍时会自动高亮显示")
            print("- 按 'q' 或 ESC 键退出")
        else:
            print("操作说明:")
            print("- 摄像头画面会保存为图像文件")
            print("- 找到书籍时会自动高亮并保存")
            print("- 图像保存在当前目录")
        print("="*60 + "\n")
        
        frame_count = 0
        save_interval = 30  # 每30帧保存一次（约1秒）
        
        try:
            while not stop_event.is_set() and self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("⚠️  无法读取摄像头画面")
                    time.sleep(0.1)
                    continue
                
                # 绘制高亮
                frame = self.draw_highlight(frame)
                
                # 显示画面
                if window_created:
                    try:
                        cv2.imshow(window_name, frame)
                        
                        # 检查按键
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q') or key == 27:  # 'q' 或 ESC
                            print("退出摄像头和投影仪显示")
                            break
                    except Exception as e:
                        print(f"⚠️  显示错误: {e}")
                        window_created = False
                else:
                    # 如果没有窗口，定期保存图像
                    frame_count += 1
                    if frame_count % save_interval == 0:
                        try:
                            filename = f"bookshelf_frame_{int(time.time())}.jpg"
                            cv2.imwrite(filename, frame)
                            if frame_count == save_interval:
                                print(f"📸 图像已保存: {filename} (每1秒更新)")
                        except Exception as e:
                            pass
                
                time.sleep(0.03)  # 约30 FPS
                
        except KeyboardInterrupt:
            print("\n正在关闭摄像头和投影仪...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        if self.cap is not None:
            self.cap.release()
        try:
            cv2.destroyAllWindows()
        except:
            pass
        print("✅ 摄像头和投影仪已关闭")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()

