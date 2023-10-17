from utils.code.general.script import create_llm_result
import os
import logging
from utils.agents.agent_converse import agent_converse_pipline
from constants import (
    MODELS_PATH,
)

device_type = 'cpu'
show_sources = False
use_history = True

def main(device_type=device_type, use_history=use_history):
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)

    agent = agent_converse_pipline(device_type, use_history, memory_unit='project-converse-agent', promptTemplate_type="llama")

    while True:
        query = input("\nEnter a query: ")
        if query.lower() == "exit":
            break

        answer = agent(query)

        result_folder = "./results/converse"
        create_llm_result(result_folder, answer)

        print("\n\n> Question:")
        print(query)
        print("\n\n> Answer:")
        print(answer)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    main()