"""
主程序入口
演示如何使用语音转文字转换器和音频分析器
"""
import json
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from speech_processing.speech_to_text_converter import convert_speech_to_text
from speech_processing.audio_analyzer import analyze_audio
from utils.output_formatter import print_analysis_result, format_output
from speech_processing.text_to_vec import calculate_similarity, TextSimilarityCalculator


def main():
    print("语音分析系统演示")
    
    # 示例音频文件路径（请替换为实际存在的音频文件）
    audio_file = "1773449008772.wav"
    
    try:
        # 直接从JSON文件加载结果（用于演示）
        # result = json.load(open("1747281149103.json", "r", encoding="utf-8"))
        result = convert_speech_to_text(audio_file)
        
        # 分析音频
        # analysis_result = analyze_audio(result)
        
        # 使用格式化输出
        # print_analysis_result(analysis_result)

        # 计算相似度
        # format_output(analysis_result)
        
        similarity = calculate_similarity(result["text"])
        print(f"相似度: {similarity}")
        
    except FileNotFoundError:
        print(f"错误: 找不到音频文件 '{audio_file}'")
        print("请确保音频文件存在且路径正确")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")


if __name__ == "__main__":
    main()