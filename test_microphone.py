#!/usr/bin/env python3
"""
麦克风测试工具
用于诊断语音输入问题
"""

import speech_recognition as sr
import sys

def test_microphone():
    """测试麦克风是否正常工作"""
    print("="*60)
    print("麦克风测试工具")
    print("="*60)
    
    try:
        # 初始化识别器
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("\n1. 检查可用的麦克风设备...")
        mic_list = sr.Microphone.list_microphone_names()
        if mic_list:
            print(f"   找到 {len(mic_list)} 个麦克风设备:")
            for i, name in enumerate(mic_list):
                print(f"   [{i}] {name}")
        else:
            print("   ⚠️  未找到麦克风设备")
        
        print("\n2. 测试麦克风访问...")
        try:
            with microphone as source:
                print("   ✅ 可以访问默认麦克风")
        except Exception as e:
            print(f"   ❌ 无法访问麦克风: {e}")
            print("   提示: 请检查系统设置中的麦克风权限")
            return False
        
        print("\n3. 校准环境噪音（请保持安静3秒）...")
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=3)
            print("   ✅ 校准完成")
        except Exception as e:
            print(f"   ⚠️  校准失败: {e}")
        
        print("\n4. 测试语音录制（请说话5秒）...")
        try:
            with microphone as source:
                print("   🎤 正在录音...（请说话）")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("   ✅ 录音成功")
        except sr.WaitTimeoutError:
            print("   ⚠️  超时：未检测到语音输入")
            print("   提示: 请检查麦克风是否正常工作，或说话声音是否足够大")
            return False
        except Exception as e:
            print(f"   ❌ 录音失败: {e}")
            return False
        
        print("\n5. 测试语音识别（需要网络连接）...")
        try:
            print("   🔍 正在识别...")
            text = recognizer.recognize_google(audio, language='zh-CN')
            print(f"   ✅ 识别成功: {text}")
            return True
        except sr.UnknownValueError:
            print("   ⚠️  无法识别语音内容")
            print("   提示: 请说话更清晰，或检查环境噪音")
            return False
        except sr.RequestError as e:
            print(f"   ❌ 语音识别服务错误: {e}")
            print("   提示: 需要网络连接才能使用Google语音识别服务")
            return False
        except Exception as e:
            print(f"   ❌ 识别失败: {e}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("\n开始测试麦克风...\n")
    success = test_microphone()
    print("\n" + "="*60)
    if success:
        print("✅ 麦克风测试通过！")
        print("   语音输入应该可以正常工作")
    else:
        print("❌ 麦克风测试失败")
        print("\n可能的解决方案:")
        print("1. 检查系统设置 -> 隐私与安全性 -> 麦克风权限")
        print("2. 确保网络连接正常（Google语音识别需要网络）")
        print("3. 检查麦克风硬件是否正常工作")
        print("4. 尝试在安静的环境中测试")
    print("="*60 + "\n")
    sys.exit(0 if success else 1)

