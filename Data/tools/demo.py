import os
import sys
import json
import yaml
from openai import OpenAI

#全局变量
FILE_NAME = 'test229-1.json'
PROMPT = """
Role: You as a professional data analyst, your expertise lies in interpreting the emotional nuances within user posts and categorizing their sentiments.

Background: Users share experiences with our bank's credit cards on social media and forums, discussing customer service, rewards, and app usability. This feedback is crucial for improving user satisfaction and product design. As a product manager, I aim to understand customer opinions to enhance our credit card services.

Task: Your objective is to distill key insights from user feedback on the "招商银行白金卡" (China Merchants Bank Platinum Card) and quantify the emotional valence of these insights. 
Requirements:

Emotion Analysis: Assign a SatisfactionScore between 0 and 10 based on the emotional tone of user comments, capturing the essence of their;

Insight Extraction: Delve into the reasons behind the assigned scores, identifying what aspects lead to user satisfaction or dissatisfaction. Highlight these findings in Chinese in the Strengths and Opportunities fields.

Dimensional Analysis: Evaluate user sentiments across five specific dimensions concerning the credit card's products and services. Assign a score on emotion (only on "-1", "0" , "1"; "-1" means bad experience on the dimensions; "0" means there is no explicit mention of the dimension, return ; "1" means good experience on the dimensions).

The five dimensions include:

CardCosts(持卡成本：账单周期，年费政策),
BenefitAllocation(生活权益，差旅权益),
PointsProgram(积分计划，积分权益),
ServiceGuarantee(人工服务，自助服务，安全保障),
AppExperience(关注用户在数字渠道的体验)
Output Format: only output json format

Relevance Filter: Exclude any feedback not directly related to the "招商银行白金卡”,”经典白”,”招商白金经典信用卡” stating: “Not related”Additional Instructions: Supplement your analysis with research to thoroughly understand the context and user experiences related to the "招商银行白金卡." Input Structure Example:[{"title": "Great Rewards Program","desc": "I love the rewards program, but the app is a bit clunky."},{"title": "High Fees","desc": "The card's benefits are good, but the high annual fee is disappointing."}]

Output Structure Example: [
{
"CreditCardExperience": {
"CardCosts": {
"emotion": Enum(-1, 0, 1),
},
// Other dimensions...
},
"SatisfactionAnalysis": {
"SatisfactionScore": Integer(0-10),
"Strengths": ["reason1", "reason2"],
"Opportunities": ["reason1", "reason2"],
}
},
// Additional objects for each input...
]
 Note: Replace reason1, reason2, etc., with the actual reasons you analyzed.
"""
KEY="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"

##load file
def read_json(json_file_path):
    """
    Args:
      json_file_path: JSON 文件路径
    """
    # 读取 JSON 文件
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    # print(yaml_data)
    return json_data

def tell_me_length(json_file_path):
    """
    Args:
      json_file_path: JSON 文件路径
    """
    # 读取 JSON 文件
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    print('length:',len(json_data))
    # return json_data


"""
循环调用 openai 获得对应的情感分析答案
:input:str(?) 爬虫得到的全部数据
:return:str 循环的到的所有分析结果 
"""


def loop(total_json_data, loop_size: int):
    if total_json_data is None:
        return
    lenth = len(total_json_data)
    print(lenth)
    # print(total_json_data)
    # 按照输入 loop size 拆分 entry
    for i in range(0, lenth, loop_size):
        # print(total_json_data[i : i + loop_size])
        response = chat_func(total_json_data[i : i + loop_size])
        save_json_to_file(response, FILE_NAME)



"""
调用 openai 获得对应的情感分析答案
:input:content 需要分析的爬虫数据
:input:prompt 爬虫得到的全部数据
:return:str ？

example:
输入
    prompt = "
    Role: As a professional data analyst, your expertise lies in identifying and classifying the emotions conveyed in user posts.

    Task: Your objective is to distill key information from the posts and conduct an emotional analysis based on specific criteria.

    Background: The focus of this analysis is on user sentiments surrounding the use of the "招商银行白金卡" (China Merchants Bank Platinum Card), also known colloquially as "经典白" and "招商白金经典信用卡."

    Requirements: Process an input consisting of an array of objects structured as { "title": string, "desc": string }[]. Your analysis should categorize the emotional sentiment across four distinct dimensions related to the credit card: Service Guarantee, Points Program, Benefit Allocation, and Card Costs.

    For each dimension, assess the emotion as -1 (negative), 0 (neutral/no mention), or 1 (positive), and extract the key phrases that justify this emotional rating. If a dimension is not explicitly mentioned, assign a 0 (neutral) and note "null" for the reasoning.

    Output Format: Provide an array of objects in the form:
    [ {"dimension_name": {"emotion": Enum(-1,0,1), "reason": ["keyword1", "keyword2"]}}, {"another_dimension_name": {"emotion": Enum(-1,0,1), "reason": ["keyword1"]}} ]

    Only include dimensions that have been analyzed. If the content does not pertain to the "招商银行白金卡," return the message: "The provided info is not related to 招商银行白金卡."
    "

    content = "招行钻石卡用腻了，而且觉得3600一年年费有点多，随手网申了大山白。居然四天就通过了，资产啥都没提供，甚至卡里余额常年0（工资卡，进账即转出系列）。不过额度就给了10w。用用看，看看是不是可以把招行淘汰掉～"

输出
ChatCompletion(id='chatcmpl-8x75AHAJ9nWfNHuC9j83UVx9EJUnv', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='[\n    {\n        "Card Costs": {\n            "emotion": -1,\n            "reason": ["3600一年年费有点多"]\n        }\n    },\n    {\n        "null": {\n            "emotion": 0,\n            "reason": ["The provided info is not related to 招商银行白金卡."]\n        }\n    }\n]', role='assistant', function_call=None, tool_calls=None))], created=1709099268, model='gpt-3.5-turbo-0125', object='chat.completion', system_fingerprint='fp_86156a94a0', usage=CompletionUsage(completion_tokens=79, prompt_tokens=488, total_tokens=567))
 
"""
##call openai and get response
def chat_func(content:dict, prompt:str=None):
    client = OpenAI(
        api_key=KEY,
    )
    content_str = '\n'.join(d['desc'] for d in content)


    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": PROMPT if prompt is None else prompt,
            },
            {
                "role": "user",
                "content": content_str,
            }
        ],
    )
    json_result = json.loads(completion.choices[0].message.content)

    print(json_result)
    return json_result


##response processing and save 写文件/处理
def save_json_to_file(json_data, file_name):
    """
    将 JSON 数据保存到指定文件

    Args:
        json_data (dict): 要保存的 JSON 数据
        file_name (str): 目标文件名

    Returns:
        None
    """
    # 确保 data 文件夹存在
    data_folder = "./analysis-results"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # 构造完整的文件路径
    file_path = os.path.join(data_folder, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as existing_file:
            existing_data = json.load(existing_file)
    except FileNotFoundError:
            existing_data = []

    # 将新数据添加到现有数据中
    existing_data += json_data
    # 将整合后的数据写回文件
    with open(file_path, 'w', encoding='utf-8') as json_file:
      json.dump(existing_data, json_file, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    tell_me_length("../../source-data/nonghang-jingcuibai.json")
    yaml_data = read_json("../test.json")
    loop(yaml_data, 1)
