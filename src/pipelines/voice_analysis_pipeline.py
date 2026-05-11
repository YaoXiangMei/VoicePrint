"""
语音分析整合模块
将语音转文字和连贯性分析两个步骤整合在一起
"""

from ..speech_processing.speech_to_text_converter import SpeechToTextConverter, convert_speech_to_text
from ..speech_processing.audio_analyzer import AudioAnalyzer, analyze_audio


class VoiceAnalysisPipeline:
    """
    语音分析流水线
    整合语音转文字和连贯性分析两个步骤
    """
    
    def __init__(self, model_size: str = "medium", pause_threshold: float = 3.0):
        """
        初始化语音分析流水线
        
        Args:
            model_size: Whisper模型大小
            pause_threshold: 长停顿时长阈值（秒）
        """
        self.converter = SpeechToTextConverter(model_size=model_size)
        self.pause_threshold = pause_threshold
    
    def analyze_audio(self, audio_path: str, **stt_kwargs) -> dict:
        """
        完整的语音分析流程
        
        Args:
            audio_path: 音频文件路径
            **stt_kwargs: 传递给语音转文字的额外参数
            
        Returns:
            分析结果字典
        """
        # 步骤1: 语音转文字
        transcription_result = self.converter.transcribe(audio_path, **stt_kwargs)
        
        # 步骤2: 连贯性分析
        analysis_result = analyze_audio(transcription_result)
        
        # 合并结果
        return {
            'transcription': transcription_result['text'],
            'whisper_result': transcription_result,
            'analysis': analysis_result
        }
    
    def get_detailed_analysis(self, audio_path: str, **stt_kwargs) -> dict:
        """
        获取详细分析结果
        
        Args:
            audio_path: 音频文件路径
            **stt_kwargs: 传递给语音转文字的额外参数
            
        Returns:
            详细分析结果字典
        """
        # 步骤1: 语音转文字
        transcription_result = self.converter.transcribe(audio_path, **stt_kwargs)
        
        # 步骤2: 连贯性分析
        analysis_result = analyze_audio(transcription_result)
        
        # 提取详细信息
        segments = transcription_result.get('segments', [])
        
        detailed_result = {
            'transcription': transcription_result['text'],
            'analysis': analysis_result,
            'segments_info': {
                'segment_count': len(segments),
                'segments': [
                    {
                        'text': seg['text'],
                        'start': seg['start'],
                        'end': seg['end'],
                        'duration': seg['end'] - seg['start']
                    } for seg in segments
                ] if segments else []
            },
            'metadata': {
                'audio_path': audio_path,
                'model_used': self.converter.model_size,
                'pause_threshold': self.pause_threshold
            }
        }
        
        return detailed_result


def analyze_voice_coherence(audio_path: str, model_size: str = "medium", pause_threshold: float = 3.0, **stt_kwargs) -> dict:
    """
    便捷函数：完整的语音连贯性分析
    
    Args:
        audio_path: 音频文件路径
        model_size: Whisper模型大小
        pause_threshold: 长停顿时长阈值（秒）
        **stt_kwargs: 传递给语音转文字的额外参数
        
    Returns:
        分析结果字典
    """
    pipeline = VoiceAnalysisPipeline(model_size=model_size, pause_threshold=pause_threshold)
    return pipeline.analyze_audio(audio_path, **stt_kwargs)


def analyze_voice_coherence_detailed(audio_path: str, model_size: str = "medium", pause_threshold: float = 3.0, **stt_kwargs) -> dict:
    """
    便捷函数：详细的语音连贯性分析
    
    Args:
        audio_path: 音频文件路径
        model_size: Whisper模型大小
        pause_threshold: 长停顿时长阈值（秒）
        **stt_kwargs: 传递给语音转文字的额外参数
        
    Returns:
        详细分析结果字典
    """
    pipeline = VoiceAnalysisPipeline(model_size=model_size, pause_threshold=pause_threshold)
    return pipeline.get_detailed_analysis(audio_path, **stt_kwargs)


# 使用示例
if __name__ == "__main__":
    import json
    
    # 示例1: 使用便捷函数
    try:
        result = analyze_voice_coherence("sample_audio.wav")
        print("=== 便捷函数分析结果 ===")
        print(json.dumps(result['analysis'], ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"便捷函数分析出错: {e}")
        print("提示: 请替换为实际存在的音频文件路径")
    
    # 示例2: 使用流水线类
    try:
        pipeline = VoiceAnalysisPipeline(model_size="medium")
        result = pipeline.analyze_audio("sample_audio.wav")
        print("\n=== 流水线类分析结果 ===")
        print(f"转录文本: {result['transcription'][:100]}...")  # 只显示前100个字符
        print(f"连贯性评分: {result['analysis']['scores']['total_coherence_score']['value']}")
    except Exception as e:
        print(f"流水线类分析出错: {e}")