import re
from typing import List, Tuple, Any
from utils.config import TEMPERATURE, PROMPT_TEMPLATE
from modelo.carregador import llm, tokenizer


def revisar_blocos_em_lote(blocos: List[str]) -> Tuple[List[str], int, int]:
    """
    Envia blocos de texto para o modelo LLM revisar e retorna:
    - os textos corrigidos,
    - a quantidade de blocos com erro (fallbacks),
    - o total de tokens de saída.

    Para cada bloco:
    - Monta um prompt com instruções.
    - Envia para o modelo.
    - Limpa artefatos indesejados da resposta.
    - Em caso de erro, mantém o bloco original e contabiliza fallback.

    Args:
        blocos (List[str]): Lista de blocos de texto a serem revisados.

    Returns:
        Tuple:
            - List[str]: Lista de blocos revisados (ou originais em caso de erro).
            - int: Quantidade de blocos que falharam e foram mantidos (fallback).
            - int: Quantidade total de tokens nos blocos revisados.
    """

    # ============================
    # 🚧 GERAÇÃO DE PROMPTS
    # ============================

    prompts: List[str] = [
        PROMPT_TEMPLATE.format(bloco=bloco) for bloco in blocos if bloco.strip()
    ]

    if not prompts:
        return [], 0, 0

    # ============================
    # 📏 CÁLCULO DE TOKENS DE SAÍDA
    # ============================

    max_entrada = max((len(tokenizer(bloco).input_ids) for bloco in blocos if bloco.strip()), default=0)
    fator = 1.2 if max_entrada > 200 else 1.0
    max_tokens = max(min(768, int(max_entrada * fator)), 128)

    # ============================
    # 🚀 CHAMADA AO MODELO
    # ============================

    try:
        respostas: Any = llm(prompts, max_new_tokens=max_tokens, temperature=TEMPERATURE)
    except Exception as e:
        print(f"[❌] Erro global ao chamar o modelo: {e}")
        return blocos, len(blocos), sum(len(tokenizer(b).input_ids) for b in blocos)

    textos_revisados: List[str] = []
    erros_fallback = 0

    # ============================
    # ✂️ PROCESSAMENTO DAS RESPOSTAS
    # ============================

    for i, (saida, original) in enumerate(zip(respostas, blocos), 1):
        print(f"[✍️] Processando {i}/{len(respostas)}")
        try:
            # Alguns modelos retornam uma lista de dicionários
            if isinstance(saida, list) and saida:
                saida = saida[0]

            # Acesso seguro ao texto gerado
            if isinstance(saida, dict):
                texto = saida.get("generated_text", "")
            else:
                texto = str(saida) if saida is not None else ""

            # ============================
            # 🧹 LIMPEZA DE ARTEFATOS COMUNS
            # ============================

            if "<|im_start|>assistant" in texto:
                texto = texto.split("<|im_start|>assistant")[-1]

            texto = re.sub(r"<\|im_.*?\|>", "", texto)
            texto = re.sub(r"<start>\n?", "", texto)
            texto = re.sub(r"\n?<end>", "", texto)
            texto = re.sub(r"You are a literary editor.*?source material\.\n", "", texto, flags=re.DOTALL)
            texto = re.sub(r"(?m)^(user|assistant):\s+(?=[a-zA-Z])", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"\n{2,}", "\n", texto.strip())
            texto = re.sub(r"\(?no changes needed\)?\.?", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"<pad\d*>", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"<pause>", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"\(?No further edits needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"\(?No changes needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)

            # ============================
            # ✅ SALVA TEXTO LIMPO OU ORIGINAL
            # ============================

            texto_limpo = texto.strip()
            if not texto_limpo or texto_limpo == original.strip():
                erros_fallback += 1

            textos_revisados.append(texto_limpo or original)

        except Exception as e:
            print(f"[⚠️] Erro ao processar bloco {i}: {e}")
            textos_revisados.append(original)
            erros_fallback += 1

    # ============================
    # 🔢 CONTAGEM DE TOKENS DE SAÍDA
    # ============================

    tokens_saida = sum(len(tokenizer(t).input_ids) for t in textos_revisados if t.strip())

    return textos_revisados, erros_fallback, tokens_saida
