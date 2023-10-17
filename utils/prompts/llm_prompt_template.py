'''
This file implements prompt template for llama based models. 
Modify the prompt template based on the model you select. 
This seems to have significant impact on the output of the LLM.
'''

from langchain.memory import ConversationBufferMemory
from langchain.memory import MongoDBChatMessageHistory
from langchain.prompts import PromptTemplate
# this is specific to Llama-2. 

system_prompt = """You are a helpful assistant, you will use the provided context to answer user questions.
Read the given context before answering questions and think step by step. If you can not answer a user question based on 
the provided context, inform the user. Do your best to answer the question."""


def get_prompt_template(system_prompt=system_prompt, promptTemplate_type=None, history=False, memory_unit="base"):

    if promptTemplate_type=="llama":
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
        if history:
            instruction = """
            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {tools}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Context: {history}
            User: {question}"""

            prompt_template =  B_INST + SYSTEM_PROMPT + instruction + E_INST
            prompt = PromptTemplate(input_variables=["history", "question", "tools"], template=prompt_template)
        else:
            instruction = """
            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {tools}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            User: {question}"""

            prompt_template =  B_INST + SYSTEM_PROMPT + instruction + E_INST
            prompt = PromptTemplate(input_variables=["question", "tools"], template=prompt_template)

    else:
        # change this based on the model you have selected. 
        if history:
            prompt_template = system_prompt + """
            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {tools}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question
            
            Context: {history}
            User: {question}
            Answer:"""
            prompt = PromptTemplate(input_variables=["history", "question", "tools"], template=prompt_template)
        else:
            prompt_template = system_prompt + """
            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {tools}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            User: {question}
            Answer:"""
            prompt = PromptTemplate(input_variables=["question", "tools"], template=prompt_template)

    # Provide the connection string to connect to the MongoDB database
    connection_string = "mongodb://localhost:27017"

    message_history = MongoDBChatMessageHistory(
        connection_string=connection_string, session_id=memory_unit
    )

    memory = ConversationBufferMemory(
        input_key="question",
        memory_key="history", 
        chat_memory=message_history
    )

    return prompt, memory, 