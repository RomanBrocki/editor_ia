from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.pipelines import pipeline

from utils.config import MODEL_NAME
import torch

# ============================
# CONFIGURAÇÃO DO MODELO
# ============================

# Define o modelo que será carregado com base na variável de configuração
model_id = MODEL_NAME

# Carrega o tokenizer correspondente ao modelo
# `use_fast=False` evita erros com tokenizers acelerados que não suportam todos os modelos
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, use_fast=False)
tokenizer.padding_side = "left"  # Importante para modelos que usam entrada à esquerda (ex: LLaMA/Mistral)

# Carrega o modelo propriamente dito, mapeando automaticamente para CPU ou GPU
# Usa float16 para otimização de memória em CUDA
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

# Garante que o pad_token_id esteja definido para evitar warnings ou erros na geração
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id or model.config.eos_token_id

# Cria o pipeline do Hugging Face para geração de texto
# `batch_size=4` para envio em lote e `do_sample=True` permite temperatura funcionar
llm = pipeline("text-generation", model=model, tokenizer=tokenizer, batch_size=4, do_sample=True)

# Mostra em qual dispositivo (CPU/GPU) o modelo está rodando
print("[🖥️] Dispositivo:", next(model.parameters()).device)

