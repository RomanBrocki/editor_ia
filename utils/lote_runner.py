import subprocess

def revisar_com_subprocesso(nome_arquivo: str):
    """Reinicia o app.py passando o nome do arquivo como argumento"""
    subprocess.run(["python", "app.py", nome_arquivo])

