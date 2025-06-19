import gc
import torch
from editor.editor_docx import revisar_docx_otimizado

# Lista de arquivos a serem revisados
arquivos_para_revisar = [
                        "Divine Emperor of Death 1901-2000.docx",
                        ]

# Executa revisão sequencialmente
for nome_arquivo in arquivos_para_revisar:
    revisar_docx_otimizado(nome_arquivo)
    # Liberação de memória após o arquivo
    gc.collect()    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
