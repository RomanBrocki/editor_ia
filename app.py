from editor.editor_docx import revisar_docx_otimizado

# Lista de arquivos a serem revisados
arquivos_para_revisar = ["teste 1-2.docx"]

# Executa revisão sequencialmente
for nome_arquivo in arquivos_para_revisar:
    revisar_docx_otimizado(nome_arquivo)
