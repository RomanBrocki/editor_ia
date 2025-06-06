import re
from typing import List, Any
from utils.config import TEMPERATURE, PROMPT_TEMPLATE
from modelo.carregador import llm, tokenizer


def revisar_blocos_em_lote(blocos: List[str]) -> List[str]:
    """
    Envia blocos de texto para o modelo LLM revisar e retorna os textos corrigidos.
    
    Para cada bloco:
    - Monta um prompt com instruções.
    - Envia para o modelo.
    - Limpa artefatos indesejados da resposta.
    - Retorna a versão corrigida.

    Em caso de erro durante a chamada ou no processamento de um bloco:
    - O bloco original é mantido sem alteração.

    Args:
        blocos (List[str]): Lista de blocos de texto a serem revisados.

    Returns:
        List[str]: Lista de blocos revisados (ou originais em caso de erro).
    """

    # ============================
    # 🚧 GERAÇÃO DE PROMPTS
    # ============================

    prompts: List[str] = [
        PROMPT_TEMPLATE.format(bloco=bloco) for bloco in blocos if bloco.strip()
    ]

    if not prompts:
        return []

    # ============================
    # 📏 CÁLCULO DE TOKENS DE SAÍDA
    # ============================

    # Calcula o maior tamanho de entrada entre os blocos
    max_entrada = max((len(tokenizer(bloco).input_ids) for bloco in blocos if bloco.strip()), default=0)

    # Aplica margem apenas se o bloco for grande
    fator = 1.2 if max_entrada > 200 else 1.0
    max_tokens = max(min(768, int(max_entrada * fator)), 128)

    # ============================
    # 🚀 CHAMADA AO MODELO
    # ============================

    try:
        respostas: Any = llm(prompts, max_new_tokens=max_tokens, temperature=TEMPERATURE)
    except Exception as e:
        print(f"[❌] Erro global ao chamar o modelo: {e}")
        return blocos  # Fallback: retorna blocos intactos

    textos_revisados: List[str] = []

    # ============================
    # ✂️ PROCESSAMENTO INDIVIDUAL DAS RESPOSTAS
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
            # 🔽 Limpeza complementar de respostas automatizadas
            texto = re.sub(r"\(?No further edits needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r"\(?No changes needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)
            


            # ============================
            # ✅ SALVA TEXTO LIMPO OU ORIGINAL
            # ============================

            texto_limpo = texto.strip()
            textos_revisados.append(texto_limpo or original)

        except Exception as e:
            print(f"[⚠️] Erro ao processar bloco {i}: {e}")
            textos_revisados.append(original)  # Fallback: mantém o original

    return textos_revisados

