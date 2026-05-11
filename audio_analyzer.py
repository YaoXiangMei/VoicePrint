import json


class AudioAnalyzer:
    """音频分析器类，用于分析语音连贯性等指标"""
    
    def __init__(self, result):
        """
        初始化分析器
        
        Args:
            result: Whisper转写结果字典
        """
        self.result = result
        self.segments = self.result["segments"]
        self.full_text = self.result["text"].strip()
        self.pause_threshold = 3  # 长停顿时长阈值（秒）
    
    def get_total_audio_duration(self):
        """获取音频总时长"""
        if not self.segments:
            return 0
        return self.segments[-1]["end"]
    
    def get_sentence_count(self):
        """获取句子总数"""
        return len(self.segments)
    
    def get_total_chars(self):
        """获取总字数（不包含空格）"""
        return len(self.full_text.replace(" ", ""))
    
    def get_pauses(self):
        """计算所有句间停顿"""
        pauses = []
        for i in range(1, len(self.segments)):
            prev_end = self.segments[i-1]["end"]
            curr_start = self.segments[i]["start"]
            pause = curr_start - prev_end
            if pause > 0:
                pauses.append(pause)
        return pauses
    
    def get_filtered_pauses(self, max_pause=30):
        """获取过滤后的停顿时长（排除异常值）"""
        pauses = self.get_pauses()
        return [p for p in pauses if p < max_pause]
    
    def get_total_pause_time(self, max_pause=30):
        """获取总停顿时间"""
        filtered_pauses = self.get_filtered_pauses(max_pause)
        return sum(filtered_pauses)
    
    def get_pause_statistics(self):
        """获取停顿相关统计数据"""
        pauses = self.get_pauses()
        filtered_pauses = self.get_filtered_pauses()
        
        total_gaps = len(self.segments) - 1
        pause_count = len(filtered_pauses)
        avg_pause = sum(filtered_pauses) / total_gaps if total_gaps > 0 else 0
        long_pause_count = sum(1 for p in pauses if p >= self.pause_threshold)
        
        total_audio_duration = self.get_total_audio_duration()
        pause_ratio = sum(filtered_pauses) / total_audio_duration if total_audio_duration > 0 else 0
        
        return {
            'total_gaps': total_gaps,
            'pause_count': pause_count,
            'avg_pause': avg_pause,
            'long_pause_count': long_pause_count,
            'pause_ratio': pause_ratio
        }
    
    def get_avg_sentence_chars(self):
        """获取平均每句字数"""
        if not self.segments:
            return 0
        
        seg_texts = [s["text"].strip() for s in self.segments]
        seg_char_counts = [len(t.replace(" ", "")) for t in seg_texts]
        return sum(seg_char_counts) / len(seg_char_counts) if seg_char_counts else 0
    
    def get_speak_duration_and_speed(self):
        """获取有效说话时长和语速"""
        speak_duration = sum(s["end"] - s["start"] for s in self.segments)
        total_chars = self.get_total_chars()
        speed_chars_per_sec = total_chars / speak_duration if speak_duration > 0 else 0
        
        return speak_duration, speed_chars_per_sec
    
    def calculate_fragment_score(self):
        """计算语句破碎度评分"""
        avg_sentence_chars = self.get_avg_sentence_chars()
        
        if avg_sentence_chars < 5:
            fragment_score = 20
        elif avg_sentence_chars < 9:
            fragment_score = 40
        elif avg_sentence_chars <= 25:
            fragment_score = 80
        else:
            fragment_score = 60
        
        return fragment_score
    
    def calculate_pause_score(self):
        """计算停顿流畅度评分"""
        pause_stats = self.get_pause_statistics()
        avg_pause = pause_stats['avg_pause']
        long_pause_count = pause_stats['long_pause_count']
        
        if avg_pause < 0.6 and long_pause_count <= 1:
            pause_score = 85
        elif avg_pause < 1.0 and long_pause_count <= 3:
            pause_score = 60
        elif avg_pause < 1.5:
            pause_score = 35
        else:
            pause_score = 15
        
        return pause_score
    
    def calculate_coherence_score(self):
        """计算综合连贯分"""
        fragment_score = self.calculate_fragment_score()
        pause_score = self.calculate_pause_score()
        return round((fragment_score + pause_score) / 2, 1)
    
    def get_level_by_score(self, score):
        """根据分数获取连贯等级"""
        if score >= 75:
            return "语言连贯正常"
        elif score >= 50:
            return "轻度不连贯"
        elif score >= 25:
            return "中度不连贯"
        else:
            return "重度不连贯"
    
    def analyze(self):
        """执行完整的音频分析，返回简化版结果"""
        if not self.segments:
            return {"status": 0, "msg": "未识别到语音内容"}
        
        # 获取各项指标
        total_audio_duration = self.get_total_audio_duration()
        sentence_count = self.get_sentence_count()
        total_chars = self.get_total_chars()
        total_pause_time = self.get_total_pause_time()
        
        pause_stats = self.get_pause_statistics()
        avg_sentence_chars = self.get_avg_sentence_chars()
        speak_duration, speed_chars_per_sec = self.get_speak_duration_and_speed()
        
        fragment_score = self.calculate_fragment_score()
        pause_score = self.calculate_pause_score()
        total_coherence_score = self.calculate_coherence_score()
        level = self.get_level_by_score(total_coherence_score)
        
        # 返回简化版分析结果，使用英文键名和值对象形式
        return {
            "status": 1,
            "msg": "分析成功",
            "scores": {
                "fragment_score": {
                    "label": "语句破碎度评分",
                    "value": fragment_score
                },
                "pause_score": {
                    "label": "停顿流畅度评分",
                    "value": pause_score
                },
                "total_coherence_score": {
                    "label": "综合语言连贯总分",
                    "value": total_coherence_score
                },
                "level": {
                    "label": "连贯等级",
                    "value": level
                }
            },
            "metrics": {
                "sentence_count": {
                    "label": "句子总数",
                    "value": sentence_count
                },
                "total_chars": {
                    "label": "总字数",
                    "value": total_chars
                },
                "avg_sentence_chars": {
                    "label": "平均每句字数",
                    "value": round(avg_sentence_chars, 1)
                },
                "speed_chars_per_sec": {
                    "label": "语速(字/秒)",
                    "value": round(speed_chars_per_sec, 2)
                },
                "total_audio_duration": {
                    "label": "音频总时长(秒)",
                    "value": round(total_audio_duration, 2)
                },
                "speak_duration": {
                    "label": "有效说话时长(秒)",
                    "value": round(speak_duration, 2)
                },
                "avg_pause": {
                    "label": "平均句间停顿(秒)",
                    "value": round(pause_stats['avg_pause'], 2)
                },
                "long_pause_count": {
                    "label": "长停顿次数(≥3s)",
                    "value": pause_stats['long_pause_count']
                },
                "pause_ratio": {
                    "label": "停顿占总时长比例(%)",
                    "value": round(pause_stats['pause_ratio'] * 100, 2)
                }
            }
        }

def analyze_audio(result):
    """
    便捷函数：分析音频连贯性
    
    Args:
        result: Whisper转写结果字典
        
    Returns:
        分析结果字典
    """
    analyzer = AudioAnalyzer(result)
    return analyzer.analyze()


# 使用示例
if __name__ == "__main__":
    # 示例用法
    try:
        # 方法1: 使用便捷函数
        result = json.load(open("1747281149103.json", "r", encoding="utf-8"))
        result = analyze_audio(result)
        print(json.dumps(result, ensure_ascii=False, indent=4))
        
        # # 方法2: 使用类实例
        analyzer = AudioAnalyzer(result)
        result = analyzer.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=4))
        
        
    except Exception as e:
        print(f"错误: {e}")