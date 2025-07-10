# main.py
import os
import database as db
from database import StatusTarefa

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPressione Enter para continuar...")

# --- As funções abaixo não precisam de alteração de lógica ---
def adicionar_nova_tarefa():
    while True:
        limpar_tela()
        print("--- Adicionar Nova Tarefa ---")
        titulo = input("Digite o título da tarefa (ou 'sair' para voltar): ")
        if titulo.lower() == 'sair':
            break
        if not titulo:
            print("\nO título não pode ser vazio.")
        else:
            nova_tarefa = db.adicionar_tarefa(titulo)
            print(f"\nTarefa '{nova_tarefa.titulo}' (ID: {nova_tarefa.id}) adicionada com sucesso!")
        continuar = input("\nDeseja adicionar outra tarefa? (s/n): ").lower()
        if continuar != 's':
            break
    print("\nVoltando ao menu principal...")
    pausar()

def listar_todas_tarefas():
    limpar_tela()
    print("--- Lista de Tarefas Ativas ---")
    tarefas = db.listar_tarefas()
    if not tarefas:
        print("Nenhuma tarefa ativa cadastrada.")
    else:
        for tarefa in tarefas:
            print(f"ID: {tarefa.id} | Título: {tarefa.titulo} | Status: {tarefa.status.capitalize()}")
    print("-" * 25)
    pausar()

def atualizar_status_tarefa():
    while True:
        limpar_tela()
        print("--- Atualizar Status da Tarefa ---")
        tarefas = db.listar_tarefas()
        if not tarefas:
            print("Nenhuma tarefa para atualizar.")
            break
        for tarefa in tarefas:
            print(f"ID: {tarefa.id} | Título: {tarefa.titulo} | Status: {tarefa.status.capitalize()}")
        print("-" * 25)
        try:
            id_para_atualizar = int(input("Digite o ID da tarefa para alterar o status (ou 0 para voltar): "))
            if id_para_atualizar == 0:
                break
            tarefa_existente = db.buscar_tarefa_por_id(id_para_atualizar)
            if not tarefa_existente or not tarefa_existente.ativo:
                print(f"\nTarefa com ID {id_para_atualizar} não encontrada ou não está ativa.")
            else:
                print("\nEscolha o novo status:")
                print("1. Pendente\n2. Fazendo\n3. Concluída")
                escolha_status = input("Opção: ")
                mapa_status = {'1': StatusTarefa.PENDENTE, '2': StatusTarefa.FAZENDO, '3': StatusTarefa.CONCLUIDA}
                novo_status = mapa_status.get(escolha_status)
                if novo_status:
                    db.atualizar_status(id_para_atualizar, novo_status)
                    print(f"\nStatus da tarefa {id_para_atualizar} atualizado para '{novo_status.value}'.")
                else:
                    print("\nOpção de status inválida.")
        except ValueError:
            print("\nID inválido. Por favor, digite um número.")
        continuar = input("\nDeseja atualizar outra tarefa? (s/n): ").lower()
        if continuar != 's':
            break
    print("\nVoltando ao menu principal...")
    pausar()
# ----------------------------------------------------------------

# MUDANÇA 1: A função de remover agora chama 'desativar_tarefa'
def remover_tarefa_logica():
    """Permite ao usuário 'remover' (desativar) uma ou mais tarefas."""
    while True:
        limpar_tela()
        print("--- Mover Tarefa para a Lixeira (Exclusão Lógica) ---")
        tarefas = db.listar_tarefas()
        if not tarefas:
            print("Nenhuma tarefa para remover.")
            break
        for tarefa in tarefas:
            print(f"ID: {tarefa.id} | Título: {tarefa.titulo} | Status: {tarefa.status.capitalize()}")
        print("-" * 25)
        try:
            id_para_remover = int(input("Digite o ID da tarefa que deseja mover para a lixeira (ou 0 para voltar): "))
            if id_para_remover == 0:
                break
            if db.desativar_tarefa(id_para_remover):
                print(f"\nTarefa com ID {id_para_remover} movida para a lixeira com sucesso.")
            else:
                print(f"\nFalha ao mover. Tarefa com ID {id_para_remover} não encontrada.")
        except ValueError:
            print("\nID inválido. Por favor, digite um número.")
        continuar = input("\nDeseja mover outra tarefa para a lixeira? (s/n): ").lower()
        if continuar != 's':
            break
    print("\nVoltando ao menu principal...")
    pausar()

# NOVA FUNÇÃO: Interface para recuperar tarefas
def recuperar_tarefa_logica():
    """Permite ao usuário recuperar uma ou mais tarefas da lixeira."""
    while True:
        limpar_tela()
        print("--- Recuperar Tarefa da Lixeira ---")
        tarefas_excluidas = db.listar_tarefas_excluidas()
        if not tarefas_excluidas:
            print("A lixeira está vazia. Nenhuma tarefa para recuperar.")
            pausar()
            break
        print("Tarefas na lixeira:")
        for tarefa in tarefas_excluidas:
            print(f"ID: {tarefa.id} | Título: {tarefa.titulo}")
        print("-" * 25)
        try:
            id_para_recuperar = int(input("Digite o ID da tarefa que deseja recuperar (ou 0 para voltar): "))
            if id_para_recuperar == 0:
                break
            if db.recuperar_tarefa(id_para_recuperar):
                print(f"\nTarefa com ID {id_para_recuperar} recuperada com sucesso!")
            else:
                print(f"\nFalha ao recuperar. Tarefa com ID {id_para_recuperar} não encontrada na lixeira.")
        except ValueError:
            print("\nID inválido. Por favor, digite um número.")
        continuar = input("\nDeseja recuperar outra tarefa? (s/n): ").lower()
        if continuar != 's':
            break
    print("\nVoltando ao menu principal...")
    pausar()

# MUDANÇA 2: O menu de opções foi atualizado
def exibir_menu_e_obter_opcao():
    limpar_tela()
    print("--- MENU To-Do List (com Lixeira) ---")
    print("1. Adicionar tarefa(s)")
    print("2. Listar tarefas ativas")
    print("3. Atualizar status de tarefa(s)")
    print("4. Mover tarefa para lixeira")
    print("5. Recuperar tarefa da lixeira") # Nova opção
    print("6. Sair")
    return input("Escolha uma opção: ")

def main():
    db.init_db()
    # MUDANÇA 3: O dicionário de opções foi atualizado
    opcoes = {
        '1': adicionar_nova_tarefa,
        '2': listar_todas_tarefas,
        '3': atualizar_status_tarefa,
        '4': remover_tarefa_logica,      # Aponta para a nova função
        '5': recuperar_tarefa_logica,    # Aponta para a nova função
    }
    while True:
        escolha = exibir_menu_e_obter_opcao()
        # MUDANÇA 4: A opção de sair agora é '6'
        if escolha == '6':
            print("Saindo do programa. Até mais!")
            break
        funcao_a_executar = opcoes.get(escolha)
        if funcao_a_executar:
            funcao_a_executar()
        else:
            print("\nOpção inválida. Tente novamente.")
            pausar()

if __name__ == "__main__":
    main()