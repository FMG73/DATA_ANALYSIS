import sys
from pathlib import Path
import subprocess
from PySide6.QtCore import QSize, Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QAction, QClipboard, QTextDocument
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
    QLabel, QMessageBox, QFrame, QStackedWidget, QMenu, QTextEdit, QDialog,
    QSizePolicy
)

# =========================
# RUTAS SCRIPTS
# =========================

oas_025_red  = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts_flujos\025_descarga_copia.py'
oas_505_current = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_505_current.py'
oas_713 = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_713.py'
oas_940 = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_940.py'

red = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\red\acceso_redes.py'
vpn = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\red\acceso_redes_vpn.py'


# =========================
# ESTILO GLOBAL
# =========================

APP_DEFAULT_STYLE = {
    "bg": "#4CAF50",
    "hover": "#45A049",
    "pressed": "#2E7D32",
    "text_color": "black",
    "font_size": 11,
    "border_radius": 10,
    "padding": "10px 20px"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CONSOLA SCRIPTS")
        self.resize(QSize(900, 500))

        self.pages_data = [
            {
                "title": "1: FRECUENTES",
                "columns": [
                    {
                        "title": "OAS",
                        "style": {"column_bg": "#E8F5E9", "bg": "#4CAF50", "hover": "#45A049"},
                        "scripts": [
                            {
                                "name": "3 OAS 025 + RED",
                                "path": oas_025_red,
                                "tooltip": "Descarga y copia datos de OAS 025",
                                "right_click_description":
                                    "Script para descargar datos de OAS 025 y copiarlos a la red.\n\n"
                                    "Detalles:\n"
                                    "1. Conecta al servidor\n"
                                    "2. Descarga datos\n"
                                    "3. Copia a red"
                            }
                        ]
                    }
                ]
            }
        ]

        self.current_page = 0
        self.init_context_menu()
        self.setup_ui()

    # =====================================================
    # CONTEXT MENU
    # =====================================================

    def init_context_menu(self):
        """Inicializa menú contextual"""

        self.context_frame = QFrame(self)
        self.context_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)

        self.context_layout = QVBoxLayout(self.context_frame)

        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setStyleSheet("""
            QTextEdit {
                border: none;
                font-size: 12px;
                color: #333;
                background: transparent;
            }
        """)

        # IMPORTANTE: permite ajuste dinámico
        self.context_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.context_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.context_layout.addWidget(self.context_text)

        self.context_close = QPushButton("Cerrar")
        self.context_close.clicked.connect(self.hide_context_menu)
        self.context_layout.addWidget(self.context_close, 0, Qt.AlignRight)

        self.context_frame.hide()

    # =====================================================
    # FIX MENÚ CONTEXTUAL (ÚNICO CAMBIO REAL)
    # =====================================================

    def show_context_menu(self, pos, description, btn):
        """
        FIX:
        - Ajuste dinámico de altura
        - Respeta saltos de línea (\n)
        - Evita corte de texto
        """

        self.context_text.setPlainText(description)

        doc = QTextDocument()
        doc.setDefaultFont(self.context_text.font())
        doc.setPlainText(description)
        doc.setTextWidth(280)

        alto_texto = doc.size().height()
        alto_boton = self.context_close.sizeHint().height()

        alto_total = int(alto_texto + alto_boton + 30)

        alto_total = max(120, min(alto_total, 600))

        self.context_frame.resize(320, alto_total)

        self.context_frame.move(self.width() - 320, 10)

        self.context_frame.show()
        self.context_frame.raise_()

    def hide_context_menu(self):
        self.context_frame.hide()

    # =====================================================
    # UI (SIN CAMBIOS)
    # =====================================================

    def setup_ui(self):
        main = QWidget()
        layout = QVBoxLayout()

        self.title = QLabel("PANEL CONTROL ENTREPRISE")
        self.page_title = QLabel(self.pages_data[0]["title"])

        self.stack = QStackedWidget()

        self.setCentralWidget(main)

    # =====================================================
    # NAV (SIN CAMBIOS)
    # =====================================================

    def next_page(self):
        pass

    def prev_page(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())