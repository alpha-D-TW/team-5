import json

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from util import read_json_to_yaml

import pandas as pd
import numpy as np

from draw_chart import handle_openai_draw_chart


st.set_page_config(page_title="Team 5", page_icon="🦜")
st.title('🦜🔗 Credit Cards Reviews')


def get_local_data():
    with open('data/test.json', 'r', encoding='utf-8') as file:
        return json.load(file)


data = get_local_data()


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


def fetch_data(name) -> str:
    """返回信用卡相关的用评论数据"""
    zhaohang_keywords = ["招行", "招商银行"]
    nonghang_keywords = ["农行", "农业银行"]
    print(666,name)

# 判断 name 是否包含招商银行相关关键词
    if any(keyword in name for keyword in zhaohang_keywords):
     path = "./source-data/test.json"
    elif any(keyword in name for keyword in nonghang_keywords):
     path= "./source-data/test1.json"
    else:
     return 'error'
    data1=read_json_to_yaml(path)
    print(99999,data1)
    return "用户评论是：" + str(data1)


def draw_plot(data):
    """接受json data 数据画图"""
    df = pd.DataFrame(data)
    with st.expander("Show data"):
        st.write(df)
    column_names = ", ".join(df.columns)
    handle_openai_draw_chart(df, column_names)
    return "done"

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
               StructuredTool.from_function(func=draw_plot, name="draw_plot",
                                            description="接受json data 数据画图"),
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
if prompt := st.chat_input("信用卡数据画图"):
    st.chat_message("human").write(prompt)
    with st.spinner("Processing..."):
        print(prompt)
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"question": prompt}, config)
        print("response is: ")
        print(response)

        chart_data = pd.DataFrame(
            {
                "col1": np.random.randn(20),
                "col2": np.random.randn(20),
                "col3": np.random.choice(["A", "B", "C"], 20),
            }
        )

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
