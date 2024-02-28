import os
import json
import yaml
from openai import OpenAI


##load file
def read_json_to_yaml(json_file_path):
    """
    Args:
      json_file_path: JSON 文件路径
    """
    # 读取 JSON 文件
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    yaml_data = yaml.dump(json_data, default_style='"', allow_unicode=True)
    return yaml_data


"""
循环调用 openai 获得对应的情感分析答案
:input:str(?) 爬虫得到的全部数据
:return:str 循环的到的所有分析结果 
"""


def loop(total_json_data, loop_size: int):
    if total_json_data is None:
        return
    lenth = len(total_json_data)
    # 按照输入 loop size 拆分 entry
    for i in range(0, lenth, int):
        response = chat_func(total_json_data[i : i + int])


##call openai and get response
def chat_func(content: str, prompt: str) -> str:
    client = OpenAI(
        api_key="xxx",
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
            },
            {
                "role": "user",
                "content": "Compose a poem that explains the concept of recursion in programming.",
            },
            {"content": content},
        ],
    )

    print(completion.choices[0].message)
    return completion


##response processing and save 写文件/处理
