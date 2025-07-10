import flet as ft
import threading
from api import app as flask_app # Importamos a app Flask do nosso arquivo api.py
import database as db # Importamos o banco de dados diretamente

# --- Funções que agora falam DIRETAMENTE com o banco ---

def add_task(title):
    if title and title.strip():
        db.adicionar_tarefa(title)

def get_active_tasks():
    return [task.__dict__ for task in db.listar_tarefas()]

def get_trashed_tasks():
    return [task.__dict__ for task in db.listar_tarefas_excluidas()]

def update_task_status(task_id, new_status_str):
    status_enum = db.StatusTarefa(new_status_str)
    db.atualizar_status(task_id, status_enum)

def move_task_to_trash(task_id):
    db.desativar_tarefa(task_id)

def restore_task_from_trash(task_id):
    db.recuperar_tarefa(task_id)

# --- A Interface Flet ---

def flet_main(page: ft.Page):
    page.title = "To-Do List (App Executável)"
    page.window_width = 600
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.appbar = ft.AppBar(
        title=ft.Text("To-Do List"),
        center_title=True,
        bgcolor="surfacevariant",
        actions=[
            ft.IconButton("refresh", on_click=lambda e: update_ui(), tooltip="Atualizar Lista")
        ]
    )
    page.floating_action_button = ft.FloatingActionButton(
        icon="add", on_click=lambda e: add_task_clicked(), tooltip="Adicionar Tarefa"
    )

    def update_ui():
        # Limpa as colunas antes de preencher
        active_tasks_column.controls.clear()
        trashed_tasks_column.controls.clear()
        
        # Preenche com tarefas ativas
        active_tasks = get_active_tasks()
        if active_tasks:
            for task in active_tasks:
                active_tasks_column.controls.append(create_task_view(task))
        else:
            active_tasks_column.controls.append(ft.Container(ft.Text("Nenhuma tarefa ativa."), alignment=ft.alignment.center, padding=20))
        
        # Preenche com tarefas da lixeira
        trashed_tasks = get_trashed_tasks()
        if trashed_tasks:
            for task in trashed_tasks:
                trashed_tasks_column.controls.append(create_trashed_task_view(task))
        else:
            trashed_tasks_column.controls.append(ft.Container(ft.Text("A lixeira está vazia."), alignment=ft.alignment.center, padding=20))
            
        page.update()

    def add_task_clicked():
        add_task(new_task_field.value)
        new_task_field.value = ""
        new_task_field.focus()
        update_ui()

    def status_changed(e):
        update_task_status(e.control.data['id'], e.control.data['status'])
        update_ui()

    def move_to_trash_clicked(e):
        move_task_to_trash(e.control.data)
        update_ui()
    
    def restore_from_trash_clicked(e):
        restore_task_from_trash(e.control.data)
        update_ui()
    
    # Funções que constroem a UI de cada item
    def create_task_view(task):
        status_icons = {
            "pendente": "radio_button_unchecked",
            "fazendo": "change_circle_outlined",
            "concluída": "check_circle_outline",
        }
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=15,
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                    controls=[
                        ft.Icon(name=status_icons.get(task['status'])),
                        ft.Text(f"[{task['id']}] {task['titulo']}", size=16),
                    ]
                ),
                ft.Row(
                    spacing=0,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.Text(task['status'].capitalize(), size=12, color="grey", weight=ft.FontWeight.BOLD),
                        ft.PopupMenuButton(
                            icon="more_vert",
                            items=[
                                ft.PopupMenuItem(text="Pendente", data={'id': task['id'], 'status': 'pendente'}, on_click=status_changed),
                                ft.PopupMenuItem(text="Fazendo", data={'id': task['id'], 'status': 'fazendo'}, on_click=status_changed),
                                ft.PopupMenuItem(text="Concluída", data={'id': task['id'], 'status': 'concluída'}, on_click=status_changed),
                            ]
                        ),
                        ft.IconButton(
                            icon="delete_outline",
                            tooltip="Mover para lixeira",
                            on_click=move_to_trash_clicked,
                            data=task['id'],
                            icon_color="redaccent"
                        )
                    ]
                )
            ]
        )

    def create_trashed_task_view(task):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            opacity=0.6,
            controls=[
                ft.Row(spacing=15, controls=[
                    ft.Icon("delete_forever_outlined"),
                    ft.Text(f"[{task['id']}] {task['titulo']}", italic=True),
                ]),
                ft.IconButton(
                    icon="restore_from_trash",
                    tooltip="Restaurar tarefa",
                    on_click=restore_from_trash_clicked,
                    data=task['id'],
                    icon_color="greenaccent"
                )
            ]
        )

    # Definição dos controles principais da UI
    new_task_field = ft.TextField(hint_text="O que precisa ser feito?", expand=True, on_submit=lambda e: add_task_clicked())
    active_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    trashed_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    
    tabs = ft.Tabs(
        selected_index=0,
        expand=1,
        tabs=[
            ft.Tab(text="Tarefas Ativas", icon="list_alt_rounded", content=active_tasks_column),
            ft.Tab(text="Lixeira", icon="delete_sweep_outlined", content=trashed_tasks_column),
        ]
    )
    
    # Adiciona os elementos à página
    page.add(
        ft.Row(controls=[new_task_field]),
        ft.Container(content=tabs, expand=True)
    )
    
    # Carrega os dados iniciais
    update_ui()

# --- Ponto de Entrada Principal que inicia as Threads ---
def run_flask():
    """Função para rodar o Flask."""
    flask_app.run(host="0.0.0.0", port=5000) 

if __name__ == "__main__":
    db.init_db()
    
    # 1. Inicia o servidor Flask em uma thread de fundo
    print("Iniciando servidor da API em segundo plano...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Inicia a aplicação Flet na thread principal
    print("Iniciando interface gráfica Flet...")
    ft.app(target=flet_main)