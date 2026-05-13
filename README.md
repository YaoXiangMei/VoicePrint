# VoicePrint - 语音分析系统

一个用于分析语音连贯性的Python项目，使用Whisper模型进行语音转文字，然后分析语音的连贯性。

# funasr 错误解决
[链接](https://github.com/modelscope/FunASR/issues/2794)
- transformers 未安装 — HuggingfaceTokenizer 需要它，uv add transformers 解决
- FunASRNano 未注册 — 模型类定义在 Fun-ASR GitHub 仓库的 model.py 中，不在 funasr pip 包内。下载了 model.- - py、ctc.py、tools/utils.py 到项目目录，并在脚本中 import model 触发注册
- openai-whisper 未安装 — SenseVoiceTokenizer 需要它，uv add openai-whisper 解决
- 时间戳格式不兼容 — FunASR 1.3.1 的 VAD 后处理期望 [[start, end], ...] 列表格式，而 Fun-ASR-Nano 返回字典格式 [{"start_time": ..., "end_time": ...}, ...]，修补了 auto_model.py 第 557 行添加了 isinstance 判断来兼容两种格式
```js
558                      +      if isinstance(t, dict):
559                      +         t["start_time"] += vadsegments[j][0]
560                      +         t["end_time"] += vadsegments[j][0]
561                      +     else:
```