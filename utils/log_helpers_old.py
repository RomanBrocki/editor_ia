import os

def log_limpeza_perigosa(nome_base: str, indice_bloco: int, antes: str, depois: str):
    caminho = os.path.join("dados", "logs", "limpeza_perigosa.txt")
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(f"\n[🚫 BLOCO DELETADO PELA LIMPEZA] - {nome_base} | Bloco #{indice_bloco}\n")
        f.write(">>> ANTES DA LIMPEZA:\n" + antes + "\n")
        f.write(">>> DEPOIS DA LIMPEZA:\n" + depois + "\n")
        f.write("=" * 100 + "\n")
