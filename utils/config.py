#from utils.prompt_parts import montar_prompt_template


# Nome do modelo Hugging Face
#MODEL_NAME = "teknium/OpenHermes-2.5-Mistral-7B"
MODEL_NAME = "NousResearch/Hermes-2-Pro-Mistral-7B"

# Temperatura do modelo (ajuste entre 0.35 e 0.8 conforme desejado)
TEMPERATURE = 0.35

# Prompt base usado para revisão
#PROMPT_TEMPLATE = montar_prompt_template() # resultado inferior
PROMPT_TEMPLATE = (
    "<|im_start|>system\n"
    "You are a strict literary editor of oriental fantasy webnovels. Your job is to improve readability while respecting original content.\n"
    "Do not remove or replace terms like 'magical beast', 'sword', 'cultivation', 'heart demon', 'blade', 'face', 'immortal', or 'dao'.\n"
    "Only correct spelling, punctuation, and grammar. Rephrase awkward or poorly structured sentences if it improves clarity, but do not invent new information.\n"
    "Preserve natural idiomatic expressions and emotional tone. Avoid replacing them with formal or mechanical alternatives.\n"
    "Never reassign dialogue. Preserve the paragraph structure.\n"
    "Avoid inserting commentary or summaries. Output only the corrected block.\n"
    "<|im_end|>\n"
    "<|im_start|>user\n<start>\n{bloco}\n<end>\n<|im_end|>\n"
    "<|im_start|>assistant\n"
)




# Definição de author para o ebook
AUTHOR = "editorAI"
