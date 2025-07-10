# verifica_ambiente.py
import os

DATABASE_FILE = "tarefas.db"

# Pega o caminho absoluto da pasta onde o script está sendo executado
diretorio_atual = os.getcwd()
caminho_completo_db = os.path.join(diretorio_atual, DATABASE_FILE)

print("--- Verificação de Ambiente ---")
print(f"[*] O Python está trabalhando no diretório: {diretorio_atual}")
print(f"[*] O caminho completo do banco de dados é: {caminho_completo_db}")
print("-" * 30)

# Verifica se o arquivo de banco de dados existe neste caminho
if os.path.exists(caminho_completo_db):
    print(f"[!] Arquivo '{DATABASE_FILE}' encontrado. Tentando apagar...")
    try:
        os.remove(caminho_completo_db)
        print(f"[✓] Arquivo '{DATABASE_FILE}' apagado com SUCESSO.")
    except Exception as e:
        print(f"[X] ERRO ao tentar apagar o arquivo: {e}")
        print("[!] Por favor, apague o arquivo manualmente neste caminho e tente de novo.")
else:
    print(f"[✓] Arquivo '{DATABASE_FILE}' não foi encontrado. Ambiente limpo!")

print("\n--- Fim da Verificação ---")