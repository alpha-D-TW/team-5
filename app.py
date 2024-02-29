import json
from typing import Dict, List

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
st.title('🦜🔗 Credit Cards Reviews')
st.set_option('deprecation.showPyplotGlobalUse', False)

def map_emotion_summary_data(data):
    # Initialize the summary object with counters for each category and emotion
    summary = {
        "CardCosts": [0, 0, 0],
        "RewardsProgram": [0, 0, 0],
        "CustomerService": [0, 0, 0],
        "AppUsability": [0, 0, 0],
        "Benefits": [0, 0, 0]
    }

    # Iterate through each item in the data list
    for item in data:
        # Extract the CreditCardExperience dictionary
        experience = item["CreditCardExperience"]
        # Iterate through each key in the experience dictionary
        for key, value in experience.items():
            # Map the emotion to the corresponding index in the summary
            # -1 maps to index 0 (negative), 0 maps to index 1 (neutral), 1 maps to index 2 (positive)
            emotion_index = value["emotion"] + 1
            # Increment the corresponding counter in the summary
            summary[key][emotion_index] += 1

    return "信用卡相关的用评论情感分析后的数据转化后的结果：" + str(summary)

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")  # 这里可以加开场白

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


CARD_MAP = {"招商银行经典白金卡": "file_1", "招商银行普通卡": "file_2"}


def fetch_data(card_key: str) -> str:
    if card_key in CARD_MAP:
        return load_json(CARD_MAP[card_key])
    else:
        print("error")


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
    return "用户评论是：" + str(json_data)


class DrawPlot_Model(BaseModel):
    category_names: List[str] = Field(description="list of str The category labels. category is the emotions list: 'positive', 'negative', 'neutral'")
    map_data: Dict[str, List[int]] = Field(
        description="传入对信用卡数据统计集合，类似这样的数据结构：{'Card Costs': [5, 5, 5], 'Rewards Program': [3, 5, 7], 'Customer Service': [5, 4, 6], 'App Usability': [4, 8, 3], 'Benefits': [1, 7, 7]}")


def draw_plot_func(category_names: List[str], map_data: Dict[str, List[int]]) -> str:
    """接受固定的数据格式画柱状图图-horizontal bar chart"""

    print("执行了draw_plot")
    print(category_names)
    print(map_data)
    message = st.chat_message("assistant")
    tab1, tab2 = message.tabs(["📈 Chart", "🗃 Data"])
    tab1.subheader("维度情感分析水平柱状图")
    category_names = ['positive', 'negative', 'neutral']
    arr_data = {'Card Costs': [5, 5, 5], 'Rewards Program': [3, 5, 7], 'Customer Service': [5, 4, 6], 'App Usability': [4, 8, 3], 'Benefits': [1, 7, 7]}
    survey(arr_data, category_names)
    plt.show()
    tab1.pyplot()

    tab2.subheader("数据Table")
    # 创建 DataFrame
    table_data = pd.DataFrame.from_dict(arr_data, orient='index', columns=category_names)
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
    openai_api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0, streaming=True
)


agent_tools = [
    StructuredTool.from_function(func=fetch_data, name="get_data",
                                 description="可以获取信用卡相关的用评论情感分析后的数据，要求输入具体的行用卡名称，比如招行信用卡，返回的是json data，是一个数组，一个对象就是对一个用户评论的分析结果"),
    StructuredTool.from_function(func=draw_plot_func, name="draw-plot-tool",
                                 args_schema=DrawPlot_Model,
                                 description="调用可以画图，一定要传入2个参数，第一个参数是emotions list: 'positive', 'negative', 'neutral'，第二个参数是统计的数据集，结构类似{'Card Costs': [5, 5, 5], 'Rewards Program': [3, 5, 7], 'Customer Service': [5, 4, 6], 'App Usability': [4, 8, 3], 'Benefits': [1, 7, 7]}的结构，可以画水平柱状图/horizontal bar chart"),
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

