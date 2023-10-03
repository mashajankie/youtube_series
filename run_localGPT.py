import os
import logging
from langchain.llms import HuggingFacePipeline



# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from transformers import (
    GenerationConfig,
    pipeline,
)

from qa import retrieval_qa_pipline

from constants import (
    EMBEDDING_MODEL_NAME,
    PERSIST_DIRECTORY,
    MODEL_ID,
    MODEL_BASENAME,
    MAX_NEW_TOKENS,
    MODELS_PATH,
)

device_type = 'cpu'
# show_sources = True
show_sources = False
use_history = True

def main(device_type=device_type, show_sources=show_sources, use_history=use_history):
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)

    qa = retrieval_qa_pipline(device_type, use_history, promptTemplate_type="llama")
    while True:
        query = input("\nEnter a query: ")
        if query.lower() == "exit":
            break

        res = qa(query)
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