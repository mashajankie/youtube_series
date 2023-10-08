from langchain.agents import initialize_agent
from langchain.agents import Tool

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response

from utils.memory.make_memory import make_agent_memory
from utils.loader.load_models import load_full_model    
from constants import (
    MODEL_ID,
    MODEL_BASENAME,
)

from utils.agents.qa import retrieval_qa_pipline

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


def agent_pipline(device_type, use_history, memory_unit, promptTemplate_type="llama"):

    qa = retrieval_qa_pipline(device_type, use_history, promptTemplate_type=promptTemplate_type)
    tools = [
        Tool(
            name='Knowledge Base',
            func=qa.run,
            description=(
                'use this tool when answering general knowledge queries to get '
                'more information about the topic'
            )
        )
    ]
     


    # get the prompt template and memory if set by the user.
    conversational_memory = make_agent_memory(memory_unit=memory_unit)

    # load the llm pipeline
    llm = load_full_model(model_id=MODEL_ID, model_basename=MODEL_BASENAME, device_type=device_type)

    if use_history:
        # qa = LLMChain(llm=myllm, prompt=prompt)

        agent = initialize_agent(
            agent='chat-conversational-react-description',
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=10,
            early_stopping_method='generate',
            memory=conversational_memory
        )
        # qa = RetrievalQA.from_chain_type(
        #     llm=llm,
        #     chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
        #     retriever=retriever,
        #     return_source_documents=True,  # verbose=True,
        #     callbacks=callback_manager,
        #     chain_type_kwargs={"prompt": prompt, "memory": memory},
        # )
    else:
        # qa = LLMChain(llm=myllm, prompt=prompt)

        agent = initialize_agent(
            agent='chat-conversational-react-description',
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=10,
            early_stopping_method='generate',
        )
        # qa = RetrievalQA.from_chain_type(
        #     llm=llm,
        #     chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
        #     retriever=retriever,
        #     return_source_documents=True,  # verbose=True,
        #     callbacks=callback_manager,
        #     chain_type_kwargs={
        #         "prompt": prompt,
        #     },
        # )

    return agent
