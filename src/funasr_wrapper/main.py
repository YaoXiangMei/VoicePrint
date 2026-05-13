import os
from converter import FunASRSpeechToTextConverter, convert_speech_to_text, save_result_to_json

def main():
    """
    主函数：演示FunASR语音转文字功能
    """
    # 设置音频文件路径
    wav_path = "./recording/normal/1747281149103.wav"
    
    try:
        # 方法1: 使用便捷函数进行转写
        print("使用便捷函数进行转写...")
        result = convert_speech_to_text(wav_path)
        print("转写结果:")
        print(result)
        
        # 保存结果到文件
        save_result_to_json(result, "result.json")
        print("结果已保存到 result.json")
        
        # 方法2: 使用类实例进行转写（更灵活的配置）
        print("\n使用类实例进行转写...")
        converter = FunASRSpeechToTextConverter()
        result2 = converter.transcribe(wav_path)
        print("转写结果:")
        print(result2)
        
        # 也可以直接保存结果
        save_result_to_json(result2, "result2.json")
        print("结果已保存到 result2.json")
        
    except FileNotFoundError:
        print(f"错误: 音频文件不存在 - {wav_path}")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()