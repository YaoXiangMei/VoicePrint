"""
FunASR到Whisper格式转换器
将FunASR的输出格式转换为Whisper的输出格式，以便与现有的analyze_audio方法兼容
"""

def funasr_to_whisper_format(funasr_result):
    """
    将FunASR输出格式转换为Whisper输出格式
    
    Args:
        funasr_result: FunASR的输出结果字典
        
    Returns:
        符合Whisper格式的结果字典
    """
    # 提取文本内容
    text = funasr_result.get("text", "")
    
    # 构建segments
    segments = []
    timestamps = funasr_result.get("timestamps", [])
    
    if timestamps:
        # 按时间顺序组织时间戳
        import re
        
        # 按时间分组，将连续的时间戳组合成句子
        sentences = []
        current_sentence = ""
        current_start = None
        current_end = None
        current_words = []
        
        for i, ts_item in enumerate(timestamps):
            token = ts_item["token"]
            start_time = ts_item["start_time"] / 1000.0  # 转换为秒
            end_time = ts_item["end_time"] / 1000.0      # 转换为秒
            score = ts_item.get("score", 0.0)
            
            # 如果是标点符号，通常表示句子结束
            if token in ['。', '！', '？', '.', '!', '?', '，', ',', '：', ':', '；', ';']:
                if current_sentence.strip():
                    # 添加当前句子
                    if current_start is not None and current_end is not None:
                        sentence_text = current_sentence.strip()
                        if sentence_text:
                            segment = {
                                "id": len(segments),
                                "seek": 0,
                                "start": round(current_start, 2),
                                "end": round(current_end, 2),
                                "text": sentence_text,
                                "tokens": list(range(len(sentence_text))),  # 占位符
                                "temperature": 0.2,
                                "avg_logprob": -0.12659429331294825,
                                "compression_ratio": 1.4195121951219511,
                                "no_speech_prob": 0.312889039516449,
                                "words": current_words.copy()
                            }
                            segments.append(segment)
                    
                    # 重置当前句子
                    current_sentence = ""
                    current_start = None
                    current_end = None
                    current_words = []
            else:
                # 添加非标点符号到当前句子
                if current_start is None:
                    current_start = start_time
                current_end = end_time
                
                current_sentence += token
                current_words.append({
                    "word": token,
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "probability": min(score, 1.0)  # 确保概率不超过1
                })
        
        # 添加最后一个句子（如果有）
        if current_sentence.strip() and current_start is not None and current_end is not None:
            sentence_text = current_sentence.strip()
            if sentence_text:
                segment = {
                    "id": len(segments),
                    "seek": 0,
                    "start": round(current_start, 2),
                    "end": round(current_end, 2),
                    "text": sentence_text,
                    "tokens": list(range(len(sentence_text))),  # 占位符
                    "temperature": 0.2,
                    "avg_logprob": -0.12659429331294825,
                    "compression_ratio": 1.4195121951219511,
                    "no_speech_prob": 0.312889039516449,
                    "words": current_words.copy()
                }
                segments.append(segment)
    
    # 如果没有时间戳信息，尝试按标点符号分割文本
    if not segments:
        import re
        # 按句子分割文本
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 简单估算时间（每分钟约200字）
        total_duration = 60  # 假设总时长为60秒
        avg_chars_per_second = len(text) / total_duration if total_duration > 0 else 1
        
        current_time = 0
        for i, sentence in enumerate(sentences):
            if sentence:
                duration = len(sentence) / avg_chars_per_second
                segment = {
                    "id": i,
                    "seek": 0,
                    "start": round(current_time, 2),
                    "end": round(current_time + duration, 2),
                    "text": sentence,
                    "tokens": list(range(len(sentence))),  # 占位符
                    "temperature": 0.2,
                    "avg_logprob": -0.12659429331294825,
                    "compression_ratio": 1.4195121951219511,
                    "no_speech_prob": 0.312889039516449,
                    "words": []  # 占位符
                }
                
                # 为每个词生成简单的时间戳
                word_duration = duration / len(sentence) if len(sentence) > 0 else 0.1
                for j, char in enumerate(sentence):
                    segment["words"].append({
                        "word": char,
                        "start": round(current_time + j * word_duration, 2),
                        "end": round(current_time + (j + 1) * word_duration, 2),
                        "probability": 0.9  # 默认高置信度
                    })
                
                segments.append(segment)
                current_time += duration
    
    # 构建最终结果
    result = {
        "text": text,
        "segments": segments,
        "language": "zh"  # 默认中文
    }
    
    return result


def split_text_to_segments(text, max_chars_per_segment=50):
    """
    将文本按指定长度分割成片段，用于在没有时间戳信息时创建segments
    
    Args:
        text: 输入文本
        max_chars_per_segment: 每个片段的最大字符数
        
    Returns:
        segments列表
    """
    import re
    
    # 按句子边界分割，优先使用句号、感叹号、问号
    sentences = re.split(r'([。！？.!?])', text)
    
    # 重组句子（将标点符号与前面的句子合并）
    parts = []
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ''
        if sentence.strip():
            parts.append(sentence.strip() + punctuation)
    
    # 如果按句子分割后仍有太长的片段，则进一步分割
    final_parts = []
    for part in parts:
        if len(part) <= max_chars_per_segment:
            final_parts.append(part)
        else:
            # 按字符数进一步分割
            for i in range(0, len(part), max_chars_per_segment):
                chunk = part[i:i+max_chars_per_segment]
                if chunk.strip():
                    final_parts.append(chunk)
    
    return final_parts


def funasr_to_whisper_simple(funasr_result):
    """
    简化版转换函数，将FunASR输出转换为Whisper格式
    
    Args:
        funasr_result: FunASR的输出结果字典
        
    Returns:
        符合Whisper格式的结果字典
    """
    text = funasr_result.get("text", "")
    
    # 按句子分割文本
    segments_text = split_text_to_segments(text)
    
    # 估算时间（假设每分钟200字）
    total_duration = max(len(text) / 3.33, 1)  # 至少1秒
    avg_duration_per_char = total_duration / len(text) if len(text) > 0 else 0.1
    
    segments = []
    current_time = 0
    
    for i, seg_text in enumerate(segments_text):
        seg_duration = len(seg_text) * avg_duration_per_char
        segment = {
            "id": i,
            "seek": 0,
            "start": round(current_time, 2),
            "end": round(current_time + seg_duration, 2),
            "text": seg_text,
            "tokens": list(range(len(seg_text))),  # 占位符
            "temperature": 0.2,
            "avg_logprob": -0.12659429331294825,
            "compression_ratio": 1.4195121951219511,
            "no_speech_prob": 0.312889039516449,
            "words": []  # 占位符
        }
        
        # 为每个字符生成时间戳
        char_duration = seg_duration / len(seg_text) if len(seg_text) > 0 else 0.1
        for j, char in enumerate(seg_text):
            segment["words"].append({
                "word": char,
                "start": round(current_time + j * char_duration, 2),
                "end": round(current_time + (j + 1) * char_duration, 2),
                "probability": 0.9  # 默认高置信度
            })
        
        segments.append(segment)
        current_time += seg_duration
    
    result = {
        "text": text,
        "segments": segments,
        "language": "zh"  # 默认中文
    }
    
    return result


if __name__ == "__main__":
    # 测试转换函数
    test_funasr_result = {
        "key": "test",
        "text": "这是一个在厨房的场景，场景里面有妈妈和两个孩子。",
        "text_tn": "这是一个在厨房的场景场景里面有妈妈和两个孩子",
        "timestamps": [
            {"token": "这", "start_time": 360, "end_time": 420, "score": 0.995},
            {"token": "是", "start_time": 660, "end_time": 720, "score": 0.995},
            {"token": "一", "start_time": 2530360, "end_time": 2530420, "score": 1.0},
            {"token": "个", "start_time": 2530540, "end_time": 2530600, "score": 0.998},
        ]
    }
    
    converted = funasr_to_whisper_format(test_funasr_result)
    print("转换结果:")
    import json
    print(json.dumps(converted, ensure_ascii=False, indent=2))