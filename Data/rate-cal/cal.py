import json

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


def calculate_rate(data_from_generate, data_from_label):
    if len(data_from_label) != len(data_from_generate):
        return -1
    length = len(data_from_label)
    total_score = 0.0
    for i in range(0, length, 1):
        # print(total_json_data[i : i + loop_size])
        pre_data = data_from_generate[i]["CreditCardExperience"]
        label_data = data_from_label[i]["CreditCardExperience"]
        score = 0.0
        # print(pre_data)
        # print(label_data)
        for key in label_data.keys():
            if str(pre_data[key]) == str(label_data[key]):
                # print(pre_data[key])
                # print(label_data[key])
                score += 1
        cur_socre = score/len(label_data)
        print(f"{score/len(label_data):.4f}")
        total_score += cur_socre
    print(f"{total_score/length:.4f}")
 

        
        
if __name__ == '__main__':
    data_from_generate = read_json("../tools/大模型.json")
    data_from_label = read_json("../tools/人工.json")
    calculate_rate(data_from_generate=data_from_generate, data_from_label=data_from_label)

