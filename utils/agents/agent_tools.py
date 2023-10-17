from langchain.agents.initialize import initialize_agent
from langchain.agents import Tool
from langchain.agents import AgentType

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from utils.memory.make_memory import make_agent_memory
from utils.loader.load_models import load_full_model    
from constants import (
    MODEL_ID,
    MODEL_BASENAME,
)

from utils.agents.qa import retrieval_qa_pipline
import os

os.environ["LANGCHAIN_TRACING"] = "true"

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

def multiplier(a, b):
    return a * b

def parsing_multiplier(string):
    a, b = string.split(",")
    return multiplier(int(a), int(b))

def agent_tool_pipline(device_type, use_history, memory_unit, promptTemplate_type="llama"):

    qa = retrieval_qa_pipline(device_type, use_history, promptTemplate_type=promptTemplate_type)
    tools = [
        Tool(
            name='Knowledge Base',
            func=qa.run,
            description=(
                'use this tool when answering general knowledge queries to get '
                'more information about the topic'
            )
        ),
        Tool(
            name="Multiplier",
            func=parsing_multiplier,
            description="useful for when you need to multiply two numbers together. The input to this tool should be a comma separated list of numbers of length two, representing the two numbers you want to multiply together. For example, `1,2` would be the input if you wanted to multiply 1 by 2.",
        )
    ]
     
    # get the prompt template and memory if set by the user.
    conversational_memory = make_agent_memory(memory_unit=memory_unit)

    # load the llm pipeline
    llm = load_full_model(model_id=MODEL_ID, model_basename=MODEL_BASENAME, device_type=device_type)

    if use_history:
        agent = initialize_agent(
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=10,
            early_stopping_method='generate',
            memory=conversational_memory,
            handle_parsing_errors=True
        )
    else:
        agent = initialize_agent(
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=10,
            early_stopping_method='generate',
        )

    return agent
