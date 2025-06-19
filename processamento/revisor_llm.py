import re
from typing import List, Tuple, Union, Any
from utils.config import TEMPERATURE, PROMPT_TEMPLATE
from utils.log_helpers import log_limpeza_perigosa
from modelo.carregador import llm, tokenizer


def revisar_blocos_em_lote(blocos: List[str], nome_base: str = "") -> Tuple[List[str], int, int, int, int, int]:
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

    revisados_1try = 0
    revisados_2try = 0
    mantidos_originais = 0

    max_entrada = max((len(tokenizer(b).input_ids) for b in blocos if b.strip()), default=0)
    fator = 1.2 if max_entrada > 200 else 1.0
    max_tokens = max(min(768, int(max_entrada * fator)), 128)

    prompts = [PROMPT_TEMPLATE.format(bloco=b) for b in blocos]
    respostas = llm(prompts, max_new_tokens=max_tokens, temperature=TEMPERATURE)

    if not isinstance(respostas, list):
        raise ValueError("Modelo não retornou uma lista de respostas.")

    for i, (saida, original) in enumerate(zip(respostas, blocos)):
        try:
            if isinstance(saida, list) and saida:
                saida = saida[0]

            texto = saida.get("generated_text", "") if isinstance(saida, dict) else str(saida or "")
            texto = limpar_resposta(texto, nome_base=nome_base, indice_bloco=i)

            texto_limpo = texto.strip()

            if texto_limpo and len(texto_limpo.split()) >= len(original.strip().split()) * 0.5:
                revisados[i] = texto_limpo
                revisados_1try += 1
            else:
                fallback_indices.append(i)


        except Exception:
            fallback_indices.append(i)

    if fallback_indices:
        blocos_erro = [blocos[i] for i in fallback_indices]
        prompts_2 = [PROMPT_TEMPLATE.format(bloco=b) for b in blocos_erro]

        respostas_2 = llm(prompts_2, max_new_tokens=max_tokens, temperature=0.5)

        if not isinstance(respostas_2, list):
            raise ValueError("2º try: modelo retornou tipo inesperado.")

        for local_idx, saida in enumerate(respostas_2):
            global_idx = fallback_indices[local_idx]
            try:
                if isinstance(saida, list) and saida:
                    saida = saida[0]

                texto = saida.get("generated_text", "") if isinstance(saida, dict) else str(saida or "")
                texto = limpar_resposta(texto, nome_base=nome_base, indice_bloco=global_idx)
                
                texto_limpo = texto.strip()
                original = blocos[global_idx]

                if texto_limpo and len(texto_limpo.split()) >= len(original.strip().split()) * 0.5:
                    revisados[global_idx] = texto_limpo
                    revisados_2try += 1
                else:
                    revisados[global_idx] = original.strip()
                    mantidos_originais += 1


            except Exception:
                revisados[global_idx] = blocos[global_idx]
                mantidos_originais += 1

    tokens_saida = sum(len(tokenizer(t).input_ids) for t in revisados if t.strip())
    erros_fallback = mantidos_originais

    return revisados, erros_fallback, tokens_saida, revisados_1try, revisados_2try, mantidos_originais

def limpar_resposta(texto: str, nome_base: str = "", indice_bloco: int = -1) -> str:
    """
    Limpa e sanitiza a resposta gerada pela LLM, mantendo apenas conteúdo válido.
    Remove artefatos técnicos, tags e mensagens automáticas finais.
    Garante espaçamento simples, sem linhas em branco extras.
    """
    # 1. Garante presença do marcador
    if "<|im_start|>assistant" not in texto:
        return ""  # força fallback

    texto = texto.rsplit("<|im_start|>assistant", 1)[-1]

    # 2. Remove tags e marcações técnicas
    texto = re.sub(r"<\|im_.*?\|>", "", texto)
    texto = re.sub(r"<start>", "", texto)
    texto = re.sub(r"<end>", "", texto)
    texto = re.sub(r"(?m)^(user|assistant):\s*", "", texto)
    texto = re.sub(r"<pad\d*>", "", texto)
    texto = re.sub(r"<pause>", "", texto)

    # 3. Remove mensagens automáticas finais
    paragrafos = texto.strip().split("\n")
    if paragrafos:
        ultimo = paragrafos[-1].strip().lower().rstrip(".")
        frases_finais_seguras = {
            "end", "the end", "to be continued", "the story continues"
        }
        palavras_revisao = (
            "clarity", "tone", "structure", "preserved", "corrections",
            "fixed", "capitalization", "rephrased", "edited", "punctuation",
            "grammar", "no further edits", "already clear", "no edits needed"
        )
        if (
            ultimo in frases_finais_seguras or
            sum(p in ultimo for p in palavras_revisao) >= 2
        ):
            paragrafos.pop()

    # 4. Monta texto final com espaçamento limpo
    texto_final = "\n".join(paragrafos).strip()
    texto_final = re.sub(r"\n{2,}", "\n", texto_final)

    # 5. Se limpeza eliminar tudo, registra
    if not texto_final:
        log_limpeza_perigosa("arquivo_desconhecido", -1, texto, texto_final)  # valores padrão se não quiser rastrear
        return "[❗ERRO: resposta eliminada pela limpeza]"


    return texto_final







