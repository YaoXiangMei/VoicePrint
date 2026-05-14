"""
批量测试文件
读取record目录中的录音文件，输出相似度和音频分析结果
"""
import json
import os
import sys
from pathlib import Path
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# 使用funasr转换器
from funasr_wrapper.converter import convert_speech_to_text
from funasr_wrapper.format_converter import funasr_to_whisper_format
from speech_processing.audio_analyzer import analyze_audio
from speech_processing.text_to_vec import calculate_similarity
from utils.output_formatter import format_output, print_analysis_result


def convert_numpy_types(obj):
    """
    递归转换numpy类型为Python原生类型，以便JSON序列化
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


def batch_test():
    print("开始批量测试...")
    
    # 获取record目录中的所有音频文件
    record_dir = Path("recording/danger/")
    audio_files = list(record_dir.glob("*.wav"))
    
    if not audio_files:
        print("未找到音频文件")
        return
    
    print(f"发现 {len(audio_files)} 个音频文件")
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n处理第 {i}/{len(audio_files)} 个文件: {audio_file.name}")
        
        try:
            # 1. 语音转文字 (使用funasr)
            print("  - 正在进行语音转文字...")
            funasr_result = convert_speech_to_text(str(audio_file))
            
            # 2. 将funasr结果转换为whisper格式，以便使用现有的analyze_audio方法
            whisper_format_result = funasr_to_whisper_format(funasr_result)
            
            # 3. 音频连贯性分析
            print("  - 正在进行音频连贯性分析...")
            analysis_result = analyze_audio(whisper_format_result)
            
            # 4. 计算文本相似度
            print("  - 正在计算文本相似度...")
            similarity = calculate_similarity(whisper_format_result['text'])
            
            # 5. 收集结果
            result = {
                'file_name': audio_file.name,
                'transcription': whisper_format_result['text'],
                'analysis': analysis_result,
                'similarity': similarity,
                'success': True
            }
            
            results.append(result)
            
            # 输出当前文件的结果
            print(f"  - 相似度: {similarity:.4f}")
            # 安全获取连贯性评分
            scores = analysis_result.get('scores', {})
            coherence_score = scores.get('total_coherence_score', {}).get('value', 'N/A')
            print(f"  - 连贯性评分: {coherence_score}")
            
        except Exception as e:
            print(f"  - 处理失败: {str(e)}")
            results.append({
                'file_name': audio_file.name,
                'error': str(e),
                'success': False
            })
    
    # 输出汇总结果
    print("\n" + "="*60)
    print("批量测试完成！汇总结果:")
    print("="*60)
    
    successful_count = sum(1 for r in results if r['success'])
    print(f"总文件数: {len(audio_files)}")
    print(f"成功处理: {successful_count}")
    print(f"失败数量: {len(audio_files) - successful_count}")
    
    print("\n详细结果:")
    print("-"*60)
    
    for result in results:
        if result['success']:
            print(f"文件: {result['file_name']}")
            print(f"  相似度: {result['similarity']:.4f}")
            # 安全地获取连贯性评分
            scores = result['analysis'].get('scores', {})
            coherence_score = scores.get('total_coherence_score', {}).get('value', 'N/A')
            level_value = scores.get('level', {}).get('value', 'N/A')
            print(f"  连贯性评分: {coherence_score}")
            print(f"  连贯等级: {level_value}")
            print(f"  转录文本: {result['transcription'][:100]}...")
            print("-" * 40)
        else:
            print(f"文件: {result['file_name']} - 处理失败: {result['error']}")
            print("-" * 40)
    
    # 保存结果到JSON文件（先转换numpy类型）
    output_file = "test/batch_test_results_danger.json"
    converted_results = convert_numpy_types(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_file}")


if __name__ == "__main__":
    batch_test()