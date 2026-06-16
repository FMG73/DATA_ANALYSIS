import sys
from pathlib import Path
import subprocess

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QHBoxLayout, QLabel,
    QMessageBox, QFrame, QStackedWidget
)

# =========================
# ESTILO GLOBAL
# =========================
APP_DEFAULT_STYLE = {
    "bg": "#4CAF50",
    "hover": "#45A049",
    "text_color": "white",
    "font_size": 11,
    "border_radius": 10,
    "padding": "10px 20px"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ejecutor de Scripts - MELERO")
        self.resize(QSize(900, 500))

        # =========================
        # CONFIGURACIÓN (2 PÁGINAS)
        # =========================
        self.pages_data = [
            {
                "title": "1: FRECUENTES",
                "columns": [
                    {
                        "title": "OAS",
                        "style": {
                            "column_bg": "#E8F5E9",
                            "bg": "#4CAF50",
                            "hover": "#45A049"
                        },
                        "scripts": [
                            {"name": "OAS 940", "path": r"C:\scripts\script1.py"},
                            {
                                "name": "URGENTE",
                                "path": r"C:\scripts\script2.py",
                                "style": {
                                    "bg": "#E53935",
                                    "hover": "#C62828"
                                }
                            }
                        ]
                    },
                    {
                        "title": "SCRIPTS",
                        "style": {
                            "column_bg": "#E3F2FD",
                            "bg": "#2196F3",
                            "hover": "#1976D2"
                        },
                        "scripts": [
                            {"name": "Proceso A", "path": r"C:\scripts\script3.py"}
                        ]
                    },
                    {
                        "title": "CONTROLES",
                        "style": {
                            "column_bg": "#FFF3E0",
                            "bg": "#FF9800",
                            "hover": "#F57C00"
                        },
                        "scripts": [
                            {"name": "Control 1", "path": r"C:\scripts\script4.py"}
                        ]
                    }
                ]
            },
            {
                "title": "2: OCASIONALES",
                "columns": [
                    {
                        "title": "UNO",
                        "style": {
                            "column_bg": "#F3E5F5",
                            "bg": "#9C27B0",
                            "hover": "#7B1FA2"
                        },
                        "scripts": [
                            {"name": "Script 7", "path": r"C:\scripts\script7.py"},
                            {"name": "Script 8", "path": r"C:\scripts\script8.py"}
                        ]
                    },
                    {
                        "title": "DOS",
                        "style": {
                            "column_bg": "#E0F7FA",
                            "bg": "#00ACC1",
                            "hover": "#00838F"
                        },
                        "scripts": [
                            {"name": "Script 9", "path": r"C:\scripts\script9.py"}
                        ]
                    }
                ]
            }
        ]

        self.current_page = 0
        self.setup_ui()

    # =========================
    # UI
    # =========================
    def setup_ui(self):
        main = QWidget()
        layout = QVBoxLayout()

        self.title = QLabel("Ejecutor de Scripts - MELERO")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:18px;font-weight:bold;")

        self.page_title = QLabel(self.pages_data[0]["title"])
        self.page_title.setAlignment(Qt.AlignCenter)
        self.page_title.setStyleSheet("font-size:14px;font-weight:bold;")

        self.stack = QStackedWidget()

        for page in self.pages_data:
            self.stack.addWidget(self._create_page(page))

        # navegación
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Siguiente")

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)

        layout.addWidget(self.title)
        layout.addWidget(self.page_title)
        layout.addWidget(self.stack)
        layout.addLayout(nav)

        main.setLayout(layout)
        self.setCentralWidget(main)

        self.update_nav()

    # =========================
    # PÁGINA
    # =========================
    def _create_page(self, page_data):
        page = QWidget()
        layout = QHBoxLayout()

        for col in page_data["columns"]:
            layout.addWidget(self._create_column(col))

        page.setLayout(layout)
        return page

    # =========================
    # COLUMNA
    # =========================
    def _create_column(self, column_data):
        frame = QFrame()
        layout = QVBoxLayout()

        style = column_data.get("style", {})
        column_bg = style.get("column_bg", "#F5F5F5")

        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {column_bg};
                border-radius: 10px;
                padding: 10px;
            }}
        """)

        title = QLabel(column_data["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight:bold;margin-bottom:10px;")
        layout.addWidget(title)

        for script in column_data["scripts"]:
            layout.addWidget(self._create_button(script, style))

        frame.setLayout(layout)
        return frame

    # =========================
    # BOTÓN CON HERENCIA
    # =========================
    def _create_button(self, script, column_style):
        # 1. base global
        style = APP_DEFAULT_STYLE.copy()

        # 2. columna
        style.update(column_style)

        # 3. botón (override final)
        style.update(script.get("style", {}))

        btn = QPushButton(script["name"])
        btn.setFont(QFont("Arial", style["font_size"]))

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {style["bg"]};
                color: {style["text_color"]};
                border-radius: {style["border_radius"]}px;
                padding: {style["padding"]};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {style["hover"]};
            }}
        """)

        btn.clicked.connect(
            lambda _, p=script["path"], n=script["name"]: self.run_script(p, n)
        )

        return btn

    # =========================
    # EJECUCIÓN
    # =========================
    def run_script(self, path, name):
        if not Path(path).exists():
            QMessageBox.critical(self, "Error", f"No existe: {path}")
            return

        subprocess.Popen(
            [sys.executable, path],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )

    # =========================
    # NAVEGACIÓN
    # =========================
    def next_page(self):
        if self.current_page < len(self.pages_data) - 1:
            self.current_page += 1
            self.stack.setCurrentIndex(self.current_page)
            self.page_title.setText(self.pages_data[self.current_page]["title"])
            self.update_nav()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.setCurrentIndex(self.current_page)
            self.page_title.setText(self.pages_data[self.current_page]["title"])
            self.update_nav()

    def update_nav(self):
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.pages_data) - 1)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())