"""
语音处理模块
包含语音转文字、音频分析和文本相似度计算等功能
"""

# 使用funasr转换器（硬编码）
from funasr_wrapper.converter import FunASRSpeechToTextConverter as SpeechToTextConverter, convert_speech_to_text
from .audio_analyzer import AudioAnalyzer, analyze_audio
from .text_to_vec import TextSimilarityCalculator, calculate_similarity
from funasr_wrapper.format_converter import funasr_to_whisper_format

__all__ = [
    'SpeechToTextConverter',
    'convert_speech_to_text',
    'AudioAnalyzer',
    'analyze_audio',
    'TextSimilarityCalculator',
    'calculate_similarity',
    'funasr_to_whisper_format'
]