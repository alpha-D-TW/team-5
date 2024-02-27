import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.runnables.history import RunnableWithMessageHistory

st.set_page_config(page_title="Team 5", page_icon="📖")
st.title('🦜🔗 产品名称-占位')

# key
MEMORY_KEY = "chat_history"
INPUT_KEY = "question"

from langchain_community.chat_message_histories import StreamlitChatMessageHistory

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


# Set up the LangChain, passing in Message History
agent_prompt = ChatPromptTemplate.from_messages([
    ("ai", "You are an AI chatbot having a conversation with a human."),
    MessagesPlaceholder(variable_name=MEMORY_KEY),
    ("human", f"{INPUT_KEY}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    # https://python.langchain.com/docs/modules/agents/how_to/custom_agent#adding-memory
])

llm = ChatOpenAI(openai_api_key=openai_api_key, model='gpt-3.5-turbo', temperature=0, streaming=True)

agent_tools = [StructuredTool.from_function(func=add, name="add", description="Call this to get the summary"),
               StructuredTool.from_function(func=multiply, name="multiply", description="Call this to get the product"),
               StructuredTool.from_function(func=power, name="power", description="Call this to get the power"),
               ]

agent = create_openai_tools_agent(llm, agent_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

chain_with_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: msgs,
    input_messages_key=INPUT_KEY,
    history_messages_key=MEMORY_KEY,
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input("What is up?"):
    st.chat_message("human").write(prompt)
    print(prompt)
    config = {"configurable": {"session_id": "any"}}
    stream = chain_with_history.invoke({f"{INPUT_KEY}": prompt}, config)
    print("stream is: ")
    print(stream)
    print(stream['output'])
    output_value = stream['output']
    output_iterable = [output_value]
    st.chat_message("ai").write_stream(output_iterable)

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
