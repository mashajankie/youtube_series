import os
import logging

from utils.agents.agent_converse import agent_pipline

from constants import (
    MODELS_PATH,
)

device_type = 'cpu'
show_sources = False
use_history = True

def main(device_type=device_type, show_sources=show_sources, use_history=use_history):
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)

    agent = agent_pipline(device_type, use_history, memory_unit='project-piggy', promptTemplate_type="llama")
    while True:
        query = input("\nEnter a query: ")
        if query.lower() == "exit":
            break

        res = agent(query)
        answer, docs = res["result"], res["source_documents"]

        print("\n\n> Question:")
        print(query)
        print("\n\n> Answer:")
        print(answer)

        if show_sources:  
            print("----------------------------------SOURCE DOCUMENTS---------------------------")
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)
            print("----------------------------------SOURCE DOCUMENTS---------------------------")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    main()