import json

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

st.set_page_config(page_title="Team 5", page_icon="🦜")
st.title("🦜🔗 Credit Cards Reviews")

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")  # 这里可以加开场白

view_messages = st.expander("View the message contents in session state")

# Get an OpenAI API Key before continuing
# if "openai_api_key" in st.secrets:
#     openai_api_key = st.secrets.openai_api_key
# else:
#     openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
# if not openai_api_key:
#     st.info("Enter an OpenAI API Key to continue")
#     st.stop()
openai_api_key = "xxx"


# def load (key) => data

# desc: 接受一个可以直获取到对应的信用卡数据

# def mapKeys() => 
#     return [{
#         key: 'kye1',
#         desc: "卡一的 key"
#     }]
# desc : 可以获取

card_map = {
    "信用卡1": "1",
    "信用卡2": "2",
    "信用卡3": "3"
}

def return_card_filename(card_key: str) -> str:
    if card_key in card_map:
        return card_map[card_key]
    else:
        print("error")

def load_sentiment_json_file(card_name: str):
    """
    Args:
      json_file_path: JSON 文件路径
    """
    # # 读取 JSON 文件
    # with open(
    #     "./Data/tools/analysis-results/" + card_name + ".json", "r", encoding="utf-8"
    # ) as f:
    #     json_data = json.load(f)
    # # print(yaml_data)
    # return "用户评论是：" + str(json_data)
    print(card_name)


# def load_sentiment_json_file():
#     """
#     Args:
#       json_file_path: JSON 文件路径
#     """
#     # 读取 JSON 文件
#     with open("./Data/tools/analysis-results/test.json", "r", encoding="utf-8") as f:
#         json_data = json.load(f)
#     # print(yaml_data)
#     return "用户评论是：" + str(json_data)

# """分析信用卡相关用户评论数据"""
# def analyse_origin_sentiment():
#     client = OpenAI(
#             api_key=KEY,
#         )
#         content_str = '\n'.join(d['desc'] for d in content)


#         completion = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": PROMPT if prompt is None else prompt,
#                 },
#                 {
#                     "role": "user",
#                     "content": content_str,
#                 }
#             ],
#         )
#         json_result = json.loads(completion.choices[0].message.content)

#         print(json_result)
#         return json_result


# Set up the LangChain, passing in Message History
agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        # https://python.langchain.com/docs/modules/agents/how_to/custom_agent#adding-memory
    ]
)

llm = ChatOpenAI(
    openai_api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0, streaming=True
)


agent_tools = [
    StructuredTool.from_function(
        func=return_card_filename,
        name="get_card_name",
        description="根据用户输入的信用卡名称，生成一个键值对key，返回card_map的值value，如果返回的是 error，需要使用中文提示用户：输入错误，请重新输入",
    ),
        StructuredTool.from_function(
        func=load_sentiment_json_file,
        name="load_file_name",
        description="card_map的值value作为load_sentiment_json_file函数入参",
    )
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
    st.chat_message("ai").write(response["output"])

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
