import json
import yaml

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

st.set_page_config(page_title="Team 5", page_icon="🦜")
st.title('🦜🔗 Credit Cards Reviews')

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")  # 这里可以加开场白

view_messages = st.expander("View the message contents in session state")

# Get an OpenAI API Key before continuing
if "openai_api_key" in st.secrets:
    openai_api_key = st.secrets.openai_api_key
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Enter an OpenAI API Key to continue")
    st.stop()


def power(base: float, exponent: int) -> str:
    """计算基数的乘方并返回格式化字符串"""
    result = base ** exponent
    return f'{base}的{exponent}次方是{result}'


def add(number1: float, number2: float) -> str:
    """计算两个数的加法并返回格式化字符串"""
    result = number1 + number2
    return f'{number1}加上{number2}的结果是{result}'


def multiply(number1: float, number2: float) -> str:
    """计算两个数的乘法并返回格式化字符串"""
    result = number1 * number2
    return f'{number1}乘以{number2}的结果是{result}'

def dict_to_string(dictionary):
    return json.dumps(dictionary, indent=None)


def fetch_data() -> str:
    """返回信用卡相关的用评论数据"""
    data= [
        {
            "title": "招行经典白怎么用才能发挥最大价值？",
            "desc": "18年下的卡，5年了。每年会用一次体检，几次贵宾厅，偶尔订一两次酒店，每年权益都没刷满。平时也很少刷，生日的时候去刷物业费和充油卡，拿10倍积分。\n总感觉没能发挥最大价值，求资深卡友点拨一下[微笑R]\n    "
        },
        {
            "title": "招行经典白下卡",
            "desc": "一直佛系用卡，直到来到了成都工作，回家主要是天府机场，一不是东航主战场，VIP厅难用上了；二因为广发居然在天府没有贵宾厅，才开始打其他信用卡的主意。建行大山白和招行经典白，小红薯上比较了很久，决定先拿经典白。\n\t\n【申办条件】\n- 只能线下申办\n- 没有要求传说中的50砖，没有提供房本、车本\n- 提供的资料有：招行代发工资的流水，社保记录、公积金记录，已有招行信用卡的额度，劳动合同，名片\n3天下卡，原额度7.6W，新卡额度提到20W。\n\t\n【权益】\n我看上、且用得上的权益：\n- 6次贵宾厅，关键是可带人\n- 1次洗牙\n- 1次体检（可以给家人用）\n- 12次高尔夫练习场\n- 其他酒店啥的，我一个喜欢户外苦逼徒步路线的人，好像和大城市的豪华酒店缘分未到[偷笑R]\n\t\n【年费】\n3600/年，或1W积分免年费。\n目前招行信用卡在非主力卡的情况下，户头积分有4W多，免年费不是问题。\n\t\n权益截个屏，希望坚挺[加油R]\n\t\n "
        },
        {
            "title": "经典白销卡，招行再见👋🏻。",
            "desc": ""
        },
        {
            "title": "踏入大白金信用卡门槛，经典白get",
            "desc": "从第一张信用卡2500元的额度，到大白金，花了4年；招行可别让我失望啊！\n "
        },
        {
            "title": "经典白精粹白下卡成功，权益对比",
            "desc": "10月底同一天申请了农行精粹白和招行经典白，农行1周就下卡了，招行大概两周。\n对比了一下权益，好像还挺互补的，接下来就用一下看看[害羞R]\n除了机场vip，各有所长\n招行：高尔夫，酒店，洗牙，体检，机场延误险\n农行：兑换机票开通微信5倍积分后5：1很划算，预约看病，道路救援等必要时还是可以用的\n  "
        },
        {
            "title": "招商经典白下卡攻略｜权益",
            "desc": "🌈下卡攻略\nbase上海进件条件:50砖/1.8w税后收入。要去线下办卡不能网申。\n第一次办招商的信用卡，初次授信额度下的100k，无功无过吧~\n🌈权益（排名不分先后）\n1.体检1次（里面能选的不同体检中心，套餐会不一样，可以刷一刷选择性兑换）\n2.洗牙1次\n3.酒店6次贵宾价，还可叠加M+会员优惠券，三亚亚特兰蒂斯瞄了一眼一晚上不叠加券的基础上也比飞猪便宜3838元，还能连定两晚，正好去玩三天\n4.高尔夫12次，叠加金葵花可以一年打18次，可以带朋友一起玩，不过可选场地没有金葵花的多，比方说信用卡权益不能换黄兴VIP大包房\n5.五星级酒店自助餐买一送一，无限次\n6.机场贵宾厅6次，可带人（扣次数），经典白的权益能满足绝大部分需求，但没有金葵花能进的厅全\n对我来说这个次数太不够用了，但可以搭配其他无限次贵宾厅的卡用，无限次卡进不去的厅有些能用经典白进...下卡一个月就把六次用完了[哭惹R][哭惹R]\n\t\n🌈养卡成本（门槛）:生日当天刷💰22240\n非刚性年费3600，可以用1w积分抵扣。\n招商积分20元1分，比方说19.9元是没有积分的，比方说39.9只有1分，所以正常刷看似是消费20w能拿1w积分，实际可能需要30w+。\n所以养这个卡除了硬刚之外，绕不开生日十倍积分这件事，微信支付宝都有~如果办副卡的话副卡也有，所以生日当天能刷到22240就没压力，能多刷那多出来的分还可以换里程，实现商务舱自由~\n🌈另外注意\n蓝色软件积分是无上限的，绿色软件一年只给1w分，所以答应我，除了生日十倍之外，绿色软件平时一毛钱也不要刷经典白好吗？\n以下是我规划到时候攒积分的项目，反正免年费肯定是轻轻松松的:\n上海交通卡充值2000（天真了，我刚刚发现上限是1000元）\n燃气7200\n物业费6500\n电费5000（要通过网上国网app跳转zfb充值才有积分）\n水费600\n油费6000\n天猫超市卡、天猫购物金\n姐妹们注意每家每户每个模块消费金额肯定是不一样的，我这边主要交流一下思路，比方说燃气费我们家是开地暖的可能高一点[捂脸R]充钱之前按自己家实际情况单独计算一下哦\n🌈有其他预付费思路也可以评论分享哦"
        }
    ]
    return "用户评论是：" + dict_to_string(data)


# Set up the LangChain, passing in Message History
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI chatbot having a conversation with a human."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    # https://python.langchain.com/docs/modules/agents/how_to/custom_agent#adding-memory
])

llm = ChatOpenAI(openai_api_key=openai_api_key, model='gpt-3.5-turbo', temperature=0, streaming=True)

agent_tools = [StructuredTool.from_function(func=add, name="add", description="Call this to get the summary"),
               StructuredTool.from_function(func=multiply, name="multiply", description="Call this to get the product"),
               StructuredTool.from_function(func=power, name="power", description="Call this to get the power"),
               StructuredTool.from_function(func=fetch_data, name="get_data",
                                            description="可以获取信用卡相关的用评论数据"),
               ]

agent = create_openai_tools_agent(llm, agent_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

chain_with_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input("What is up?"):
    st.chat_message("human").write(prompt)
    print(prompt)
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    print("response is: ")
    print(response)
    st.chat_message("ai").write(response['output'])

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Message History initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
