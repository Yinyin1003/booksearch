"""
主程序
整合语音识别、书籍搜索和投影仪高亮功能
"""

import sys
import threading
import time
from voice_recognition import VoiceRecognizer
from book_database import BookDatabase
from projector_highlight import ProjectorHighlight
from camera_projector import CameraProjector

class BookSearchSystem:
    def __init__(self, use_camera=False, camera_index=0):
        """
        初始化系统
        use_camera: 是否使用摄像头和投影仪
        camera_index: 摄像头设备索引
        """
        print("正在初始化书籍搜索系统...")
        
        # 初始化各个模块
        # 使用英文语音识别（因为书籍名称是英文）
        self.voice_recognizer = VoiceRecognizer(language='en-US')
        self.book_database = BookDatabase()
        
        # 选择显示方式
        self.use_camera = use_camera
        if use_camera:
            print("📹 使用摄像头和投影仪模式")
            self.camera_projector = CameraProjector(camera_index=camera_index)
            self.projector = None
        else:
            print("🖥️  使用普通投影显示模式")
            # 默认不全屏，避免阻塞界面（如需全屏，设置 fullscreen=True）
            self.projector = ProjectorHighlight(width=1920, height=1080, fullscreen=False)
            self.camera_projector = None
        
        # 控制标志
        self.running = False
        self.stop_event = threading.Event()
        
        print("系统初始化完成！")
    
    def on_voice_recognized(self, text):
        """语音识别回调函数"""
        print(f"\n识别到语音: {text}")
        
        # 搜索书籍
        book_key, book_info = self.book_database.search_book(text)
        
        if book_info:
            print(f"✅ 找到书籍: {book_info['full_name']}")
            shelf_name = "上排" if book_info['shelf'] == 0 else "下排"
            print(f"📍 位置: {shelf_name}, 坐标: {book_info['position']}")
            
            # 语音反馈
            self.voice_recognizer.speak(f"找到书籍：{book_info['full_name']}")
            
            # 高亮显示
            if self.use_camera and self.camera_projector:
                self.camera_projector.highlight_book(
                    book_info['position'],
                    book_info['full_name']
                )
            elif self.projector:
                self.projector.highlight_book(
                    book_info['position'],
                    book_info['full_name']
                )
        else:
            print("❌ 未找到匹配的书籍")
            print("   提示: 尝试使用更完整或更准确的书名")
            self.voice_recognizer.speak("抱歉，未找到匹配的书籍")
    
    def start(self):
        """启动系统"""
        if self.running:
            print("系统已在运行中")
            return
        
        self.running = True
        self.stop_event.clear()
        
        print("\n" + "="*50)
        print("书籍搜索系统已启动")
        print("="*50)
        print("使用说明:")
        print("1. 说出书名，系统会自动搜索并高亮显示")
        if self.use_camera:
            print("2. 摄像头画面会实时显示在投影仪上")
            print("3. 按 'q' 键退出投影显示窗口")
        else:
            print("2. 按 'q' 键退出投影显示窗口")
        print("3. 按 Ctrl+C 退出程序")
        print("="*50 + "\n")
        
        # 启动投影仪显示线程
        if self.use_camera and self.camera_projector:
            projector_thread = threading.Thread(
                target=self.camera_projector.run,
                args=(self.stop_event,),
                daemon=True
            )
            projector_thread.start()
        elif self.projector:
            projector_thread = threading.Thread(
                target=self.projector.run,
                args=(self.stop_event,),
                daemon=True
            )
            projector_thread.start()
        
        # 启动持续语音监听
        self.voice_recognizer.continuous_listen(
            self.on_voice_recognized,
            self.stop_event
        )
        
        try:
            # 主循环
            while self.running and not self.stop_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n正在关闭系统...")
            self.stop()
    
    def stop(self):
        """停止系统"""
        self.running = False
        self.stop_event.set()
        print("系统已关闭")
    
    def interactive_mode(self):
        """交互模式：手动输入书名进行测试"""
        print("\n进入交互测试模式")
        print("输入书名进行测试（输入 'quit' 退出）:")
        if self.use_camera:
            print("注意：摄像头画面会实时显示在投影仪上\n")
        else:
            print("注意：投影窗口会在找到书籍时自动打开，不会阻塞键盘输入\n")
        
        # 在后台启动投影窗口线程（不阻塞输入）
        if self.use_camera and self.camera_projector:
            projector_thread = threading.Thread(
                target=self.camera_projector.run,
                args=(self.stop_event,),
                daemon=True
            )
            projector_thread.start()
        elif self.projector:
            projector_thread = threading.Thread(
                target=self.projector.run,
                args=(self.stop_event,),
                daemon=True
            )
            projector_thread.start()
        
        try:
            while True:
                try:
                    query = input("\n请输入书名: ").strip()
                    if query.lower() == 'quit':
                        break
                    
                    if query:
                        self.on_voice_recognized(query)
                except KeyboardInterrupt:
                    break
        finally:
            self.stop_event.set()
            print("退出交互模式")

def main():
    """主函数"""
    # 检查命令行参数
    use_camera = '--camera' in sys.argv or '-c' in sys.argv
    camera_index = 0
    
    # 检查是否指定了摄像头索引
    if '--camera-index' in sys.argv:
        idx = sys.argv.index('--camera-index')
        if idx + 1 < len(sys.argv):
            try:
                camera_index = int(sys.argv[idx + 1])
            except:
                print("警告: 无效的摄像头索引，使用默认值 0")
    
    system = BookSearchSystem(use_camera=use_camera, camera_index=camera_index)
    
    # 检查命令行参数
    if len(sys.argv) > 1 and (sys.argv[1] == '--test' or sys.argv[1] == '-t'):
        # 测试模式：使用文本输入而不是语音
        system.interactive_mode()
    else:
        # 正常模式：使用语音识别
        system.start()

if __name__ == "__main__":
    main()

