import re
from modelo.carregador import llm, tokenizer

def revisar_blocos_em_lote(blocos: list) -> list:
    prompt_template = (
        "<|im_start|>system\n"
        "You are a literary editor of oriental fantasy webnovels. Preserve names, exaggerated emotions, dramatic pacing, and poetic rhythm.\n"
        "Terms like 'sword', 'heart demon', 'blade', 'cultivation', 'dao', 'yin', 'demon', 'immortal', and 'spirit' are part of the genre and should be preserved as-is. Do not replace them with generic or Westernized alternatives.\n"
        "Retain all character dialogue and its structure. Never confuse who is speaking. Do not reassign dialogue to other characters.\n"
        "Only correct grammar or clarity when truly needed, and never simplify the emotional tone.\n"
        "Do not add archaic, poetic, or overly refined vocabulary if it is not already present in the original.\n"
        "Do NOT add commentary, summaries, explanations, or analysis. Do NOT rephrase entire blocks unless strictly necessary for clarity.\n"
        "Do NOT add sentences that were not in the original. Your output must contain ONLY the corrected version of the input, block by block.\n"
        "Use modern, natural English that matches the tone and style of the source material.\n"
        "Preserve paragraph structure and spacing unless there's a clear improvement.\n"
        "<|im_end|>\n"
        "<|im_start|>user\n<start>\n{bloco}\n<end>\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    prompts = [prompt_template.format(bloco=bloco) for bloco in blocos if bloco.strip() != ""]

    max_tokens = max(
        min(512, max(len(tokenizer(bloco, return_tensors=None).input_ids) for bloco in blocos if bloco.strip())),
        128
    )

    print(f"[🧪] Enviando {len(prompts)} blocos para revisão...")
    respostas = llm(prompts, max_new_tokens=max_tokens, temperature=0.7)
    print(f"[✅] Respostas recebidas. Processando blocos...\n")

    textos_revisados = []
    for i, saida in enumerate(respostas, 1):
        print(f"[✍️] Processando {i}/{len(respostas)}")

        if isinstance(saida, list):
            saida = saida[0]
        texto = saida["generated_text"]

        if "<|im_start|>assistant" in texto:
            texto = texto.split("<|im_start|>assistant")[-1]

        texto = re.sub(r"<\|im_.*?\|>", "", texto)
        texto = re.sub(r"<start>\n?", "", texto)
        texto = re.sub(r"\n?<end>", "", texto)
        texto = re.sub(r"You are a literary editor.*?source material\.\n", "", texto, flags=re.DOTALL)
        texto = re.sub(r"(?m)^(user|assistant):\s+(?=[a-zA-Z])", "", texto, flags=re.IGNORECASE)
        texto = re.sub(r"\n{2,}", "\n", texto.strip())

        textos_revisados.append(texto.strip())

    return textos_revisados
