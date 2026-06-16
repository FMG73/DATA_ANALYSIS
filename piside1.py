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
# ESTILO GLOBAL POR DEFECTO
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
        self.resize(QSize(900, 450))

        # =========================
        # CONFIGURACIÓN DE PÁGINAS
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
                            {
                                "name": "OAS 940",
                                "path": r"C:\Python\script1.py"
                            },
                            {
                                "name": "URGENTE FIX",
                                "path": r"C:\Python\script2.py",
                                "style": {
                                    "bg": "#E53935",
                                    "hover": "#C62828",
                                    "font_size": 12
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
                            {
                                "name": "Proceso A",
                                "path": r"C:\Python\script3.py"
                            }
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
                            {
                                "name": "Control 1",
                                "path": r"C:\Python\script4.py"
                            }
                        ]
                    }
                ]
            }
        ]

        self.current_page = 0
        self.setup_ui()

    # =========================
    # UI PRINCIPAL
    # =========================
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.title = QLabel("Ejecutor de Scripts - MELERO")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:18px;font-weight:bold;")

        self.page_title = QLabel(self.pages_data[0]["title"])
        self.page_title.setAlignment(Qt.AlignCenter)
        self.page_title.setStyleSheet("font-size:14px;font-weight:bold;")

        self.stacked = QStackedWidget()

        for page in self.pages_data:
            self.stacked.addWidget(self._create_page(page))

        nav = QHBoxLayout()
        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Siguiente")

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.page_title)
        main_layout.addWidget(self.stacked)
        main_layout.addLayout(nav)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.update_nav()

    # =========================
    # CREACIÓN DE PÁGINAS
    # =========================
    def _create_page(self, page_data):
        page = QWidget()
        layout = QHBoxLayout()

        for col in page_data["columns"]:
            layout.addWidget(self._create_column(col))

        page.setLayout(layout)
        return page

    # =========================
    # COLUMNAS
    # =========================
    def _create_column(self, column_data):
        frame = QFrame()
        layout = QVBoxLayout()

        col_style = column_data.get("style", {})
        column_bg = col_style.get("column_bg", "#F5F5F5")

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
            layout.addWidget(self._create_button(script, col_style))

        frame.setLayout(layout)
        return frame

    # =========================
    # BOTONES (HERENCIA DE ESTILO)
    # =========================
    def _create_button(self, script, column_style):
        # 1. Base global
        style = APP_DEFAULT_STYLE.copy()

        # 2. Estilo de columna
        style.update(column_style)

        # 3. Estilo del botón (máxima prioridad)
        style.update(script.get("style", {}))

        name = script["name"]
        path = script["path"]

        btn = QPushButton(name)
        btn.setFont(QFont("Arial", style.get("font_size", 11)))

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {style.get("bg")};
                color: {style.get("text_color")};
                border-radius: {style.get("border_radius")}px;
                padding: {style.get("padding")};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {style.get("hover")};
            }}
        """)

        btn.clicked.connect(lambda _, p=path, n=name: self.run_script(p, n))
        return btn

    # =========================
    # EJECUCIÓN DE SCRIPTS
    # =========================
    def run_script(self, script_path, name):
        if not Path(script_path).exists():
            QMessageBox.critical(self, "Error", f"No existe: {script_path}")
            return

        try:
            subprocess.Popen(
                [sys.executable, script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # =========================
    # NAVEGACIÓN
    # =========================
    def next_page(self):
        if self.current_page < len(self.pages_data) - 1:
            self.current_page += 1
            self.stacked.setCurrentIndex(self.current_page)
            self.page_title.setText(self.pages_data[self.current_page]["title"])
            self.update_nav()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked.setCurrentIndex(self.current_page)
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())