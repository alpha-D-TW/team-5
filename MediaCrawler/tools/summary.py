import json
import os
import re


def filter_data(data, regex_pattern):
    filtered_data = []
    regex = re.compile(regex_pattern)
    for item in data:
        # 判断 item 是否匹配正则表达式
        if regex.match(json.dumps(item, ensure_ascii=False)):
            filtered_data.append(item)
    print(f"正则过滤后的数据共有{len(filtered_data)}条")
    return filtered_data


def deduplicate_by_title(json_data):
    unique_titles = set()
    deduplicated_data = []

    for entry in json_data:
        title = entry.get("title")
        if title and title not in unique_titles:
            unique_titles.add(title)
            deduplicated_data.append(entry)
    print(f"去重后的数据共有{len(deduplicated_data)}条")
    return deduplicated_data


def merge_json_files(directory, output_file, regex_pattern=None):
    all_data = []

    # 遍历目录下的所有json文件
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)

            # 读取json文件内容并添加到列表中
            with open(file_path, 'r', encoding='utf-8') as file:
                file_data = json.load(file)
                all_data.extend(file_data)
    print(f"原始数据共有{len(all_data) }条")

    # 如果提供了正则表达式模式，则进行数据过滤
    print(f"使用的正则规则是{regex_pattern}")

    if regex_pattern:
        all_data = filter_data(all_data, regex_pattern)
    deduplicated_data = deduplicate_by_title(all_data)
    # 将合并后的数据写入新的json文件
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(deduplicated_data, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 设置目录、输出文件名和正则表达式模式（可选）
    # directory_path = "xhs"
    # output_file_path = "regex.json"
    directory_path = "../data/xhs"  # 注意这里的路径是相对于 summary.py 文件的位置
    output_file_path = "../data/mergeJsonFile/merge.json"
    regex_pattern = r'.*(招行|白金卡|招白).*'

    # 执行合并操作
    merge_json_files(directory_path, output_file_path, regex_pattern)
    print(f"合并完成，结果保存在 {output_file_path}")

    with open(output_file_path, 'r', encoding='utf-8') as merged_file:
        merged_data = json.load(merged_file)
        num_records = len(merged_data)
    print(f"合并后的 JSON 数据共有 {num_records} 条记录。")
