"""
文本向量化和相似度计算模块
使用text2vec模型计算文本相似度
"""
import os
import math
from text2vec import SentenceModel


# 强制使用国内镜像，解决SSL/网络问题
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class TextSimilarityCalculator:
    """
    文本相似度计算器
    使用text2vec模型计算文本相似度
    """
    
    def __init__(self, model_name="shibing624/text2vec-base-chinese", standard_text=None):
        """
        初始化相似度计算器
        
        Args:
            model_name: text2vec模型名称
            standard_text: 标准描述文本
        """
        self.model = SentenceModel(model_name)
        self.standard_text = standard_text or "在厨房里，一位妈妈站在水槽边洗碗，水槽里的水溢出来流到了地上，她却没有注意到。另一边，一个男孩站在摇摇晃晃的凳子上，伸手去够橱柜里的饼干盒，想要拿饼干。旁边还有一个小女孩，担忧地看着男孩，好像在担心他会摔下来"
    
    def cos_sim(self, v1, v2):
        """
        余弦相似度计算
        """
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(a * a for a in v2))
        return dot / (norm1 * norm2)
    
    def calculate_similarity(self, patient_text):
        """
        计算患者描述与标准描述的相似度
        
        Args:
            patient_text: 患者描述文本
            
        Returns:
            相似度值
        """
        std_vec = self.model.encode(self.standard_text)
        pat_vec = self.model.encode(patient_text)
        similarity = self.cos_sim(std_vec, pat_vec)
        return similarity


# 便捷函数，保持简单接口
def calculate_similarity(patient_text):
    """
    计算患者描述与标准描述的相似度（便捷函数）
    
    Args:
        patient_text: 患者描述文本
        
    Returns:
        相似度值
    """
    calculator = TextSimilarityCalculator()
    return calculator.calculate_similarity(patient_text)


# 使用示例
if __name__ == "__main__":
    # 患者口述
    patient_text = "2025年运河收入GDP超7%，政府超20% 的财政收入都来自运河分红，港口、航运、物流更是牵一发而动身心的经济命脉。"
    
    # 使用便捷函数
    similarity = calculate_similarity(patient_text)
    print(f"相似度: {similarity}")
    
    # 也可以使用类实例（适用于多次调用的场景）
    calc = TextSimilarityCalculator()
    similarity = calc.calculate_similarity(patient_text)
    print(f"相似度: {similarity}")



