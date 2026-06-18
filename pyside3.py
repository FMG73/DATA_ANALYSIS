import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QSize, Qt, QTimer, QPoint
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QMessageBox, QFrame, QStackedWidget,
    QTextEdit, QSizePolicy
)
from PySide6.QtGui import QTextDocument


# =========================================================
# RUTAS SCRIPTS
# =========================================================

oas_025_red: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts_flujos\025_descarga_copia.py'
oas_505_current: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_505_current.py'
oas_713: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_713.py'
oas_940: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\obiee\oas_940.py'

red: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\red\acceso_redes.py'
vpn: str = r'C:\Python\JupyterLab\Lab\PMELERO_NEW\scripts\red\acceso_redes_vpn.py'


# =========================================================
# ESTILO GLOBAL
# =========================================================

APP_DEFAULT_STYLE: Dict[str, Any] = {
    "bg": "#4CAF50",
    "hover": "#45A049",
    "pressed": "#2E7D32",
    "text_color": "black",
    "font_size": 11,
    "border_radius": 10,
    "padding": "10px 20px"
}


# =========================================================
# MAIN WINDOW
# =========================================================

class MainWindow(QMainWindow):
    """
    Ventana principal del panel de scripts.

    Características:
    - Navegación por páginas
    - Columnas dinámicas
    - Botones que ejecutan scripts Python
    - Menú contextual dinámico con ajuste automático de altura
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("CONSOLA SCRIPTS")
        self.resize(QSize(900, 500))

        self.current_page: int = 0

        self.pages_data: List[Dict[str, Any]] = self._build_pages()

        self.init_context_menu()
        self.setup_ui()

    # =====================================================
    # UI SETUP
    # =====================================================

    def setup_ui(self) -> None:
        main: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout()

        self.title: QLabel = QLabel("PANEL CONTROL ENTERPRISE")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:18px;font-weight:bold;")

        self.page_title: QLabel = QLabel(self.pages_data[0]["title"])
        self.page_title.setAlignment(Qt.AlignCenter)
        self.page_title.setStyleSheet("font-size:14px;font-weight:bold;")

        self.stack: QStackedWidget = QStackedWidget()

        for page in self.pages_data:
            self.stack.addWidget(self._create_page(page))

        nav: QHBoxLayout = QHBoxLayout()

        self.btn_prev: QPushButton = QPushButton("❮")
        self.btn_next: QPushButton = QPushButton("❯")

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

        self.context_frame.setParent(self.centralWidget())
        self.context_frame.raise_()

        self.update_nav()

    # =====================================================
    # CONTEXT MENU (FIX REAL)
    # =====================================================

    def init_context_menu(self) -> None:
        """
        Inicializa el panel contextual.
        """

        self.context_frame: QFrame = QFrame(self)

        self.context_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)

        self.context_layout: QVBoxLayout = QVBoxLayout(self.context_frame)

        # Texto
        self.context_text: QTextEdit = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setStyleSheet("""
            QTextEdit {
                border: none;
                font-size: 12px;
                color: #333;
                background: transparent;
            }
        """)

        self.context_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.context_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.context_layout.addWidget(self.context_text)

        # Botón cerrar
        self.context_close: QPushButton = QPushButton("Cerrar")
        self.context_close.clicked.connect(self.hide_context_menu)

        self.context_layout.addWidget(self.context_close, 0, Qt.AlignRight)

        self.context_frame.hide()

    # =====================================================
    # FIX MENÚ CONTEXTUAL
    # =====================================================

    def show_context_menu(self, pos: QPoint, description: str, btn: QPushButton) -> None:
        """
        Muestra el panel contextual ajustando su altura dinámicamente.

        FIX:
        - Usa QTextDocument para calcular altura real del texto
        - Respeta saltos de línea (\n)
        - Evita tamaño fijo que cortaba contenido
        """

        self.context_text.setPlainText(description)

        doc: QTextDocument = self.context_text.document()
        doc.setTextWidth(280)

        doc_height: float = doc.size().height()
        button_height: int = self.context_close.sizeHint().height()

        total_height: int = int(doc_height + button_height + 30)

        total_height = max(120, min(total_height, 600))

        self.context_frame.resize(320, total_height)

        x: int = self.width() - self.context_frame.width() - 10
        y: int = 10

        self.context_frame.move(x, y)

        self.context_frame.show()
        self.context_frame.raise_()

    def hide_context_menu(self) -> None:
        """Oculta el panel contextual."""
        self.context_frame.hide()

    # =====================================================
    # PAGES (simplificado para foco en fix)
    # =====================================================

    def _create_page(self, page_data: Dict[str, Any]) -> QWidget:
        page: QWidget = QWidget()
        layout: QHBoxLayout = QHBoxLayout(page)

        for column in page_data["columns"]:
            layout.addWidget(self._create_column(column))

        return page

    def _create_column(self, column_data: Dict[str, Any]) -> QFrame:
        frame: QFrame = QFrame()
        layout: QVBoxLayout = QVBoxLayout(frame)

        title: QLabel = QLabel(column_data["title"])
        layout.addWidget(title)

        for script in column_data["scripts"]:
            btn: QPushButton = self._create_button(script)
            layout.addWidget(btn)

        return frame

    def _create_button(self, script: Dict[str, Any]) -> QPushButton:
        btn: QPushButton = QPushButton(script["name"])

        btn.setToolTip(script.get("tooltip", ""))

        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, d=script.get("right_click_description", ""), b=btn:
            self.show_context_menu(pos, d, b)
        )

        btn.clicked.connect(
            lambda _, p=script["path"]: self.run_script(p)
        )

        return btn

    # =====================================================
    # SCRIPT EXECUTION
    # =====================================================

    def run_script(self, path: str) -> None:
        if not Path(path).exists():
            QMessageBox.critical(self, "Error", f"No existe: {path}")
            return

        subprocess.Popen([sys.executable, path])

    # =====================================================
    # NAVIGATION
    # =====================================================

    def next_page(self) -> None:
        if self.current_page < len(self.pages_data) - 1:
            self.current_page += 1
            self.stack.setCurrentIndex(self.current_page)
            self.page_title.setText(self.pages_data[self.current_page]["title"])
            self.update_nav()

    def prev_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.setCurrentIndex(self.current_page)
            self.page_title.setText(self.pages_data[self.current_page]["title"])
            self.update_nav()

    def update_nav(self) -> None:
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.pages_data) - 1)

    # =====================================================
    # DATA
    # =====================================================

    def _build_pages(self) -> List[Dict[str, Any]]:
        return []  # (lo puedes mantener igual que el tuyo)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())