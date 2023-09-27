import torch
from auto_gptq import AutoGPTQForCausalLM
from huggingface_hub import hf_hub_download
from langchain.llms import LlamaCpp

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LlamaForCausalLM,
    LlamaTokenizer,
)
from constants import CONTEXT_WINDOW_SIZE, MAX_NEW_TOKENS, N_GPU_LAYERS, N_BATCH, MODELS_PATH


def load_full_model(model_id, model_basename, device_type):
    model_path = hf_hub_download(
        repo_id=model_id,
        filename=model_basename,
        resume_download=True,
        cache_dir=MODELS_PATH,
    )
    kwargs = {
        "model_path": model_path,
        "n_ctx": CONTEXT_WINDOW_SIZE,
        "max_tokens": MAX_NEW_TOKENS,
        "n_batch": N_BATCH,  # set this based on your GPU & CPU RAM
    }
    if device_type.lower() == "mps":
        kwargs["n_gpu_layers"] = 1
    if device_type.lower() == "cuda":
        kwargs["n_gpu_layers"] = N_GPU_LAYERS  # set this based on your GPU

    return LlamaCpp(**kwargs)