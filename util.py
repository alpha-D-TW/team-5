import json
import yaml

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
# json_file_path = "./source-data/zhaoshang-baijin.json"
# yaml_data = read_json_to_yaml(json_file_path)
# print(yaml_data)

