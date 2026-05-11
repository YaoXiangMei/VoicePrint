"""
通用工具模块
包含常用的工具函数
"""

import json


def format_output(data, title=None):
    """
    格式化输出数据
    
    Args:
        data: 要输出的数据
        title: 输出标题（可选）
    """
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=4))
    else:
        print(data)
    
    if title:
        print('='*len(f"{'='*20} {title} {'='*20}"))


def print_analysis_result(analysis_result):
    """
    专门用于打印分析结果的格式化函数
    
    Args:
        analysis_result: 分析结果字典
    """
    print("\n" + "="*50)
    print("音频连贯性分析结果")
    print("="*50)
    
    if analysis_result.get('status') == 0:
        print(f"错误: {analysis_result.get('msg', '未知错误')}")
        return
    
    # 打印评分
    scores = analysis_result.get('scores', {})
    print("\n📊 评分详情:")
    for key, value_obj in scores.items():
        if isinstance(value_obj, dict) and 'label' in value_obj and 'value' in value_obj:
            print(f"  {value_obj['label']}: {value_obj['value']}")
    
    # 打印指标
    metrics = analysis_result.get('metrics', {})
    if metrics:
        print("\n📈 详细指标:")
        for key, value_obj in metrics.items():
            if isinstance(value_obj, dict) and 'label' in value_obj and 'value' in value_obj:
                print(f"  {value_obj['label']}: {value_obj['value']}")
    
    print("="*50)


def print_transcription_result(transcription_result, title="语音转写结果"):
    """
    专门用于打印转写结果的格式化函数
    
    Args:
        transcription_result: 转写结果字典
        title: 标题
    """
    print(f"\n{'='*20} {title} {'='*20}")
    
    if 'text' in transcription_result:
        print(f"转录文本: {transcription_result['text']}")
    
    if 'language' in transcription_result:
        print(f"检测语言: {transcription_result['language']}")
    
    if 'segments' in transcription_result:
        print(f"段落数量: {len(transcription_result['segments'])}")
    
    print('='*len(f"{'='*20} {title} {'='*20}"))