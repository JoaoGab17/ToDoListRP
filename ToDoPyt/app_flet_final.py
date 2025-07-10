# app_flet_final.py
import flet as ft
import requests

# --- PONTO DE CONFIGURAÇÃO CRÍTICO ---
# Se você estiver testando com a API rodando localmente, use a primeira linha.
# Se você já implantou a API na nuvem (Render), comente a primeira linha e use a segunda.

API_URL = "http://127.0.0.1:5000"
# API_URL = "https://sua-api.onrender.com" # Exemplo da URL do Render

def main(page: ft.Page):
    page.title = "To-Do List (Desktop App)"
    page.window_width = 600
    page.window_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
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

    def show_error_snackbar(message="Erro de conexão com a API."):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    def get_tasks_from_api(url_path):
        try:
            response = requests.get(f"{API_URL}{url_path}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados de {url_path}: {e}")
            show_error_snackbar(f"Não foi possível buscar dados. A API está rodando?")
            return []

    def api_call_handler(method, url_path, json_data=None):
        try:
            response = requests.request(method, f"{API_URL}{url_path}", json=json_data)
            response.raise_for_status()
            update_ui()
        except requests.exceptions.RequestException as e:
            print(f"Erro na operação de API em {url_path}: {e}")
            show_error_snackbar("A operação falhou.")

    def add_task_clicked(e=None):
        if new_task_field.value.strip():
            api_call_handler("POST", "/tarefas", json_data={"text": new_task_field.value})
            new_task_field.value = ""
            new_task_field.focus()

    def status_changed(e):
        api_call_handler("PUT", f"/tarefas/{e.control.data['id']}/status", json_data={"status": e.control.data['status']})

    def move_to_trash_clicked(e):
        api_call_handler("DELETE", f"/tarefas/{e.control.data}")

    def restore_from_trash_clicked(e):
        api_call_handler("PUT", f"/tarefas/{e.control.data}/recuperar")

    def create_task_view(task):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=15, alignment=ft.MainAxisAlignment.START, expand=True,
                    controls=[ft.Text(f"[{task['id']}] {task['titulo']}", size=16)]
                ),
                ft.Row(
                    spacing=0, alignment=ft.MainAxisAlignment.END,
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
                        ft.IconButton(icon="delete_outline", tooltip="Mover para lixeira", on_click=move_to_trash_clicked, data=task['id'], icon_color="redaccent")
                    ]
                )
            ]
        )

    def create_trashed_task_view(task):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, opacity=0.6,
            controls=[
                ft.Row(spacing=15, controls=[
                    ft.Icon("delete_forever_outlined"),
                    ft.Text(f"[{task['id']}] {task['titulo']}", italic=True),
                ]),
                ft.IconButton(icon="restore_from_trash", tooltip="Restaurar tarefa", on_click=restore_from_trash_clicked, data=task['id'], icon_color="greenaccent")
            ]
        )

    new_task_field = ft.TextField(hint_text="O que precisa ser feito?", expand=True, on_submit=add_task_clicked)
    active_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    trashed_tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)

    def update_ui():
        active_tasks_column.controls.clear()
        trashed_tasks_column.controls.clear()
        
        for task in get_tasks_from_api("/tarefas"):
            active_tasks_column.controls.append(create_task_view(task))
        if not active_tasks_column.controls:
            active_tasks_column.controls.append(ft.Container(ft.Text("Nenhuma tarefa ativa."), alignment=ft.alignment.center, padding=20))
            
        for task in get_tasks_from_api("/tarefas/excluidas"):
            trashed_tasks_column.controls.append(create_trashed_task_view(task))
        if not trashed_tasks_column.controls:
            trashed_tasks_column.controls.append(ft.Container(ft.Text("A lixeira está vazia."), alignment=ft.alignment.center, padding=20))
            
        page.update()

    tabs = ft.Tabs(
        selected_index=0, expand=1,
        tabs=[
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