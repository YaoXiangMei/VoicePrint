# VoicePrint - 语音分析系统

一个用于分析语音连贯性的Python项目，使用Whisper模型进行语音转文字，然后分析语音的连贯性。

## 项目结构

```
voiceprint/
├── src/
│   ├── __init__.py
│   ├── speech_processing/
│   │   ├── __init__.py
│   │   ├── speech_to_text_converter.py    # 语音转文字模块
│   │   └── audio_analyzer.py              # 音频分析模块
│   ├── utils/
│   │   ├── __init__.py
│   │   └── output_formatter.py            # 输出格式化工具
│   └── pipelines/
│       ├── __init__.py
│       └── voice_analysis_pipeline.py     # 语音分析流水线
├── main.py                                # 主程序入口
├── requirements.txt                       # 项目依赖
├── setup.py                              # 项目配置
└── README.md                             # 项目说明
```

## 功能特性

- **语音转文字**：使用Whisper模型将语音转换为文字
- **连贯性分析**：分析语音的连贯性，包括停顿、语速等指标
- **模型缓存**：避免重复加载模型，提高性能
- **格式化输出**：提供美观的分析结果输出

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 直接运行主程序

```bash
python main.py
```

### 在代码中使用

```python
from src.speech_processing.speech_to_text_converter import convert_speech_to_text
from src.speech_processing.audio_analyzer import analyze_audio

# 语音转文字
transcription_result = convert_speech_to_text("audio.wav")

# 连贯性分析
analysis_result = analyze_audio(transcription_result)
```

## 模块说明

### speech_to_text_converter.py
- `SpeechToTextConverter`类：语音转文字转换器
- `convert_speech_to_text()`函数：便捷的语音转文字函数

### audio_analyzer.py
- `AudioAnalyzer`类：音频分析器
- `analyze_audio()`函数：便捷的音频分析函数

### output_formatter.py
- `format_output()`函数：通用格式化输出
- `print_analysis_result()`函数：专门用于打印分析结果
- `print_transcription_result()`函数：专门用于打印转写结果

### voice_analysis_pipeline.py
- `VoiceAnalysisPipeline`类：整合语音转文字和分析的流水线
- `analyze_voice_coherence()`函数：一键完成语音分析