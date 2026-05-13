import model
from funasr import AutoModel
import os

# 使用本地模型路径
model_dir = os.path.join(os.path.dirname(__file__), "..\\..\\models\\FunAudioLLM\\Fun-ASR-Nano-2512")

model = AutoModel(
    model=model_dir,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cpu",
)
# wav_path = "./dir/example/zh.mp3"
wav_path = "./recording/normal/1747281149103.wav"
res = model.generate(input=[wav_path], cache={}, batch_size_s=0)
text = res[0]["text"]
# 格式化输出到json文件，确保中文字符不乱码
import json
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=4)
print(res)