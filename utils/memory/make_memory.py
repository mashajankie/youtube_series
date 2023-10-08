'''
This file implements prompt template for llama based models. 
Modify the prompt template based on the model you select. 
This seems to have significant impact on the output of the LLM.
'''
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.memory import MongoDBChatMessageHistory
from langchain.prompts import PromptTemplate
# this is specific to Llama-2. 

def make_agent_memory(memory_unit="base", connection_string = "mongodb://localhost:27017"):

    # Provide the connection string to connect to the MongoDB database
    message_history = MongoDBChatMessageHistory(
        connection_string=connection_string, session_id=memory_unit
    )

    memory = ConversationBufferMemory(
        input_key="input",
        memory_key="chat_history", 
        chat_memory=message_history,
        return_messages=True
    )

    return memory