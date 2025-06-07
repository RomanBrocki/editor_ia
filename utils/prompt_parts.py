persona = (
    "You are a strict literary editor of oriental fantasy webnovels. Your job is to improve readability while respecting original content.\n"
)

conteudo_preservado = (
    "Do not remove or replace terms like 'magical beast', 'sword', 'cultivation', 'heart demon', 'blade', 'face', 'immortal', or 'dao'.\n"
)

permissoes_e_limites = (
    "Only correct spelling, punctuation, and grammar. Do not add or rephrase unless clarity absolutely requires it.\n"
    "Preserve natural idiomatic expressions and emotional tone. Avoid replacing them with formal or mechanical alternatives.\n"
    "Never reassign dialogue. Preserve the paragraph structure.\n"
    "Avoid inserting commentary or summaries. Output only the corrected block.\n"
)



# o resultado do prompt composto se mostrou pior do que o direto.# Por isso, o prompt foi definido diretamente no config.py
def montar_prompt_template(bloco_placeholder="{bloco}") -> str:
    """
    Monta o prompt completo com blocos de instrução segmentados de forma semântica.

    Args:
        bloco_placeholder (str): Placeholder a ser substituído pelo conteúdo do bloco.

    Returns:
        str: Prompt formatado com instruções e estrutura compatível com o modelo.
    """
    system = (
        "<|im_start|>system\n"
        + persona
        + conteudo_preservado
        + permissoes_e_limites
        + "<|im_end|>\n"
    )
    user = f"<|im_start|>user\n<start>\n{bloco_placeholder}\n<end>\n<|im_end|>\n"
    assistant = "<|im_start|>assistant\n"
    return system + user + assistant
