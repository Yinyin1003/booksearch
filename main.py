"""
主程序
整合语音识别、书籍搜索和投影仪高亮功能
"""

import sys
import threading
import time
import os
from voice_recognition import VoiceRecognizer
from book_database import BookDatabase
from projector_highlight import ProjectorHighlight
from projector_image import ProjectorImage

# 尝试导入Tkinter版本
try:
    from projector_tkinter import ProjectorTkinter
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    ProjectorTkinter = None

# 导入简单模式（保存图片文件）
from projector_simple import ProjectorSimple

class BookSearchSystem:
    def __init__(self, image_path=None, use_simple_mode=True):
        """
        初始化系统
        image_path: 书架照片路径（如果提供，将使用图片模式）
        use_simple_mode: 是否使用简单模式（保存图片文件，推荐）
        """
        print("正在初始化书籍搜索系统...")
        
        # 初始化各个模块
        # 使用英文语音识别（因为书籍名称是英文）
        self.voice_recognizer = VoiceRecognizer(language='en-US')
        self.book_database = BookDatabase()
        
        # 选择显示模式
        if image_path and os.path.exists(image_path):
            print(f"📸 使用图片模式: {image_path}")
            
            if use_simple_mode:
                # 使用简单模式（推荐）：保存图片文件
                print("   使用简单模式：保存高亮图片到文件")
                self.projector = ProjectorSimple(image_path=image_path)
                self.use_image_mode = True
                self.use_tkinter = False
                self.use_simple_mode = True
            else:
                # 尝试GUI模式
                if TKINTER_AVAILABLE:
                    try:
                        print("   尝试使用Tkinter显示（GUI模式）...")
                        self.projector = ProjectorTkinter(image_path=image_path, width=1920, height=1080)
                        self.use_image_mode = True
                        self.use_tkinter = True
                        self.use_simple_mode = False
                        print("✅ 使用Tkinter显示模式")
                    except Exception as e:
                        print(f"⚠️  Tkinter初始化失败: {e}")
                        print("   降级到OpenCV模式...")
                        self.projector = ProjectorImage(image_path=image_path, width=1920, height=1080, fullscreen=True)
                        self.use_image_mode = True
                        self.use_tkinter = False
                        self.use_simple_mode = False
                else:
                    # 使用OpenCV模式
                    self.projector = ProjectorImage(image_path=image_path, width=1920, height=1080, fullscreen=True)
                    self.use_image_mode = True
                    self.use_tkinter = False
                    self.use_simple_mode = False
        else:
            print("🖥️  使用普通显示模式")
            # 默认不全屏，避免阻塞界面（如需全屏，设置 fullscreen=True）
            self.projector = ProjectorHighlight(width=1920, height=1080, fullscreen=False)
            self.use_image_mode = False
            self.use_tkinter = False
            self.use_simple_mode = False
        
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
            print(f"   匹配关键词: {book_key}")
            shelf_name = "上排" if book_info['shelf'] == 0 else "下排"
            print(f"📍 位置: {shelf_name}, 坐标: {book_info['position']}")
            
            # 语音反馈
            self.voice_recognizer.speak(f"找到书籍：{book_info['full_name']}")
            
            # 高亮显示
            self.projector.highlight_book(
                book_info['position'],
                book_info['full_name']
            )
        else:
            print("❌ 未找到匹配的书籍")
            print(f"   识别到的文本: '{text}'")
            print("   提示: 尝试使用更完整或更准确的书名")
            print("\n   可用的书籍关键词示例:")
            all_books = self.book_database.get_all_books()
            for i, key in enumerate(list(all_books.keys())[:5], 1):
                print(f"   {i}. {key}")
            if len(all_books) > 5:
                print(f"   ... 还有 {len(all_books) - 5} 本书")
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
        print("2. 按 'q' 键退出投影显示窗口")
        print("3. 按 Ctrl+C 退出程序")
        print("="*50 + "\n")
        
        # 启动投影仪显示线程
        if self.use_tkinter:
            # Tkinter需要在主线程运行，但我们可以用特殊方式处理
            # 在interactive_mode中会特殊处理
            pass
        else:
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
        print("注意：投影窗口会在找到书籍时自动打开，不会阻塞键盘输入\n")
        
        # 启动投影窗口
        if self.use_simple_mode:
            # 简单模式不需要启动窗口
            print("💡 简单模式：找到书籍时会自动保存图片并打开")
            pass
        elif self.use_tkinter:
            # Tkinter必须在主线程创建，使用非阻塞模式
            try:
                # 在主线程中创建窗口（非阻塞）
                self.projector._create_window_main_thread(self.stop_event)
                print("✅ Tkinter窗口已创建（非阻塞模式）")
            except Exception as e:
                print(f"❌ Tkinter窗口创建失败: {e}")
                print("   降级到文本输出模式")
                self.use_tkinter = False
        else:
            # OpenCV在后台线程运行
            projector_thread = threading.Thread(
                target=self.projector.run,
                args=(self.stop_event,),
                daemon=True
            )
            projector_thread.start()
        
        try:
            while True:
                try:
                    # 如果是Tkinter，需要定期更新窗口（非阻塞）
                    if self.use_tkinter and self.projector and self.projector.root:
                        try:
                            self.projector.root.update_idletasks()
                        except:
                            pass
                    
                    query = input("\n请输入书名: ").strip()
                    if query.lower() == 'quit':
                        break
                    
                    if query:
                        self.on_voice_recognized(query)
                        # 如果是Tkinter，立即更新显示
                        if self.use_tkinter and self.projector:
                            self.projector.update_display()
                        # 简单模式不需要额外操作，图片已自动保存
                except KeyboardInterrupt:
                    break
        finally:
            self.stop_event.set()
            if self.use_tkinter and self.projector:
                self.projector._close_window()
            print("退出交互模式")

def main():
    """主函数"""
    # 检查命令行参数
    image_path = None
    
    # 检查是否有图片路径参数
    if '--image' in sys.argv:
        idx = sys.argv.index('--image')
        if idx + 1 < len(sys.argv):
            image_path = sys.argv[idx + 1]
        else:
            print("错误: --image 参数需要指定图片路径")
            print("用法: python3 main.py --image <图片路径> [--test]")
            return
    
    # 如果没有指定图片，检查是否有默认图片
    if image_path is None:
        # 检查常见的图片文件名
        default_images = ['bookshelf.jpg', 'bookshelf.png', 'shelf.jpg', 'shelf.png', 'book.jpg', 'book.png']
        for img in default_images:
            if os.path.exists(img):
                image_path = img
                print(f"📸 找到默认图片: {image_path}")
                break
    
    system = BookSearchSystem(image_path=image_path)
    
    # 检查是否是测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # 测试模式：使用文本输入而不是语音
        system.interactive_mode()
    elif '--test' in sys.argv:
        # 测试模式（可能在 --image 之后）
        system.interactive_mode()
    else:
        # 正常模式：使用语音识别
        system.start()

if __name__ == "__main__":
    main()

