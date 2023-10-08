from langchain.agents import AgentExecutor
from langchain.schema.agent import AgentFinish
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import tool
from utils.loader.load_models import load_full_model 
from constants import (
    EMBEDDING_MODEL_NAME,
    PERSIST_DIRECTORY,
    MODEL_ID,
    MODEL_BASENAME,
    MAX_NEW_TOKENS,
    MODELS_PATH,
)
from langchain.schema.messages import HumanMessage, AIMessage

chat_history = []
MEMORY_KEY = "chat_history"
device_type = 'cpu'
llm = load_full_model(model_id=MODEL_ID, model_basename=MODEL_BASENAME, device_type=device_type)

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

tools = [get_word_length]

from langchain.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are very powerful assistant, but bad at calculating lengths of words."),
    MessagesPlaceholder(variable_name=MEMORY_KEY),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

llm_with_tools = llm.bind(
    functions=[format_tool_to_openai_function(t) for t in tools]
)

agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_openai_functions(x['intermediate_steps']),
    "chat_history": lambda x: x["chat_history"]
} | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser()

# agent.invoke({
#     "input": "how many letters in the word educa?",
#     "intermediate_steps": []
# })

# intermediate_steps = []
# while True:
#     output = agent.invoke({
#         "input": "how many letters in the word educa?",
#         "intermediate_steps": intermediate_steps
#     })
#     if isinstance(output, AgentFinish):
#         final_result = output.return_values["output"]
#         break
#     else:
#         print(output.tool, output.tool_input)
#         tool = {
#             "get_word_length": get_word_length
#         }[output.tool]
#         observation = tool.run(output.tool_input)
#         intermediate_steps.append((output, observation))
# print(final_result)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

input1 = "how many letters in the word educa?"
result = agent_executor.invoke({"input": input1, "chat_history": chat_history})
chat_history.append(HumanMessage(content=input1))
chat_history.append(AIMessage(content=result['output']))
agent_executor.invoke({"input": "is that a real word?", "chat_history": chat_history})
