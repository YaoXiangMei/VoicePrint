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
    
    # 优先使用ctc_timestamps，因为它是更准确的时间戳
    ctc_timestamps = funasr_result.get("ctc_timestamps", [])
    all_timestamps = funasr_result.get("timestamps", [])
    
    if ctc_timestamps:
        # 使用ctc_timestamps作为时间戳源，使用text和all_timestamps来确定分割点
        import re
        
        # 首先预处理，找出所有标点符号位置（在all_timestamps中）
        sentence_break_indices = []
        for i, ts_item in enumerate(all_timestamps):
            token = ts_item["token"]
            if token in ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';', '：', ':']:  # 包括逗号等
                sentence_break_indices.append(i)
        
        # 添加末尾索引
        sentence_break_indices.append(len(all_timestamps))
        
        # 创建一个映射，将text中的字符位置映射到ctc_timestamps中的索引
        text_pos = 0
        ctc_idx = 0
        char_to_ctc_idx = {}  # 将text中的字符位置映射到ctc_timestamps中的索引
        
        while text_pos < len(text) and ctc_idx < len(ctc_timestamps):
            char = text[text_pos]
            # 如果是标点符号或空格，跳过
            if char in '。，！？、；：」「""''（）【】《》<>{}[] \t\n\r':
                text_pos += 1
                continue
            # 如果是普通字符，建立映射
            if ctc_idx < len(ctc_timestamps) and ctc_timestamps[ctc_idx]["token"] == char:
                char_to_ctc_idx[text_pos] = ctc_idx
                ctc_idx += 1
            text_pos += 1
        
        # 根据标点符号位置分割文本
        start_text_pos = 0
        for break_idx in sentence_break_indices:
            if break_idx >= len(all_timestamps):
                # 处理到最后
                raw_segment_text = text[start_text_pos:]
            else:
                # 找到下一个非标点符号字符的位置
                next_non_punct_pos = break_idx
                while next_non_punct_pos < len(all_timestamps) and all_timestamps[next_non_punct_pos]["token"] in ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';', '：', ':']:
                    next_non_punct_pos += 1
                
                raw_segment_text = text[start_text_pos:next_non_punct_pos]
            
            if raw_segment_text.strip():
                # 从raw_segment_text中移除标点符号，只保留纯文本
                segment_text = ''.join([char for char in raw_segment_text if char not in '。，！？、；：」「""''（）【】《》<>{}[] \t\n\r'])
                
                # 找到该段文本在ctc_timestamps中的起始和结束索引
                segment_start_time = None
                segment_end_time = None
                segment_words = []
                
                for text_pos in range(start_text_pos, min(start_text_pos + len(raw_segment_text), len(text))):
                    char = text[text_pos]
                    # 跳过标点符号和空格
                    if char in '。，！？、；：」「""''（）【】《》<>{}[] \t\n\r':
                        continue
                    
                    if text_pos in char_to_ctc_idx:
                        ctc_idx = char_to_ctc_idx[text_pos]
                        if ctc_idx < len(ctc_timestamps):
                            ctc_item = ctc_timestamps[ctc_idx]
                            if segment_start_time is None:
                                segment_start_time = ctc_item["start_time"]
                            segment_end_time = ctc_item["end_time"]
                            
                            segment_words.append({
                                "word": char,
                                "start": round(ctc_item["start_time"], 2),
                                "end": round(ctc_item["end_time"], 2),
                                "probability": min(ctc_item.get("score", 0.0), 1.0)
                            })
                
                if segment_start_time is not None and segment_end_time is not None and segment_text.strip():
                    segment = {
                        "id": len(segments),
                        "seek": 0,
                        "start": round(segment_start_time, 2),
                        "end": round(segment_end_time, 2),
                        "text": segment_text,
                        "tokens": list(range(len(segment_text))),  # 占位符
                        "temperature": 0.2,
                        "avg_logprob": -0.12659429331294825,
                        "compression_ratio": 1.4195121951219511,
                        "no_speech_prob": 0.312889039516449,
                        "words": segment_words
                    }
                    segments.append(segment)
            
            # 更新下一个段的开始位置
            start_text_pos = next_non_punct_pos if break_idx < len(all_timestamps) else len(text)
    
    elif all_timestamps:
        # 如果没有ctc_timestamps，使用原始的timestamps
        import re
        
        # 颢先预处理，找出所有标点符号位置（包括句号和逗号等）
        sentence_break_indices = []
        for i, ts_item in enumerate(all_timestamps):
            token = ts_item["token"]
            if token in ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';', '：', ':']:  # 包括逗号等
                sentence_break_indices.append(i)
        
        # 添加末尾索引
        sentence_break_indices.append(len(all_timestamps))
        
        start_idx = 0
        for end_idx in sentence_break_indices:
            # 处理从start_idx到end_idx-1的字符
            segment_words = []
            segment_text = ""
            segment_start = None
            segment_end = None
            
            for j in range(start_idx, min(end_idx, len(all_timestamps))):
                ts_item = all_timestamps[j]
                token = ts_item["token"]
                start_time = ts_item["start_time"] / 1000.0  # 转换为秒
                end_time = ts_item["end_time"] / 1000.0      # 转换为秒
                score = ts_item.get("score", 0.0)
                
                # 记录段落的开始和结束时间
                # 只有当token不是标点符号时才更新开始时间
                if segment_start is None and token not in ['。', '！', '？', '.', '!', '?', '，', ',', '；', ';', '：', ':', ' ', '　']:
                    segment_start = start_time
                segment_end = end_time  # 更新为最后一个字符的结束时间
                
                segment_text += token
                segment_words.append({
                    "word": token,
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "probability": min(score, 1.0)  # 确保概率不超过1
                })
            
            # 如果segment_start仍为None（比如整个片段都是标点符号），则使用第一个字符的时间
            if segment_start is None and segment_text.strip():
                if len(segment_words) > 0:
                    segment_start = segment_words[0]["start"]
            
            # 只建段落
            if segment_text.strip():
                segment = {
                    "id": len(segments),
                    "seek": 0,
                    "start": round(segment_start, 2),
                    "end": round(segment_end, 2),
                    "text": segment_text,
                    "tokens": list(range(len(segment_text))),  # 占位符
                    "temperature": 0.2,
                    "avg_logprob": -0.12659429331294825,
                    "compression_ratio": 1.4195121951219511,
                    "no_speech_prob": 0.312889039516449,
                    "words": segment_words
                }
                segments.append(segment)
            
            start_idx = end_idx  # 移动到下一个段落的开始
    
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