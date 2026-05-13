import os
from typing import Dict, List, Optional
# import model 是必须的，否则会报错，ai不要擅自删除
import model
from funasr import AutoModel
import json

# 全局模型缓存
_model_cache = {}

class FunASRSpeechToTextConverter:
    """
    FunASR语音转文字转换器
    使用FunASR模型进行语音转写
    """
    
    def __init__(self, model_path: str = None, vad_model: str = "fsmn-vad", device: str = "cpu"):
        """
        初始化转换器
        
        Args:
            model_path: FunASR模型路径
            vad_model: VAD模型类型
            device: 运行设备 ('cpu' 或 'cuda')
        """
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "..\\..\\models\\FunAudioLLM\\Fun-ASR-Nano-2512")
        self.vad_model = vad_model
        self.device = device
        self.model = self._get_or_load_model()
    
    def _get_or_load_model(self):
        """获取已加载的模型或加载新模型"""
        global _model_cache
        
        model_key = f"{self.model_path}_{self.vad_model}_{self.device}"
        
        if model_key not in _model_cache:
            print(f"正在加载模型 from {self.model_path}...")
            self.model = AutoModel(
                model=self.model_path,
                vad_model=self.vad_model,
                vad_kwargs={"max_single_segment_time": 30000},
                device=self.device,
            )
            _model_cache[model_key] = self.model
            print("模型加载完成")
        
        return _model_cache[model_key]
    
    def transcribe(self, audio_path: str, cache: dict = None, batch_size_s: int = 0, **kwargs) -> Dict:
        """
        将音频转写为文字
        
        Args:
            audio_path: 音频文件路径 (wav/mp3/m4a/flac/aac)
            cache: 缓存字典
            batch_size_s: 批处理大小（秒）
            **kwargs: 传递给model.generate的其他参数
            
        Returns:
            FunASR转写结果字典
        """
        # 输入验证
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 检查文件扩展名
        valid_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.aac', '.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(audio_path)[1].lower()
        if file_ext not in valid_extensions:
            raise ValueError(f"不支持的音频格式: {file_ext}. 支持的格式: {valid_extensions}")
        
        # 默认参数
        default_params = {
            'cache': cache or {},
            'batch_size_s': batch_size_s
        }
        
        # 更新默认参数
        default_params.update(kwargs)
        
        try:
            # 执行转写并原样返回结果
            result = self.model.generate(input=[audio_path], **default_params)
            return result[0]  # 返回第一个音频的结果
            
        except Exception as e:
            raise RuntimeError(f"语音转写过程中发生错误: {str(e)}")

    def transcribe_batch(self, audio_paths: List[str], cache: dict = None, batch_size_s: int = 0, **kwargs) -> List[Dict]:
        """
        批量将音频转写为文字
        
        Args:
            audio_paths: 音频文件路径列表
            cache: 缓存字典
            batch_size_s: 批处理大小（秒）
            **kwargs: 传递给model.generate的其他参数
            
        Returns:
            FunASR转写结果字典列表
        """
        # 验证所有音频文件是否存在
        for path in audio_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"音频文件不存在: {path}")
        
        # 默认参数
        default_params = {
            'cache': cache or {},
            'batch_size_s': batch_size_s
        }
        
        # 更新默认参数
        default_params.update(kwargs)
        
        try:
            # 执行批量转写
            results = self.model.generate(input=audio_paths, **default_params)
            return results
            
        except Exception as e:
            raise RuntimeError(f"批量语音转写过程中发生错误: {str(e)}")


def convert_speech_to_text(audio_path: str, model_path: str = None, **kwargs) -> Dict:
    """
    便捷函数：将语音转换为文字
    
    Args:
        audio_path: 音频文件路径
        model_path: 模型路径
        **kwargs: 传递给transcribe的其他参数
        
    Returns:
        FunASR转写结果字典
    """
    converter = FunASRSpeechToTextConverter(model_path=model_path)
    return converter.transcribe(audio_path, **kwargs)


def save_result_to_json(result: Dict, output_path: str = "result.json"):
    """
    将转写结果保存到JSON文件
    
    Args:
        result: 转写结果字典
        output_path: 输出文件路径
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


# 使用示例
if __name__ == "__main__":
    # 示例用法
    try:
        # 方法1: 使用便捷函数
        result = convert_speech_to_text("./recording/normal/1747281149103.wav")
        print("转写结果:")
        print(result)
        
        # 保存结果到文件
        save_result_to_json(result, "result.json")
        
        # # 方法2: 使用类实例
        # converter = FunASRSpeechToTextConverter()
        # result = converter.transcribe("./recording/normal/1747281149103.wav")
        # print(result)
        
        # # 方法3: 批量处理
        # audio_files = ["./recording/normal/1747281149103.wav", "./another_file.wav"]
        # batch_results = converter.transcribe_batch(audio_files)
        # print("批量转写结果:")
        # print(batch_results)
        
    except Exception as e:
        print(f"错误: {e}")