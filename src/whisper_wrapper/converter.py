import whisper
import os
from typing import Dict

# 全局模型缓存
_model_cache = {}

class SpeechToTextConverter:
    """
    语音转文字转换器
    使用Whisper模型进行语音转写
    """
    
    def __init__(self, model_size: str = "tiny"):
        """
        初始化转换器
        
        Args:
            model_size: Whisper模型大小 ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = self._get_or_load_model(model_size)
    
    @classmethod
    def _get_or_load_model(cls, model_size: str):
        """获取已加载的模型或加载新模型"""
        global _model_cache
        
        if model_size not in _model_cache:
            print(f"正在加载 {model_size} 模型...")
            _model_cache[model_size] = whisper.load_model(model_size)
            print("模型加载完成")
        
        return _model_cache[model_size]
    
    def transcribe(self, audio_path: str, **kwargs) -> Dict:
        """
        将音频转写为文字
        
        Args:
            audio_path: 音频文件路径 (wav/mp3/m4a/flac/aac)
            **kwargs: 传递给whisper.transcribe的其他参数
            
        Returns:
            Whisper原始转写结果字典
        """
        # 输入验证
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 检查文件扩展名
        valid_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        file_ext = os.path.splitext(audio_path)[1].lower()
        if file_ext not in valid_extensions:
            raise ValueError(f"不支持的音频格式: {file_ext}. 支持的格式: {valid_extensions}")
        
        # 默认参数
        default_params = {
            'language': 'zh',
            'verbose': True,
            'word_timestamps': True,
            'temperature': 0.2,
            'condition_on_previous_text': True,
            'fp16': False,
            'initial_prompt': '请使用简体中文输出转写结果'
        }
        
        # 更新默认参数
        default_params.update(kwargs)
        
        try:
            # 执行转写并原样返回结果
            result = self.model.transcribe(audio_path, **default_params)
            return result
            
        except Exception as e:
            raise RuntimeError(f"语音转写过程中发生错误: {str(e)}")


def convert_speech_to_text(audio_path: str, model_size: str = "medium", **kwargs) -> Dict:
    """
    便捷函数：将语音转换为文字
    
    Args:
        audio_path: 音频文件路径
        model_size: 模型大小
        **kwargs: 传递给whisper.transcribe的其他参数
        
    Returns:
        Whisper原始转写结果字典
    """
    converter = SpeechToTextConverter(model_size=model_size)
    return converter.transcribe(audio_path, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 示例用法
    try:
        # 方法1: 使用便捷函数
        result = convert_speech_to_text("1747281149103.wav")
        print("转写结果:")
        print(result)
        
        # # 方法2: 使用类实例
        # converter = SpeechToTextConverter()
        # result = converter.transcribe("1747281149103.wav")
        # print(result)
        
    except Exception as e:
        print(f"错误: {e}")