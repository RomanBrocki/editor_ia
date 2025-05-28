from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# ============================
# CONFIGURAÇÃO DO MODELO
# ============================

model_id = "teknium/OpenHermes-2.5-Mistral-7B"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, use_fast=False)
tokenizer.padding_side = "left"

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id or model.config.eos_token_id

llm = pipeline("text-generation", model=model, tokenizer=tokenizer, batch_size=4, do_sample=True)
print("[🖥️] Dispositivo:", next(model.parameters()).device)
