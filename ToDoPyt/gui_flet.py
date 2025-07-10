import flet as ft
import requests

API_URL = "http://127.0.0.1:5000"

def main(page: ft.Page):
    page.title = "To-Do List Full-Stack"
    page.window_width = 600
    page.window_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.appbar = ft.AppBar(
        title=ft.Text("To-Do List (Flet)"),
        center_title=True,
        bgcolor="surfacevariant",
        actions=[
            # CORREÇÃO: Ícone como texto
            ft.IconButton("refresh", on_click=lambda e: update_ui(), tooltip="Atualizar Lista")
        ]
    )
    page.floating_action_button = ft.FloatingActionButton(
        # CORREÇÃO: Ícone como texto
        icon="add", on_click=lambda e: add_task_clicked(), tooltip="Adicionar Tarefa"
    )

    # --- Funções de API (não mudam) ---
    def get_tasks_from_api():
        try:
            response = requests.get(f"{API_URL}/tarefas")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar tarefas: {e}")
            page.snack_bar = ft.SnackBar(ft.Text("Erro de conexão com a API."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return []

    def get_trashed_tasks_from_api():
        try:
            response = requests.get(f"{API_URL}/tarefas/excluidas")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar lixeira: {e}")
            return []
            
    # --- Funções de Ação (Event Handlers) ---
    def add_task_clicked(e=None):
        task_title = new_task_field.value
        if not task_title.strip():
            return
        try:
            requests.post(f"{API_URL}/tarefas", json={"text": task_title})
            new_task_field.value = ""
            new_task_field.focus()
            update_ui()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao adicionar tarefa: {e}")

    def status_changed(e):
        task_id = e.control.data['id']
        new_status = e.control.data['status']
        try:
            requests.put(f"{API_URL}/tarefas/{task_id}/status", json={"status": new_status})
            update_ui()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao atualizar status: {e}")

    def move_to_trash_clicked(e):
        task_id = e.control.data
        try:
            requests.delete(f"{API_URL}/tarefas/{task_id}")
            update_ui()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao mover para lixeira: {e}")
    
    def restore_from_trash_clicked(e):
        task_id = e.control.data
        try:
            requests.put(f"{API_URL}/tarefas/{task_id}/recuperar")
            update_ui()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao restaurar: {e}")

    # --- Funções para Construir a UI ---
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
                            # CORREÇÃO: Ícone como texto
                            icon="more_vert",
                            items=[
                                ft.PopupMenuItem(text="Pendente", data={'id': task['id'], 'status': 'pendente'}, on_click=status_changed),
                                ft.PopupMenuItem(text="Fazendo", data={'id': task['id'], 'status': 'fazendo'}, on_click=status_changed),
                                ft.PopupMenuItem(text="Concluída", data={'id': task['id'], 'status': 'concluída'}, on_click=status_changed),
                            ]
                        ),
                        ft.IconButton(
                            # CORREÇÃO: Ícone como texto
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
                    # CORREÇÃO: Ícone como texto
                    ft.Icon("delete_forever_outlined"),
                    ft.Text(f"[{task['id']}] {task['titulo']}", italic=True),
                ]),
                ft.IconButton(
                    # CORREÇÃO: Ícone como texto
                    icon="restore_from_trash",
                    tooltip="Restaurar tarefa",
                    on_click=restore_from_trash_clicked,
                    data=task['id'],
                    icon_color="greenaccent"
                )
            ]
        )

    # --- Controles Principais e Função de Atualização ---
    new_task_field = ft.TextField(hint_text="O que precisa ser feito?", expand=True, on_submit=add_task_clicked)
    active_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    trashed_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)

    def update_ui(e=None):
        active_tasks_column.controls.clear()
        trashed_tasks_column.controls.clear()
        
        active_tasks = get_tasks_from_api()
        if active_tasks:
            for task in active_tasks:
                active_tasks_column.controls.append(create_task_view(task))
        else:
            active_tasks_column.controls.append(ft.Container(ft.Text("Nenhuma tarefa ativa."), alignment=ft.alignment.center, padding=20))
            
        trashed_tasks = get_trashed_tasks_from_api()
        if trashed_tasks:
            for task in trashed_tasks:
                trashed_tasks_column.controls.append(create_trashed_task_view(task))
        else:
            trashed_tasks_column.controls.append(ft.Container(ft.Text("A lixeira está vazia."), alignment=ft.alignment.center, padding=20))
            
        page.update()

    # --- Montagem da Página com a nova estrutura ---
    tabs = ft.Tabs(
        selected_index=0,
        expand=1,
        tabs=[
            # CORREÇÃO: Ícones como texto
            ft.Tab(text="Tarefas Ativas", icon="list_alt_rounded", content=active_tasks_column),
            ft.Tab(text="Lixeira", icon="delete_sweep_outlined", content=trashed_tasks_column),
        ]
    )
    
    page.add(
        ft.Row(controls=[new_task_field]),
        ft.Container(content=tabs, expand=True)
    )
    
    update_ui()

if __name__ == "__main__":
    ft.app(target=main)