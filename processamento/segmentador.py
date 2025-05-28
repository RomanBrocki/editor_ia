import re

def segmentar_em_blocos(texto: str, max_linhas: int = 7) -> list:
    linhas = texto.strip().splitlines()
    blocos = []
    buffer = []
    linhas_buffer = 0

    for linha in linhas:
        if linha.strip():
            buffer.append(linha.strip())
            linhas_buffer += 1
            if linhas_buffer >= max_linhas and re.search(r"[.!?][\"']?$", linha):
                blocos.append("\n".join(buffer))
                buffer = []
                linhas_buffer = 0
        else:
            if buffer:
                blocos.append("\n".join(buffer))
                buffer = []
                linhas_buffer = 0

    if buffer:
        blocos.append("\n".join(buffer))

    return blocos
