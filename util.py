import json
import yaml
import os

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

# 测试函数
# json_file_path = "./source-data/zhaohang-baijin-before.json"
# yaml_data = read_json_to_yaml(json_file_path)
# print(yaml_data)


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
    print(34,file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as existing_file:
            existing_data = json.load(existing_file)
    except FileNotFoundError:
            existing_data = []

    # 将新数据添加到现有数据中
    combined_data = existing_data + json_data

    # 将整合后的数据写回文件
    with open(file_path, 'w', encoding='utf-8') as json_file:
      json.dump(combined_data, json_file, ensure_ascii=False, indent=2)
    # 测试函数
    # file_name= 'test.json'
    # save_json_to_file(json_data, file_name)
