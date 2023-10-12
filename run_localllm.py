import os
import logging
from langchain.llms import HuggingFacePipeline
from langchain.chains import LLMChain

# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from utils.agents.chain import normal_chain
from constants import (
    MODEL_ID,
    MODEL_BASENAME,
    MODELS_PATH,
)

device_type = 'cpu'
# show_sources = True
show_sources = False
use_history = True

def main(device_type=device_type, use_history=use_history):
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)

    chain = normal_chain(device_type, use_history, promptTemplate_type="llama")
    
    while True:
        query = input("\nEnter a query: ")
        if query.lower() == "exit":
            break

        answer = chain.run(query)
        
        result_folder = "./results/chain"
        num = len(os.listdir(result_folder))
        filenaming = f'query{num}.md'
        with open(os.path.join(result_folder, filenaming), 'w') as f:
            f.write(answer)

        print("\n\n> Question:")
        print(query)
        print("\n\n> Answer:")
        print(answer)



if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    main()