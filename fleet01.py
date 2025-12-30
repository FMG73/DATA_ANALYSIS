import flet as ft
import subprocess
import os

# Configuración personalizable de las páginas, columnas y botones
# Cada página tiene un nombre y 3 columnas
# Cada columna tiene un color de fondo y una lista de botones
# Cada botón tiene: nombre, color, y ruta al script Python
PAGES_CONFIG = {
    "page1": {
        "title": "Página 1 - Categoría Principal",
        "columns": [
            {
                "bgcolor": ft.colors.BLUE_100,
                "buttons": [
                    {"name": "Script 1A", "color": ft.colors.RED, "script": "path/to/script1A.py"},
                    {"name": "Script 1B", "color": ft.colors.GREEN, "script": "path/to/script1B.py"},
                ]
            },
            {
                "bgcolor": ft.colors.GREEN_100,
                "buttons": [
                    {"name": "Script 1C", "color": ft.colors.BLUE, "script": "path/to/script1C.py"},
                ]
            },
            {
                "bgcolor": ft.colors.RED_100,
                "buttons": [
                    {"name": "Script 1D", "color": ft.colors.YELLOW, "script": "path/to/script1D.py"},
                    {"name": "Script 1E", "color": ft.colors.PURPLE, "script": "path/to/script1E.py"},
                ]
            }
        ]
    },
    "page2": {
        "title": "Página 2 - Otra Categoría",
        "columns": [
            {
                "bgcolor": ft.colors.YELLOW_100,
                "buttons": [
                    {"name": "Script 2A", "color": ft.colors.ORANGE, "script": "path/to/script2A.py"},
                ]
            },
            {
                "bgcolor": ft.colors.PURPLE_100,
                "buttons": [
                    {"name": "Script 2B", "color": ft.colors.CYAN, "script": "path/to/script2B.py"},
                    {"name": "Script 2C", "color": ft.colors.PINK, "script": "path/to/script2C.py"},
                ]
            },
            {
                "bgcolor": ft.colors.ORANGE_100,
                "buttons": [
                    {"name": "Script 2D", "color": ft.colors.TEAL, "script": "path/to/script2D.py"},
                ]
            }
        ]
    }
}

def execute_script(script_path: str) -> str:
    """Ejecuta un script Python y devuelve la salida o errores."""
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        return f"Salida:\n{result.stdout}\nErrores:\n{result.stderr}"
    except subprocess.CalledProcessError as err:
        return f"Error al ejecutar: {err.stderr}"
    except Exception as ex:
        return f"Error inesperado: {str(ex)}"

def create_output_container(page: ft.Page) -> ft.Text:
    """Crea un contenedor de texto para mostrar la salida de los scripts."""
    return ft.Text(value="", italic=True, size=14, color=ft.colors.GREEN_700, width=page.width)

def create_column(col_config: dict, execute_fn: callable) -> ft.Container:
    """Crea una columna con botones basados en la configuración."""
    buttons = [
        ft.ElevatedButton(
            text=btn["name"],
            color=btn["color"],
            on_click=lambda e, path=btn["script"]: execute_fn(path)
        ) for btn in col_config["buttons"]
    ]
    return ft.Container(
        content=ft.Column(buttons, spacing=10, alignment=ft.MainAxisAlignment.START),
        bgcolor=col_config["bgcolor"],
        padding=20,
        expand=True,
        border_radius=10
    )

def create_page_content(page_key: str, output_container: ft.Text, page: ft.Page) -> ft.Column:
    """Crea el contenido de una página específica con columnas y botones."""
    config = PAGES_CONFIG[page_key]
    columns = ft.Row(
        [create_column(col, lambda path: output_container.update(value=execute_script(path))) for col in config["columns"]],
        expand=True,
        spacing=20
    )
    return ft.Column(
        [
            ft.Text(config["title"], size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
            columns,
            output_container,
            ft.ElevatedButton(text="Volver al Menú", on_click=lambda _: page.go("/"))
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def create_menu_view(page: ft.Page) -> ft.View:
    """Crea la vista del menú principal."""
    menu_buttons = [
        ft.ElevatedButton(f"Ir a {config['title'].split(' - ')[0]}", on_click=lambda _, key=key: page.go(f"/{key}"))
        for key, config in PAGES_CONFIG.items()
    ]
    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Text("Menú Principal", size=28, weight=ft.FontWeight.BOLD),
                    *menu_buttons
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def create_page_view(page_key: str, page: ft.Page) -> ft.View:
    """Crea la vista para una página específica."""
    output = create_output_container(page)
    content = create_page_content(page_key, output, page)
    return ft.View(
        f"/{page_key}",
        [content],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20
    )

def route_change(route, page: ft.Page):
    """Maneja el cambio de rutas."""
    page.views.clear()
    if page.route == "/":
        page.views.append(create_menu_view(page))
    else:
        page_key = page.route.lstrip("/")
        if page_key in PAGES_CONFIG:
            page.views.append(create_page_view(page_key, page))
    page.update()

def view_pop(view, page: ft.Page):
    """Maneja el pop de vistas para navegación hacia atrás."""
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

def main(page: ft.Page):
    """Función principal para inicializar la app."""
    page.title = "Menú de Ejecución de Scripts"
    page.bgcolor = ft.colors.GREY_200
    page.on_route_change = lambda route: route_change(route, page)
    page.on_view_pop = lambda view: view_pop(view, page)
    page.go(page.route)

ft.app(target=main)