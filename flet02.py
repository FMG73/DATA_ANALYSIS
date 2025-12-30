import flet as ft
import subprocess
import os

# ---------------- CONFIGURACIÓN ----------------

PAGES_CONFIG = {
    "page1": {
        "title": "Página 1 - Categoría Principal",
        "columns": [
            {
                "bgcolor": ft.Colors.BLUE_100,
                "buttons": [
                    {"name": "Script 1A", "color": ft.Colors.RED, "script": "path/to/script1A.py"},
                    {"name": "Script 1B", "color": ft.Colors.GREEN, "script": "path/to/script1B.py"},
                ]
            },
            {
                "bgcolor": ft.Colors.GREEN_100,
                "buttons": [
                    {"name": "Script 1C", "color": ft.Colors.BLUE, "script": "path/to/script1C.py"},
                ]
            },
            {
                "bgcolor": ft.Colors.RED_100,
                "buttons": [
                    {"name": "Script 1D", "color": ft.Colors.YELLOW, "script": "path/to/script1D.py"},
                    {"name": "Script 1E", "color": ft.Colors.PURPLE, "script": "path/to/script1E.py"},
                ]
            }
        ]
    },
    "page2": {
        "title": "Página 2 - Otra Categoría",
        "columns": [
            {
                "bgcolor": ft.Colors.YELLOW_100,
                "buttons": [
                    {"name": "Script 2A", "color": ft.Colors.ORANGE, "script": "path/to/script2A.py"},
                ]
            },
            {
                "bgcolor": ft.Colors.PURPLE_100,
                "buttons": [
                    {"name": "Script 2B", "color": ft.Colors.CYAN, "script": "path/to/script2B.py"},
                    {"name": "Script 2C", "color": ft.Colors.PINK, "script": "path/to/script2C.py"},
                ]
            },
            {
                "bgcolor": ft.Colors.ORANGE_100,
                "buttons": [
                    {"name": "Script 2D", "color": ft.Colors.TEAL, "script": "path/to/script2D.py"},
                ]
            }
        ]
    }
}

# ---------------- LÓGICA ----------------

def execute_script(script_path: str) -> str:
    script_path = os.path.abspath(script_path)

    if not os.path.exists(script_path):
        return f"❌ El archivo no existe:\n{script_path}"

    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as ex:
        return f"❌ Error inesperado:\n{str(ex)}"


def run_and_show(path: str, output: ft.Text):
    output.value = execute_script(path)
    output.update()

# ---------------- UI ----------------

def create_output_text() -> ft.Text:
    return ft.Text(
        value="",
        selectable=True,
        size=14,
        color=ft.Colors.GREEN_700
    )


def create_column(col_config: dict, output: ft.Text) -> ft.Container:
    buttons = []

    for btn in col_config["buttons"]:
        script_path = btn["script"]

        buttons.append(
            ft.ElevatedButton(
                text=btn["name"],
                color=btn["color"],
                on_click=lambda e, p=script_path: run_and_show(p, output)
            )
        )

    return ft.Container(
        content=ft.Column(buttons, spacing=10),
        bgcolor=col_config["bgcolor"],
        padding=20,
        expand=True,
        border_radius=10
    )


def create_page_content(page_key: str, page: ft.Page) -> ft.Column:
    config = PAGES_CONFIG[page_key]
    output = create_output_text()

    columns = ft.Row(
        [create_column(col, output) for col in config["columns"]],
        spacing=20,
        expand=True
    )

    output_box = ft.Container(
        content=ft.Column(
            [
                ft.Text("Salida del script:", weight=ft.FontWeight.BOLD),
                output
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        height=220,
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8
    )

    return ft.Column(
        [
            ft.Text(config["title"], size=24, weight=ft.FontWeight.BOLD),
            columns,
            output_box,
            ft.ElevatedButton("Volver al menú", on_click=lambda _: page.go("/"))
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


def create_menu_view(page: ft.Page) -> ft.View:
    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Text("Menú Principal", size=28, weight=ft.FontWeight.BOLD),
                    *[
                        ft.ElevatedButton(
                            f"Ir a {cfg['title'].split(' - ')[0]}",
                            on_click=lambda e, k=key: page.go(f"/{k}")
                        )
                        for key, cfg in PAGES_CONFIG.items()
                    ]
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
    return ft.View(
        f"/{page_key}",
        [create_page_content(page_key, page)],
        padding=20
    )


def route_change(route, page: ft.Page):
    page.views.clear()

    if page.route == "/":
        page.views.append(create_menu_view(page))
    else:
        key = page.route.lstrip("/")
        if key in PAGES_CONFIG:
            page.views.append(create_page_view(key, page))

    page.update()


def view_pop(view, page: ft.Page):
    page.views.pop()
    page.go(page.views[-1].route)


def main(page: ft.Page):
    page.title = "Menú de Ejecución de Scripts"
    page.bgcolor = ft.Colors.GREY_200
    page.on_route_change = lambda r: route_change(r, page)
    page.on_view_pop = lambda v: view_pop(v, page)
    page.go("/")

# ---------------- APP ----------------

ft.app(target=main)