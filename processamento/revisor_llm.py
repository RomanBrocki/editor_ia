import re
from utils.config import TEMPERATURE, PROMPT_TEMPLATE
from modelo.carregador import llm, tokenizer

def revisar_blocos_em_lote(blocos: list) -> list:
    """
    Envia blocos de texto para o modelo LLM revisar e retorna os textos corrigidos.

    Args:
        blocos (list): Lista de blocos de texto (strings) a serem revisados.

    Returns:
        list: Lista de textos revisados.
    """

    # Usa o template definido no config, com instruções específicas para revisão de webnovels
    prompt_template = PROMPT_TEMPLATE

    # Monta os prompts substituindo {bloco} dentro do template por cada bloco real
    prompts = [prompt_template.format(bloco=bloco) for bloco in blocos if bloco.strip() != ""]

    # Define o número máximo de tokens que o modelo pode retornar
    # Ajusta para não ultrapassar 512 e garante no mínimo 128
    max_tokens = max(
        min(512, max(len(tokenizer(bloco, return_tensors=None).input_ids) for bloco in blocos if bloco.strip())),
        128
    )

    print(f"[🧪] Enviando {len(prompts)} blocos para revisão...")
    
    # Chama o modelo para revisar os blocos, com temperatura definida na config
    respostas = llm(prompts, max_new_tokens=max_tokens, temperature=TEMPERATURE)
    print(f"[✅] Respostas recebidas. Processando blocos...\n")

    textos_revisados = []

    for i, saida in enumerate(respostas, 1):
        print(f"[✍️] Processando {i}/{len(respostas)}")

        # Se a saída vier como lista, pega o primeiro item
        if isinstance(saida, list):
            saida = saida[0]
        texto = saida["generated_text"]

        # Remove artefatos típicos do modelo e da formatação do prompt
        if "<|im_start|>assistant" in texto:
            texto = texto.split("<|im_start|>assistant")[-1]

        texto = re.sub(r"<\|im_.*?\|>", "", texto)
        texto = re.sub(r"<start>\n?", "", texto)
        texto = re.sub(r"\n?<end>", "", texto)
        texto = re.sub(r"You are a literary editor.*?source material\.\n", "", texto, flags=re.DOTALL)
        texto = re.sub(r"(?m)^(user|assistant):\s+(?=[a-zA-Z])", "", texto, flags=re.IGNORECASE)
        texto = re.sub(r"\n{2,}", "\n", texto.strip())

        # Guarda o texto limpo
        textos_revisados.append(texto.strip())

    return textos_revisados
