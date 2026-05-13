"""
语音处理模块
包含语音转文字、音频分析和文本相似度计算等功能
"""

from whisper_wrapper.converter import SpeechToTextConverter, convert_speech_to_text
from .audio_analyzer import AudioAnalyzer, analyze_audio
from .text_to_vec import TextSimilarityCalculator, calculate_similarity

__all__ = [
    'SpeechToTextConverter',
    'convert_speech_to_text',
    'AudioAnalyzer',
    'analyze_audio',
    'TextSimilarityCalculator',
    'calculate_similarity'
]