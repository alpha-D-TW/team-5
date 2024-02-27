import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="Team 5", page_icon="📖")
st.title('🦜🔗 Credit Cards Reviews')

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


agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful assistant, answer me using a friendly tone, and add some emoji in answer"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = ChatOpenAI(openai_api_key=openai_api_key, model='gpt-3.5-turbo',
                 temperature=0, streaming=False)

# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# client = OpenAI(api_key=openai_api_key)

agent_tools = [StructuredTool.from_function(func=add, name="add", description="Call this to get the summary"),
               StructuredTool.from_function(func=multiply, name="multiply", description="Call this to get the product"),
               StructuredTool.from_function(func=power, name="power", description="Call this to get the power"),
               ]

agent = create_openai_tools_agent(llm, agent_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        print("messages:")
        print(st.session_state.messages)

        # 将消息列表转换为chat_history参数
        chat_history = []
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                chat_history.append(AIMessage(content=msg['content']))

        stream = agent_executor.invoke({"input": prompt,
                                        "chat_history": chat_history, })
        print("stream is: ")
        print(stream)
        print(stream['output'])
        output_value = stream['output']
        output_iterable = [output_value]
        response = st.write_stream(output_iterable)
    st.session_state.messages.append({"role": "assistant", "content": response})
