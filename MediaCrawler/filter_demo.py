import jieba
from jieba import posseg
import re
 
def compress_text(keyword):
    # 加载自定义字典（如果有）
    jieba.load_userdict("custom_dictionary.txt")
    
    # 对输入的文本进行分词并标注词性
    words = jieba.posseg.cut(keyword)
    
    compressed_text = ""
    for word in words:
        if word.flag == "nr" or word.flag == "ns":   # 只保留名词或地名作为关键词
            compressed_text += word.word + "/"
            
    return compressed_text[:-1]   # 去除最后多余的斜线符号
 
# 测试样例
input_text_1 = "一直是招行的忠实用户，基本得这一家银行用，觉得各方面体验感还可以。最近打算开始玩卡了，因为娃还小，就打算申一张可以积分抵年费的白金卡，之前使用的鸟白相对来说权益有点少。于是参考了网上一系列下卡门槛，感觉都能满足，在五一期间去找了客户经理提交申请。\n没想到提交了之后三天就给我拒了，找客服问就是一堆综合评估不符合标准的。我就不明白了，你告诉我哪里不符合，我可以补交材料，也不是一张门槛多高的卡。后面又找了客户经理问，说参考他行的信用卡额度和信贷情况不符合标准。那可不是吗，怪我只用你们家银行呗，这是逼着我去他行办卡啊。M7金葵花，月均资产200w，鸟白额度17W，我还提交了房产证和行驶证，一张入门白金卡都搞不定我还用你干嘛。\n跟客户经理大发了一顿火，立马转去建行开好户准备去搞大山白，然后客户经理一顿道歉重新提交去了，昨天通知下卡了。所以，就是欠骂是吧。平时太好弄了，一些有的没的礼品也无所谓，然后就糊弄客户了是吗？"
input_text_2 = "建行大山白，权益类似于交行，多了一个高端酒店预订（但据说今年提前结束了，很多人没享受到，差评[生气R]）点评批评建行，申请卡提示我补交材料，我当天就去网点补交了，结果等了20天才显示进入审批，将近一个月才下卡，效率极低，打电话加急也毫无用处。\n—\n以后就靠这几张信用卡超前消费才能艰难度日了[偷笑R][doge]"
# compressed_result = compress_text(input_text)
# print(compressed_result)


def pattern_text(text):
    pattern = re.compile(r'招行|白金卡|经典白金卡')
    if pattern.search(text):
        return text
    
    
output = pattern_text(input_text_2)
print(output)