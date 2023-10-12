from langchain.chains import LLMChain
from utils.loader.load_models import load_full_model 
from utils.prompts.llm_prompt_template import get_prompt_template
from constants import (
    MODEL_ID,
    MODEL_BASENAME,
    MODELS_PATH,
)

def normal_chain(device_type, use_history, promptTemplate_type="llama"):
    llm = load_full_model(model_id=MODEL_ID, model_basename=MODEL_BASENAME, device_type=device_type)
    prompt, memory = get_prompt_template(promptTemplate_type=promptTemplate_type, history=use_history, memory_unit='simple')
    # print(prompt.template)
    # print(memory.chat_memory)
    # input('continue')
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

    return chain