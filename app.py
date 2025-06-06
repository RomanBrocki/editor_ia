from editor.editor_docx import revisar_docx_otimizado

# Lista de arquivos a serem revisados
arquivos_para_revisar = [
    "Divine Emperor of Death 1601-1700.docx",
    "Divine Emperor of Death 1701-1800.docx",
    "Divine Emperor of Death 1801-1900.docx"
]

# Executa revisão sequencialmente
for nome_arquivo in arquivos_para_revisar:
    revisar_docx_otimizado(nome_arquivo)
