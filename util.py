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

    # 将数据保存到 JSON 文件
    # with open(file_path, 'w', encoding='utf-8') as json_file:
    #     json.dump(json_data, json_file, ensure_ascii=False, indent=2)
# 测试函数
json_data = [
    {"title": "招行经典白下卡流程与条件", "desc": "👉下卡流程\n去线下网点申请..."},
    {"title": "职场小白 招行经典白顺利下卡喽", "desc": "Timeline：\n12.7 晚上线下申请..."},
    {"title": "招行经典白申请分享", "desc": "  \n为什么写这个分享：\n最近发现小红书能搜到的干货居然挺多..."}
]
json_data2 = [
    {
        "title": "有了这两张白金信用卡，羊毛算是被我薅到了！",
        "desc": "白金信用卡的配卡思路，得根据每个人具体需求看，建议大家梳理下需要哪方面的权益和自己的收入/消费情况，再研究申请哪张卡～（不要盲目申请多张，防止多次征信记录等问题）\n\t\n👇讲讲我个人情况和配卡思路，提供参考\n\t\n-\n\t\n[拥抱R]我的需求：\n日常消费多（暂无车贷/房贷），热衷各地儿玩，想要信用卡积分兑里程，一年最好能薅2-3张机票；\n对体检、贵宾厅等权益无刚性需求，有则更好；\n可以低门槛免年费，不要刚性收取年费的卡；\n\t\n[打卡R]配卡思路：\n1⃣️由于我对“积分兑换里程”这件事是刚需，于是第一优先级找了南航联名白金卡（为啥是南航？因为从深圳飞，南航算是航线最多，且容易兑换的航司），最后选择了广发南航联名的精英白。\n\t\n核心原因是这张卡免年费门槛极低（首年刷3笔88元以上就能免），且信用卡消费的积分可自动兑换里程，开了加速包就是12:1（相当于消费12元兑换1里程，一般6k里程就能深圳飞三亚），里程自动兑换太吸引懒癌患者了！[赞R][赞R]\n\t\n2⃣️招行经典白算是白金卡的常青藤了，它的权益胜在“不废且稳定”，覆盖出行、医疗、保险等。6次贵宾厅、6次“300+精选酒店”贵宾入住权益，五星酒店自助餐买一赠一（很适合跟闺蜜一起），都是比较实用的～最重要的是年费很好免，生日当天刷两万左右，享受十倍积分。\n\t\n我现在打算日常消费主刷广发的卡，多兑里程，生日当天刷招行经典白～免年费的同时应薅尽薅，且也不用太费心管理信用卡[赞R]\n\t\n有疑问的小伙伴们多多交流呀！也求信用卡大神指点～\n\t\n            "
    },
    {
        "title": "招行经典白三战下卡",
        "desc": "屡败屡战[捂脸R]不容易，额度从8.1涨到10了  "
    }
]
json_data_str = '''
[
  {
    "title": "招行经典白下卡流程与条件",
    "desc": "👉下卡流程\n去线下网点申请，只能线下→申请一周后有人打电话来确认信息→等了10天开始审核，两周造成\n👉下卡条件\n就一条，招行代发工资。\n申请的时候有个客户经理说要存款50万，我一点存款也没有[笑哭R]想着资料都填了一半了随缘试试吧，结果过了。\n\t\n之前用招行的young卡，额度5万，这次下卡直接10万。\n提醒❗️现在招行不允许改生日了，只能身份证生日那天刷满免年费\n  "
  },
  {
    "title": "职场小白 招行经典白顺利下卡喽",
    "desc": "Timeline：\n12.7 晚上线下申请，随后一直处于待审核状态，等了10天一直没动静。\n12.18找了办卡的小姐姐，回复说卡在三审，可能是卡部业绩到了就在拖进度，然后帮我去催了一下。\n12.19 顺利放行 变成审核中\n12.20审核完成 只用了一天时间！\n12.21卡片寄出\n12.22收到卡\n\t\n申请的时候工作才刚1年多3个月，进件条件用的是招行代发，也刚满足3个月，没有用名下的车。下卡只用了一天真的是so surprised！额度给的是10个w~"
  },
  {
    "title": "招行经典白申请分享",
    "desc": "  \n为什么写这个分享：\n最近发现小红书能搜到的干货居然挺多，今天比较空我也分享下回馈下平台\n\t\n换卡背景：\n之前young卡用了几年，半年前收到信息邀请我换自由人生白金卡，但是随便搜了下都说鸟白有点鸡肋；经典白作为白金卡还行；于是想的有空就换个；但是这个申请貌似必须临柜（好麻烦），最近正好路过招行我就进去了\n\t\n我的背景：\n1.无招行银行卡，下了个app显示是M1....，我看网上说要M6?7?貌似？\n2.我只是偶尔刷刷young卡（所以网上说的申请条件我基本都不满足）\n\t\n申请过程：\n1.1第一天（周日）在大厅我给客户经理介绍了下我的诉求；\n1.2她说最好提供固定资产，现在不太好通过\n1.3我说我临时过来的就带个手机，过不了就算了\n1.4她说那你填下资料，仅填星号这种必填即可\n1.5拍了3个月的工资流水和税单\n2.1第二天（周一）客户经理打电话，问我岗位、职位并希望提供证明，然后我就截了个图发他\n3.1第三天（周二）有个信用卡中心的电话，核实了下我身份，问了我工作地址和职位\n4.1第四天（周三）收到短信已经核发\n\t\n我感觉网上说的条件真不一定准，有需要的小伙伴都可以去申请下试一试"
  }
]
'''
file_name= 'test.json'
save_json_to_file(json_data2,file_name)
