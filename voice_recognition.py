"""
语音识别模块
使用麦克风接收语音输入并转换为文本
"""

import speech_recognition as sr
import threading
import subprocess
import platform
import sys

# 尝试导入 pyttsx3，如果失败则使用系统命令
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception as e:
    TTS_AVAILABLE = False
    print(f"注意: pyttsx3 不可用，将使用系统 say 命令: {e}")

class VoiceRecognizer:
    def __init__(self, language='en-US'):
        """
        初始化语音识别器
        language: 语言代码，'zh-CN' 为中文，'en-US' 为英文
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = language
        self.tts_engine = None
        self.use_system_say = False
        
        # 显示当前语言设置
        lang_name = "英文" if language == 'en-US' else "中文"
        print(f"语音识别语言: {lang_name} ({language})")
        
        # 尝试初始化 TTS 引擎
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # 配置TTS（文本转语音）
                if language == 'zh-CN':
                    # 尝试设置中文语音
                    voices = self.tts_engine.getProperty('voices')
                    for voice in voices:
                        if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            except Exception as e:
                print(f"pyttsx3 初始化失败，将使用系统 say 命令: {e}")
                self.tts_engine = None
        
        # 如果 TTS 引擎不可用，使用系统命令
        if self.tts_engine is None:
            self.use_system_say = True
            if platform.system() == 'Darwin':  # macOS
                print("将使用 macOS say 命令进行语音输出")
            else:
                print("警告: 当前系统不支持语音输出")
        
        # 调整环境噪音
        print("正在校准麦克风，请保持安静...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("校准完成！")
    
    def listen(self, timeout=5, phrase_time_limit=5):
        """
        监听语音输入
        timeout: 超时时间（秒）
        phrase_time_limit: 短语最大长度（秒）
        返回: 识别的文本或 None
        """
        try:
            with self.microphone as source:
                print(f"🎤 正在监听...（{timeout}秒超时，请说话）")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔍 正在识别语音...")
            # 使用Google语音识别API
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"✅ 识别结果: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏱️  超时：未检测到语音输入（请检查麦克风是否正常工作）")
            return None
        except sr.UnknownValueError:
            print("❌ 无法识别语音（请说话更清晰或检查环境噪音）")
            return None
        except sr.RequestError as e:
            print(f"❌ 语音识别服务错误: {e}")
            print("   提示：需要网络连接才能使用Google语音识别服务")
            return None
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("   提示：请检查麦克风权限和连接")
            return None
    
    def speak(self, text):
        """文本转语音输出"""
        if self.use_system_say:
            # 使用 macOS 的 say 命令
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['say', text], check=False)
                else:
                    print(f"语音输出: {text}")
            except Exception as e:
                print(f"语音输出错误: {e}")
        elif self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"语音输出错误: {e}")
                # 如果 pyttsx3 失败，尝试使用系统命令
                if platform.system() == 'Darwin':
                    try:
                        subprocess.run(['say', text], check=False)
                    except:
                        pass
        else:
            print(f"语音输出: {text}")
    
    def continuous_listen(self, callback, stop_event=None):
        """
        持续监听模式
        callback: 识别到文本后的回调函数
        stop_event: 停止事件（threading.Event）
        """
        if stop_event is None:
            stop_event = threading.Event()
        
        def listen_loop():
            print("🎤 语音监听已启动，请说话...")
            while not stop_event.is_set():
                try:
                    text = self.listen(timeout=3, phrase_time_limit=5)
                    if text:
                        callback(text)
                except Exception as e:
                    print(f"监听循环错误: {e}")
                    # 继续监听，不退出
                    import time
                    time.sleep(1)
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        return stop_event

