import json
from typing import Dict, List,  Any

import pandas as pd
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from util import read_json_to_yaml, load_prompt_text

import matplotlib.pyplot as plt
from langchain.pydantic_v1 import BaseModel, Field

from draw_chart import handle_openai_draw_chart, survey

systerm_prompt = load_prompt_text()

print(systerm_prompt)

st.set_page_config(page_title="Team 5", page_icon="🦜")
st.title('Credit Cards Reviews')
st.set_option('deprecation.showPyplotGlobalUse', False)


# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("请输入您想要了解的信用卡产品名")  # 这里可以加开场白

# view_messages = st.expander("View the message contents in session state")

# Get an OpenAI API Key before continuing
if "openai_api_key" in st.secrets:
    openai_api_key = st.secrets.openai_api_key
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Enter an OpenAI API Key to continue")
    st.stop()


def dict_to_string(dictionary):
    return json.dumps(dictionary, indent=None)


CARD_MAP = {"招商银行经典白金卡": "file_1", "万事达": "file_2"}


def fetch_data(card_key: str) -> str:
    if card_key in CARD_MAP:
        return load_json(CARD_MAP[card_key])
    else:
        print("fetch_data没有找到对应数据")


def load_json(card_name: str):
    """
    Args:
      json_file_path: JSON 文件路径
    """
    # 读取 JSON 文件
    with open(
            "./Data/tools/analysis-results/" + card_name + ".json", "r", encoding="utf-8"
    ) as f:
        json_data = json.load(f)
    # print(yaml_data)
    st.spinner("获取到了数据，正在分析...")
    return "返回的是json data，是一个数组，一个对象就是对一个用户评论的分析结果。用户信用卡相关的评论，情感分析后的数据是：" + str(json_data)


class DrawBarChart_Model(BaseModel):
    category_names: List[str] = Field(description="list of str The category labels. category is the emotions list: 'positive', 'negative', 'neutral'")
    map_data: Dict[str, List[int]] = Field(
        description="传入对信用卡数据统计集合，输出Dict[str, List[int]]的python 结构体：{'Card Costs': [5, 5, 5], 'Rewards Program': [3, 5, 7], 'Customer Service': [5, 4, 6], 'App Usability': [4, 8, 3], 'Benefits': [1, 7, 7]}")


# def draw_plot_func(category_names: List[str], map_data: Dict[str, List[int]]) -> str:
def draw_bar_chart(category_names: List[str], map_data: Dict[str, List[int]]) -> str:
    """
    draw a horizontal chart
    """
    category_names = category_names
    map_data = map_data
    print("执行了draw_plot")
    print(category_names)
    print(map_data)
    message = st.chat_message("assistant")
    tab1, tab2 = message.tabs(["📈 Chart", "🗃 Data"])
    tab1.subheader("维度情感分析水平柱状图")
    # category_names = ['positive', 'negative', 'neutral']
    # arr_data = {'Card Costs': [5, 5, 5], 'Rewards Program': [3, 5, 7], 'Customer Service': [5, 4, 6], 'App Usability': [4, 8, 3], 'Benefits': [1, 7, 7]}
    survey(map_data, category_names)
    plt.show()
    tab1.pyplot()

    tab2.subheader("数据Table")
    # 创建 DataFrame
    table_data = pd.DataFrame.from_dict(map_data, orient='index', columns=category_names)
    tab2.write(table_data)
    return "图和表都展示完成了"


# Set up the LangChain, passing in Message History
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", systerm_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    # https://python.langchain.com/docs/modules/agents/how_to/custom_agent#adding-memory
])

llm = ChatOpenAI(
    openai_api_key=openai_api_key, model="gpt-4-turbo-preview", temperature=0, streaming=True
)


class DrawGeneralPlot_Model(BaseModel):
    chart_desc_text: str = Field(description="用户想画什么图，传入英文")
    data: str = Field(
        description="传入对信用卡数据统计集合即可，并字段附带描述和含义}")


agent_tools = [
    StructuredTool.from_function(func=fetch_data, name="fetch_data",
                                 description=f"可以获取用户信用卡相关的评论，情感分析后的数据。请根据输入信用卡关键字自动map传入，map数据是{dict_to_string(CARD_MAP)}"),
    StructuredTool.from_function(func=handle_openai_draw_chart, name="draw_general_plot",
                                 args_schema=DrawGeneralPlot_Model,
                                 description="根据描述，画图，要传入用户评论情感分析数据统计后的数据集和描述，要画什么图请提前关键字并翻译成英文传入"),
    StructuredTool.from_function(func=draw_bar_chart, name="draw_bar_chart",
                                 # args_schema=DrawPlot_Model,
                                 description="当用户想要柱状图时，使用这个工具画图，could draw a chart，given: { 'category_names': ['positive', 'negative', 'neutral'],'map_data': {'CardCosts': [5, 5, 5], 'RewardsProgram': [3, 5, 7], 'CustomerService': [5, 4, 6], 'AppUsability': [4, 8, 3], 'Benefits': [1, 7, 7]}} as parmas then it could draw horizontal bar chart"),

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
if prompt := st.chat_input("你可以输出一个信用卡：比如招行信用卡"):
    st.chat_message("human").write(prompt)
    with st.spinner("Processing..."):
        print(prompt)
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"question": prompt}, config)
        print("response is: ")
        print(response)

        st.chat_message("ai").write(response["output"])

# Draw the messages at the end, so newly generated ones show up immediately
# with view_messages:
#     """
#     Message History initialized with:
#     ```python
#     msgs = StreamlitChatMessageHistory(key="langchain_messages")
#     ```
#
#     Contents of `st.session_state.langchain_messages`:
#     """
#     view_messages.json(st.session_state.langchain_messages)

