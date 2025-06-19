import re

def segmentar_em_blocos(texto: str, max_linhas: int = 7) -> list:
    """
    Divide o texto em blocos menores para enviar ao modelo LLM sem ultrapassar o limite.

    A divisão é feita por linha, agrupando até `max_linhas` por bloco, mas só quebra
    quando uma linha termina com pontuação típica de fim de frase (., ! ou ?),
    garantindo que o bloco faça sentido.

    Args:
        texto (str): Texto completo a ser segmentado.
        max_linhas (int): Número máximo de linhas por bloco (default é 7).

    Returns:
        list: Lista de blocos de texto prontos para revisão.
    """

    linhas = texto.strip().splitlines()  # Quebra o texto em linhas
    blocos = []                          # Lista final de blocos
    buffer = []                          # Acumula linhas até formar um bloco
    linhas_buffer = 0                   # Conta as linhas acumuladas

    for linha in linhas:
        if linha.strip():  # Se não for linha em branco
            buffer.append(linha.strip())
            linhas_buffer += 1

            # Se chegou no limite e a linha termina com pontuação de fim de frase
            if linhas_buffer >= max_linhas and re.search(r"[.!?][\"']?$", linha):
                blocos.append("\n".join(buffer))
                buffer = []
                linhas_buffer = 0


        else:
            # Se for linha em branco e já tem conteúdo no buffer, fecha o bloco
            if buffer:
                blocos.append("\n".join(buffer))
                buffer = []
                linhas_buffer = 0

    # Se sobrou conteúdo no buffer ao final, adiciona como último bloco
    if buffer:
        blocos.append("\n".join(buffer))

    return blocos
