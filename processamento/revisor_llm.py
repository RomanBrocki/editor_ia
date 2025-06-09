import re
from typing import List, Tuple, Union, Any
from utils.config import TEMPERATURE, PROMPT_TEMPLATE
from modelo.carregador import llm, tokenizer


def revisar_blocos_em_lote(blocos: List[str]) -> Tuple[List[str], int, int, int, int, int]:
    """
    Envia blocos para revisão por LLM com fallback apenas em caso de erro real.

    O processo ocorre em duas etapas:
    1. Primeira tentativa (1º try): todos os blocos são enviados normalmente.
    2. Segunda tentativa (2º try): apenas os blocos com erro real (resposta vazia ou exceção)
       são reenviados com temperatura mais alta.

    A função classifica os blocos revisados por origem:
    - Revisado com sucesso no 1º try.
    - Revisado com sucesso no 2º try.
    - Mantido como original (casos com falha nos dois tries).

    Returns:
        Tuple contendo:
        - List[str]: blocos revisados finais na ordem original
        - int: total de blocos mantidos como original (fallback)
        - int: total de tokens gerados na saída
        - int: total de blocos revisados no 1º try
        - int: total de blocos revisados no 2º try
        - int: total de blocos mantidos sem revisão
    """
    if not blocos:
        return [], 0, 0, 0, 0, 0

    revisados = [""] * len(blocos)
    fallback_indices = []

    # Contadores por tipo de resolução
    revisados_1try = 0
    revisados_2try = 0
    mantidos_originais = 0

    # ============================
    # 📏 CÁLCULO DE TOKENS DE SAÍDA
    # ============================
    max_entrada = max((len(tokenizer(b).input_ids) for b in blocos if b.strip()), default=0)
    fator = 1.2 if max_entrada > 200 else 1.0
    max_tokens = max(min(768, int(max_entrada * fator)), 128)

    # ============================
    # 🚀 PRIMEIRA CHAMADA AO MODELO (1º TRY)
    # ============================
    prompts = [PROMPT_TEMPLATE.format(bloco=b) for b in blocos]
    respostas = llm(prompts, max_new_tokens=max_tokens, temperature=TEMPERATURE)
    if not isinstance(respostas, list):
        raise ValueError("Modelo não retornou uma lista de respostas.")


    # Verifica tipo de retorno para evitar quebra em tempo de execução
    if not isinstance(respostas, list):
        raise ValueError("Modelo não retornou uma lista de respostas.")

    for i, (saida, original) in enumerate(zip(respostas, blocos)):
        try:
            if isinstance(saida, list) and saida:
                saida = saida[0]

            texto = saida.get("generated_text", "") if isinstance(saida, dict) else str(saida or "")
            texto = limpar_saida(texto)

            if texto.strip():
                revisados[i] = texto.strip()
                revisados_1try += 1
            else:
                fallback_indices.append(i)

        except Exception as e:
            print(f"[⚠️] Erro ao processar bloco {i+1}: {e}")
            fallback_indices.append(i)

    # ============================
    # 🔁 SEGUNDA TENTATIVA PARA ERROS REAIS (2º TRY)
    # ============================
    if fallback_indices:
        blocos_erro = [blocos[i] for i in fallback_indices]
        prompts_2 = [PROMPT_TEMPLATE.format(bloco=b) for b in blocos_erro]

        respostas_2 = llm(
            prompts_2,
            max_new_tokens=max_tokens,
            temperature=0.6
        )
        if not isinstance(respostas_2, list):
            raise ValueError("2º try: modelo retornou tipo inesperado.")


        for local_idx, saida in enumerate(respostas_2):
            global_idx = fallback_indices[local_idx]
            try:
                if isinstance(saida, list) and saida:
                    saida = saida[0]

                texto = saida.get("generated_text", "") if isinstance(saida, dict) else str(saida or "")
                texto = limpar_saida(texto)

                if texto.strip():
                    revisados[global_idx] = texto.strip()
                    revisados_2try += 1
                else:
                    revisados[global_idx] = blocos[global_idx]
                    mantidos_originais += 1

            except Exception as e:
                print(f"[⚠️] Erro no bloco {global_idx+1} do 2º try: {e}")
                revisados[global_idx] = blocos[global_idx]
                mantidos_originais += 1

    # ============================
    # 📊 MÉTRICAS FINAIS
    # ============================
    tokens_saida = sum(len(tokenizer(t).input_ids) for t in revisados if t.strip())
    erros_fallback = mantidos_originais

    return revisados, erros_fallback, tokens_saida, revisados_1try, revisados_2try, mantidos_originais


# ============================
# 🧹 FUNÇÃO AUXILIAR: LIMPEZA DA SAÍDA
# ============================
def limpar_saida(texto: str) -> str:
    """
    Remove artefatos comuns da resposta do modelo e isola apenas a revisão.
    Garante que qualquer repetição do prompt ou marcação seja eliminada.
    """
    if "<|im_start|>assistant" in texto:
        texto = texto.split("<|im_start|>assistant", 1)[-1]

    texto = re.sub(r"<\|im_.*?\|>", "", texto)
    texto = re.sub(r"<start>\n?", "", texto)
    texto = re.sub(r"\n?<end>", "", texto)
    texto = re.sub(r"(?m)^(user|assistant):\s+(?=[a-zA-Z])", "", texto)
    texto = re.sub(r"\n{2,}", "\n", texto.strip())
    texto = re.sub(r"<pad\d*>", "", texto)
    texto = re.sub(r"<pause>", "", texto)
    texto = re.sub(r"\(?no changes needed\)?\.?", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\(?No further edits needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\(?No changes needed.*?\)?\.?", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"(?i)^\s*the end\s*$", "", texto, flags=re.MULTILINE)
    texto = re.sub(r"(?i)^ *(corrected|edited|fixes|changes|modifications):.*$", "", texto, flags=re.MULTILINE)
    return texto.strip()

