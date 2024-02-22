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

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain


agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful assistant, answer me using a friendly tone, and add some emoji in answer"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
llm = ChatOpenAI(openai_api_key='123', organization="gluon-meson",
                 openai_api_base='https://0972-152-101-166-135.ngrok-free.app', model='gpt-3.5-turbo', temperature=0, streaming=False)

embeddings = OpenAIEmbeddings(openai_api_key='123', organization="gluon-meson",
                              openai_api_base='https://0972-152-101-166-135.ngrok-free.app', model='text-embedding-ada-002')

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import  StructuredTool

agent_tools=[StructuredTool.from_function(func=add, name="add", description="Call this to get the summary"),
             StructuredTool.from_function(func=multiply, name="multiply", description="Call this to get the product"),
             StructuredTool.from_function(func=power, name="power", description="Call this to get the power"),
             ]

agent = create_openai_tools_agent(llm, agent_tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

result = agent_executor.invoke({"input":"Take 3 to the fifth power and multiply that by the sum of twelve and three, then square the whole result"})
print(result["output"])