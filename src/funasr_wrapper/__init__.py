"""
FunASR到Whisper格式转换器
将FunASR的输出格式转换为Whisper的输出格式，以便与现有的analyze_audio方法兼容

注意：此模块专门处理ASR（自动语音识别）引擎之间的格式转换，
特别是将FunASR输出转换为Whisper格式，以确保与现有音频分析工具的兼容性。
"""

from .format_converter import funasr_to_whisper_format


def convert_funasr_to_whisper_format(funasr_result):
    """
    将FunASR输出格式转换为Whisper输出格式，以便与现有的analyze_audio方法兼容
    
    Args:
        funasr_result: FunASR的输出结果字典
        
    Returns:
        符合Whisper格式的结果字典
    """
    return funasr_to_whisper_format(funasr_result)