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