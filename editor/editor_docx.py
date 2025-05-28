import os
import time
from docx import Document
from processamento.segmentador import segmentar_em_blocos
from processamento.revisor_llm import revisar_blocos_em_lote

def revisar_docx_otimizado(nome_arquivo: str):
    caminho_entrada = os.path.join("dados", "entrada", nome_arquivo)
    nome_base = os.path.splitext(nome_arquivo)[0]
    caminho_saida = os.path.join("dados", "saida", f"{nome_base}_revisado.docx")

    doc = Document(caminho_entrada)

    capitulos = []
    titulo_atual = None
    buffer = []

    for par in doc.paragraphs:
        if par.style.name in ("Heading 1", "Heading 2"):
            if titulo_atual and buffer:
                capitulos.append((titulo_atual, buffer))
                buffer = []
            titulo_atual = par.text.strip()
        else:
            texto = par.text.strip()
            if texto and texto != titulo_atual:
                buffer.append(texto)

    if titulo_atual and buffer:
        capitulos.append((titulo_atual, buffer))

    print(f"[📘] Total de capítulos identificados: {len(capitulos)}")

    novo_doc = Document()
    inicio_total = time.time()

    for i, (titulo, paragrafos) in enumerate(capitulos):
        print(f"\n[📖] Revisando capítulo {i+1}/{len(capitulos)}: {titulo}")
        tempo_passado = time.time() - inicio_total
        print(f"[⏱️] Tempo decorrido: {int(tempo_passado // 3600)}h {int((tempo_passado % 3600) // 60)}m")

        texto_capitulo = "\n".join(paragrafos).strip()
        blocos = segmentar_em_blocos(texto_capitulo, max_linhas=7)

        print(f"[📚] {len(blocos)} blocos a revisar no capítulo {i+1}")
        revisados = revisar_blocos_em_lote(blocos)

        if i > 0:
            novo_doc.add_page_break()

        novo_doc.add_paragraph(titulo, style="Heading 1")
        for bloco in revisados:
            for linha in bloco.split("\n"):
                novo_doc.add_paragraph(linha.strip()) if linha.strip() else novo_doc.add_paragraph("")

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    novo_doc.save(caminho_saida)

    duracao = time.time() - inicio_total
    minutos = duracao // 60
    segundos = duracao % 60

    print(f"\n[✓] Revisão concluída. Arquivo salvo em: {caminho_saida}")
    print(f"[⏱️] Tempo total: {duracao:.2f} segundos ({int(minutos)} min {int(segundos)} s)")
