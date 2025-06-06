# utils/logger.py

import os
from datetime import datetime

class LoggerProcesso:
    """
    Classe responsável por gerar e gerenciar arquivos de log durante a revisão.

    Registra por capítulo:
    - tempo,
    - blocos,
    - tokens de entrada e saída,
    - erros (fallbacks).

    E no final:
    - totais agregados,
    - tempo total.
    - tempo médio por capítulo.
    O log é salvo em 'dados/logs' com nome baseado no arquivo revisado e timestamp.
    """

    def __init__(self, nome_arquivo_base: str):
        """
        Cria o arquivo de log na pasta 'dados/logs'.

        Args:
            nome_arquivo_base (str): Nome base do arquivo revisado (sem .docx).
        """
        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.log_dir = os.path.join("dados", "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        self.log_path = os.path.join(self.log_dir, f"log_{nome_arquivo_base}_{data_hora}.txt")
        self.inicio = datetime.now()
        self.capitulos_info = []  # Cada item: (blocos, tokens_in, tokens_out, erros, duracao_segundos)

        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write(f"[📄] Arquivo: {nome_arquivo_base}.docx\n")
            f.write(f"[🕒] Início: {self.inicio.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def registrar_capitulo(self, titulo: str, blocos: int, tokens: int, erros: int, duracao_segundos: float, tokens_saida: int = 0):
        """
        Adiciona uma entrada no log para o capítulo atual.

        Args:
            titulo (str): Nome do capítulo.
            blocos (int): Quantidade de blocos revisados.
            tokens (int): Total de tokens de entrada.
            erros (int): Fallbacks registrados.
            duracao_segundos (float): Tempo gasto.
            tokens_saida (int): Total de tokens gerados pela revisão.
        """
        self.capitulos_info.append((blocos, tokens, tokens_saida, erros, duracao_segundos))
        tempo_fmt = f"{int(duracao_segundos // 60)}m {int(duracao_segundos % 60)}s"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"-- {titulo} --\n")
            f.write(f"Blocos: {blocos}\n")
            f.write(f"Tokens (entrada): {tokens:,}\n")
            f.write(f"Tokens (saída):   {tokens_saida:,}\n")
            f.write(f"Erros (fallback): {erros}\n")
            f.write(f"Tempo: {tempo_fmt}\n\n")

    def finalizar_log(self):
        """
        Consolida os totais ao final do processo, incluindo:
        - tempo total,
        - blocos,
        - tokens de entrada e saída,
        - total de erros.
        """
        fim = datetime.now()
        total_segundos = (fim - self.inicio).total_seconds()

        total_blocos = sum(b for b, _, _, _, _ in self.capitulos_info)
        total_tokens_in = sum(tin for _, tin, _, _, _ in self.capitulos_info)
        total_tokens_out = sum(tout for _, _, tout, _, _ in self.capitulos_info)
        total_erros = sum(e for _, _, _, e, _ in self.capitulos_info)

        media_capitulo = total_segundos / len(self.capitulos_info)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[✓] Fim: {fim.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de capítulos: {len(self.capitulos_info)}\n")
            f.write(f"Blocos totais: {total_blocos}\n")
            f.write(f"Tokens totais (entrada): {total_tokens_in:,}\n")
            f.write(f"Tokens totais (saída):   {total_tokens_out:,}\n")
            f.write(f"Erros totais (fallback): {total_erros}\n")
            f.write(
                f"Tempo total: {int(total_segundos // 3600)}h {int((total_segundos % 3600) // 60)}m {int(total_segundos % 60)}s\n"
            )
            f.write(f"Tempo médio por capítulo: {int(media_capitulo // 60)}m {int(media_capitulo % 60)}s\n")
