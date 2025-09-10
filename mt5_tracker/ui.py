"""
UI - Interfaz de usuario PyQt5

Contiene la clase MT5TrackerApp con toda la interfaz gráfica
y la lógica de interacción con el usuario.
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QTextEdit, QProgressBar, QMessageBox, QSplitter,
                             QGroupBox, QLineEdit, QComboBox, QHeaderView, QInputDialog,
                             QMenu)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon

from .connector import MT5Connector
from .tracker import TradeTracker
from .file_manager import FileManager
from .comments_manager import CommentsManager


class MT5TrackerApp(QMainWindow):
    """Aplicación principal del registrador de operaciones MT5"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.mt5_connector = MT5Connector()
        self.trade_tracker = TradeTracker()
        
        # Pasar la configuración de exportación al FileManager
        self.file_manager = FileManager(config=self.config)
        
        self.comments_manager = CommentsManager()
        self.trades_data = []
        
        self.init_ui()
        self.log("🚀 Registrador de Operaciones MT5 iniciado")
        self.log("💡 Conecta a MT5 y carga las operaciones")
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        app_settings = self.config.get('app_settings', {})
        window_title = app_settings.get('window_title', "MT5 Tracker")
        window_size = app_settings.get('window_size', [1600, 1000])

        self.setWindowTitle(window_title)
        self.setGeometry(50, 50, window_size[0], window_size[1])
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header principal con logo y navegación
        self.create_main_header(main_layout)
        
        # Contenido principal con splitter
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_widget.setLayout(content_layout)
        
        # Splitter para dividir la ventana
        splitter = QSplitter(Qt.Horizontal)
        content_layout.addWidget(splitter)
        
        # Panel izquierdo
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho (tabla)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter (más balanceado)
        splitter.setSizes([550, 1050])
        
        # Agregar contenido principal
        main_layout.addWidget(content_widget)
        
        # Footer con redes sociales
        self.create_social_footer(main_layout)
        
        # Barra de estado
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Listo para usar")
    
    def create_main_header(self, main_layout):
        """Crea el header principal profesional y moderno"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #2A7A9E;
                padding: 12px 16px;
            }
        """)
        
        # Layout horizontal principal
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignVCenter)
        header_widget.setLayout(header_layout)
        
        # Logo (izquierda)
        logo_label = QLabel()
        logo_label.setScaledContents(False)  # Evitar recortes
        try:
            # Cargar el logo desde assets/images/Logo.png
            logo_pixmap = QPixmap("assets/images/Logo.png")
            if not logo_pixmap.isNull():
                # Escalar el logo a máximo 70x70px manteniendo proporción
                scaled_pixmap = logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                # Fallback si no se puede cargar la imagen
                logo_label.setText("🚀")
                logo_label.setFont(QFont("Arial", 42, QFont.Bold))
        except Exception as e:
            # Fallback en caso de error
            logo_label.setText("🚀")
            logo_label.setFont(QFont("Arial", 42, QFont.Bold))
        
        logo_label.setStyleSheet("""
            color: white;
            margin-right: 12px;
        """)
        logo_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(logo_label)
        
        # Sección de textos (derecha del logo)
        text_section = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)
        text_section.setLayout(text_layout)
        
        # Título principal
        main_title = QLabel("MT5 Tracker")
        main_title.setFont(QFont("Arial", 18, QFont.Bold))
        main_title.setStyleSheet("""
            color: white;
            margin: 0;
            padding: 0;
        """)
        main_title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text_layout.addWidget(main_title)
        
        # Subtítulo
        subtitle = QLabel("Registrador automático de operaciones en MT5 | XTRADE")
        subtitle.setFont(QFont("Arial", 13))
        subtitle.setStyleSheet("""
            color: #E6E6E6;
            margin: 0;
            padding: 0;
        """)
        subtitle.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text_layout.addWidget(subtitle)
        
        header_layout.addWidget(text_section)
        
        # Espaciador para empujar los botones a la derecha
        header_layout.addStretch()
        
        # Botones de navegación (derecha)
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)
        nav_layout.setAlignment(Qt.AlignVCenter)
        
        # Botón comunidad
        community_btn = QPushButton("🚀 Comunidad")
        community_btn.clicked.connect(self.open_telegram_community)
        community_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E55A2B;
            }
        """)
        nav_layout.addWidget(community_btn)
        
        # Botón acerca de
        about_btn = QPushButton("ℹ️ Acerca de")
        about_btn.clicked.connect(self.show_about_dialog)
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.25);
                padding: 8px 16px;
                border-radius: 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        nav_layout.addWidget(about_btn)
        
        # Agregar navegación al header
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        header_layout.addWidget(nav_widget)
        
        # Agregar al layout principal
        main_layout.addWidget(header_widget)
    
    def create_left_panel(self):
        """Crea el panel izquierdo con controles"""
        from PyQt5.QtWidgets import QScrollArea
        
        # Crear scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8F9FA;
            }
            QScrollBar:vertical {
                background-color: #E9ECEF;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2E86AB;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #1E6B8B;
            }
        """)
        
        # Widget contenido del scroll
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(30)
        left_widget.setLayout(layout)
        
        # Espaciador superior
        layout.addSpacing(15)
        
        # Sección de conexión
        connection_group = QGroupBox("🔗 Conexión a MetaTrader 5")
        connection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E86AB;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        connection_layout = QVBoxLayout()
        connection_layout.setSpacing(20)
        connection_layout.setContentsMargins(15, 20, 15, 15)
        connection_group.setLayout(connection_layout)
        
        # Campos de conexión
        login_label = QLabel("Login:")
        login_label.setStyleSheet("font-weight: bold; color: #495057; margin-bottom: 8px;")
        connection_layout.addWidget(login_label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Tu login de MT5")
        self.login_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E9ECEF;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2E86AB;
            }
        """)
        connection_layout.addWidget(self.login_input)
        
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("font-weight: bold; color: #495057; margin-bottom: 8px;")
        connection_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Tu contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E9ECEF;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2E86AB;
            }
        """)
        connection_layout.addWidget(self.password_input)
        
        server_label = QLabel("Servidor:")
        server_label.setStyleSheet("font-weight: bold; color: #495057; margin-bottom: 8px;")
        connection_layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Tu servidor MT5")
        self.server_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E9ECEF;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2E86AB;
            }
        """)
        connection_layout.addWidget(self.server_input)
        
        self.connect_btn = QPushButton("🔗 Conectar MT5")
        self.connect_btn.clicked.connect(self.connect_to_mt5)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1E7E34;
            }
        """)
        connection_layout.addWidget(self.connect_btn)
        
        # Botón para desconexión forzada
        self.force_disconnect_btn = QPushButton("🔌 Desconectar Forzadamente")
        self.force_disconnect_btn.clicked.connect(self.force_disconnect_mt5)
        self.force_disconnect_btn.setToolTip("Fuerza la desconexión de MT5 y limpia credenciales guardadas")
        self.force_disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
        """)
        connection_layout.addWidget(self.force_disconnect_btn)
        
        # Botón para verificar estado de conexión
        self.check_status_btn = QPushButton("🔍 Verificar Estado de Conexión")
        self.check_status_btn.clicked.connect(self.check_connection_status)
        self.check_status_btn.setToolTip("Verifica el estado actual de la conexión a MT5")
        self.check_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117A8B;
            }
        """)
        connection_layout.addWidget(self.check_status_btn)
        
        layout.addWidget(connection_group)
        
        # Sección de operaciones
        operations_group = QGroupBox("📋 Operaciones")
        operations_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E86AB;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        operations_layout = QVBoxLayout()
        operations_layout.setSpacing(20)
        operations_layout.setContentsMargins(15, 20, 15, 15)
        operations_group.setLayout(operations_layout)
        
        self.load_trades_btn = QPushButton("📄 Cargar Todas las Operaciones (5 años)")
        self.load_trades_btn.clicked.connect(self.load_trades)
        self.load_trades_btn.setEnabled(False)
        self.load_trades_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover:enabled {
                background-color: #0056B3;
            }
            QPushButton:pressed:enabled {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6C757D;
                color: #ADB5BD;
            }
        """)
        operations_layout.addWidget(self.load_trades_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Tabla")
        self.clear_btn.clicked.connect(self.clear_trades)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
            QPushButton:pressed {
                background-color: #545B62;
            }
        """)
        operations_layout.addWidget(self.clear_btn)
        
        layout.addWidget(operations_group)
        
        # Sección de exportación
        export_group = QGroupBox("📊 Exportar Operaciones")
        export_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E86AB;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        export_layout = QVBoxLayout()
        export_layout.setSpacing(20)
        export_layout.setContentsMargins(15, 20, 15, 15)
        export_group.setLayout(export_layout)
        
        # Selector de formato
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setStyleSheet("font-weight: bold; color: #495057;")
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "XLSX", "Ambos"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E9ECEF;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #2E86AB;
            }
        """)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        export_layout.addLayout(format_layout)
        
        self.export_btn = QPushButton("📊 Exportar Operaciones")
        self.export_btn.clicked.connect(self.export_trades)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover:enabled {
                background-color: #218838;
            }
            QPushButton:pressed:enabled {
                background-color: #1E7E34;
            }
            QPushButton:disabled {
                background-color: #6C757D;
                color: #ADB5BD;
            }
        """)
        export_layout.addWidget(self.export_btn)
        
        self.open_folder_btn = QPushButton("📁 Abrir Carpeta")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #6F42C1;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5A32A3;
            }
            QPushButton:pressed {
                background-color: #4C2A85;
            }
        """)
        export_layout.addWidget(self.open_folder_btn)
        
        layout.addWidget(export_group)
        
        # Sección de comunidad
        community_group = QGroupBox("🚀 Comunidad XTRADE")
        community_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E86AB;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        community_layout = QVBoxLayout()
        community_layout.setSpacing(20)
        community_layout.setContentsMargins(15, 20, 15, 15)
        community_group.setLayout(community_layout)
        
        self.join_community_btn = QPushButton("🚀 Unirme a la Comunidad")
        self.join_community_btn.clicked.connect(self.open_telegram_community)
        self.join_community_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1E6B8B;
            }
        """)
        community_layout.addWidget(self.join_community_btn)
        
        self.about_btn = QPushButton("ℹ️ Acerca de XTRADE")
        self.about_btn.clicked.connect(self.show_about_dialog)
        self.about_btn.setStyleSheet("""
            QPushButton {
                background-color: #F4F4F4;
                color: #333333;
                border: 1px solid #CCCCCC;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
        """)
        community_layout.addWidget(self.about_btn)
        
        layout.addWidget(community_group)
        
        # Sección de información
        info_group = QGroupBox("ℹ️ Información")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E86AB;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(15, 20, 15, 15)
        info_group.setLayout(info_layout)
        
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(200)
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E9ECEF;
                border-radius: 6px;
                padding: 10px;
                background-color: #F8F9FA;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(self.log_area)
        
        layout.addWidget(info_group)
        
        # Espaciador
        layout.addStretch()
        
        # Configurar el scroll area
        scroll_area.setWidget(left_widget)
        
        return scroll_area
    
    def create_right_panel(self):
        """Crea el panel derecho con la tabla"""
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #E9ECEF;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        right_widget.setLayout(layout)
        
        # Título de la tabla
        table_title = QLabel("📋 Operaciones Registradas")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet("color: #2E86AB; margin-bottom: 15px;")
        layout.addWidget(table_title)
        
        # Tabla de operaciones
        self.trades_table = QTableWidget()
        self.trades_table.setAlternatingRowColors(True)
        self.trades_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trades_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.trades_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Configuración de encabezados
        self.trades_table.verticalHeader().setVisible(True)
        self.trades_table.verticalHeader().setDefaultSectionSize(30)
        self.trades_table.verticalHeader().setMinimumSectionSize(26)
        self.trades_table.verticalHeader().setFixedWidth(46)
        self.trades_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.trades_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Configuración del encabezado horizontal
        self.trades_table.horizontalHeader().setFixedHeight(34)
        self.trades_table.horizontalHeader().setDefaultAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Configuración de word wrap
        self.trades_table.setWordWrap(False)
        
        # Estilo de la tabla
        self.trades_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E9ECEF;
                background-color: white;
                alternate-background-color: #F8F9FA;
                selection-background-color: #E8F2FF;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #2E86AB;
                color: white;
                padding: 6px 8px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QHeaderView::section:vertical {
                background: #1A6C8A;
            }
            QTableCornerButton::section {
                background: #2E86AB;
                border: none;
            }
            QTableView::item {
                padding: 6px 8px;
            }
            QTableView::item:selected {
                background: #E8F2FF;
                color: #0D1B2A;
            }
        """)
        
        # Permitir edición solo en la columna de comentarios
        self.trades_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
        # Conectar señal para detectar cambios en comentarios
        self.trades_table.itemChanged.connect(self.on_comment_changed)
        
        # Configurar columnas
        headers = ['Position ID (Ticket)', 'Símbolo', 'Tipo', 'Volumen', 'Precio', 'Beneficio', 'Fecha Apertura', 'Fecha Cierre', 'Comentario']
        self.trades_table.setColumnCount(len(headers))
        self.trades_table.setHorizontalHeaderLabels(headers)
        
        # Configurar encabezados
        header = self.trades_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Configurar ancho de columnas específicas
        self.trades_table.setColumnWidth(0, 100)  # Position ID - más ancho para números
        self.trades_table.setColumnWidth(1, 80)   # Símbolo
        self.trades_table.setColumnWidth(2, 80)   # Tipo
        self.trades_table.setColumnWidth(3, 80)   # Volumen
        self.trades_table.setColumnWidth(4, 100)  # Precio
        self.trades_table.setColumnWidth(5, 100)  # Beneficio
        self.trades_table.setColumnWidth(6, 120)  # Fecha Apertura
        self.trades_table.setColumnWidth(7, 120)  # Fecha Cierre
        # Comentario se estira automáticamente
        
        layout.addWidget(self.trades_table)
        
        # Botones de tabla
        table_buttons_layout = QHBoxLayout()
        table_buttons_layout.setSpacing(15)
        
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.clicked.connect(self.refresh_trades)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117A8B;
            }
        """)
        table_buttons_layout.addWidget(self.refresh_btn)
        
        self.clear_table_btn = QPushButton("🗑️ Limpiar")
        self.clear_table_btn.clicked.connect(self.clear_trades)
        self.clear_table_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
        """)
        table_buttons_layout.addWidget(self.clear_table_btn)
        
        # Espaciador
        table_buttons_layout.addStretch()
        
        layout.addLayout(table_buttons_layout)
        
        return right_widget
    
    def create_social_footer(self, main_layout):
        """Crea el footer con enlaces a redes sociales"""
        # Crear widget para el footer
        footer_widget = QWidget()
        footer_widget.setFixedHeight(50)
        footer_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F8F9FA, stop:1 #E9ECEF);
                border-top: 1px solid #DEE2E6;
            }
        """)
        
        # Layout horizontal para el footer
        footer_layout = QHBoxLayout()
        footer_widget.setLayout(footer_layout)
        
        # Texto de marca
        brand_text = QLabel("Síguenos en redes sociales:")
        brand_text.setStyleSheet("color: #495057; font-weight: bold; font-size: 12px; margin-right: 10px;")
        footer_layout.addWidget(brand_text)
        
        # Botón Instagram
        instagram_btn = QPushButton("📷 Instagram")
        instagram_btn.clicked.connect(self.open_instagram)
        instagram_btn.setStyleSheet("""
            QPushButton {
                background-color: #E4405F;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 6px;
            }
            QPushButton:hover {
                background-color: #C13584;
            }
        """)
        footer_layout.addWidget(instagram_btn)
        
        # Botón YouTube
        youtube_btn = QPushButton("📺 YouTube")
        youtube_btn.clicked.connect(self.open_youtube)
        youtube_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 6px;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
        """)
        footer_layout.addWidget(youtube_btn)
        
        # Botón TikTok
        tiktok_btn = QPushButton("🎬 TikTok")
        tiktok_btn.clicked.connect(self.open_tiktok)
        tiktok_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 6px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        footer_layout.addWidget(tiktok_btn)
        
        # Botón Telegram
        telegram_btn = QPushButton("💬 Telegram")
        telegram_btn.clicked.connect(self.open_telegram)
        telegram_btn.setStyleSheet("""
            QPushButton {
                background-color: #0088CC;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 6px;
            }
            QPushButton:hover {
                background-color: #006699;
            }
        """)
        footer_layout.addWidget(telegram_btn)
        
        # Espaciador
        footer_layout.addStretch()
        
        # Texto de copyright
        copyright_text = QLabel("© 2025 XTRADE - Todos los derechos reservados")
        copyright_text.setStyleSheet("color: #6C757D; font-size: 12px; font-weight: bold;")
        footer_layout.addWidget(copyright_text)
        
        # Agregar el footer al layout principal
        main_layout.addWidget(footer_widget)
    
    def show_context_menu(self, position):
        """Muestra el menú contextual para comentarios"""
        row = self.trades_table.rowAt(position.y())
        if row >= 0:
            menu = QMenu()
            
            add_comment_action = menu.addAction("✏️ Agregar Comentario Manual")
            
            action = menu.exec_(self.trades_table.mapToGlobal(position))
            
            if action == add_comment_action:
                self.add_manual_comment(row)
    
    def on_comment_changed(self, item):
        """Maneja cambios en comentarios editados directamente en la tabla"""
        row = item.row()
        column = item.column()
        
        # Solo procesar cambios en la columna de comentarios (columna 8)
        if column == 8 and row < len(self.trades_data):
            new_comment = item.text()
            old_comment = self.trades_data[row].get('comment', '')
            
            if new_comment != old_comment:
                self.trades_data[row]['comment'] = new_comment
                
                # Guardar comentario inmediatamente
                account_id = self.mt5_connector.current_login
                position_id = self.trades_data[row].get('position_id', '')
                
                if account_id and position_id:
                    self.comments_manager.save_comment(account_id, position_id, new_comment)
                
                self.log(f"✅ Comentario actualizado y guardado para Position ID {position_id}: '{new_comment}'")
    
    def add_manual_comment(self, row):
        """Agrega comentario manual a una operación"""
        current_comment = self.trades_data[row].get('comment', '')
        text, ok = QInputDialog.getText(
            self, 
            "Agregar Comentario", 
            "Escribe tu comentario:",
            QLineEdit.Normal,
            current_comment
        )
        
        if ok and text:
            self.trades_data[row]['comment'] = text
            self.trades_table.setItem(row, 8, QTableWidgetItem(text))
            
            # Guardar comentario inmediatamente
            account_id = self.mt5_connector.current_login
            position_id = self.trades_data[row].get('position_id', '')
            
            if account_id and position_id:
                self.comments_manager.save_comment(account_id, position_id, text)
            
            self.log(f"✅ Comentario agregado y guardado para Position ID {position_id}: '{text}'")
    
    def log(self, message):
        """Registra un mensaje en el área de logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_area.append(log_message)
        print(log_message)
    
    def connect_to_mt5(self):
        """Conecta a MetaTrader 5"""
        self.log("🔌 Conectando a MetaTrader 5...")
        self.connect_btn.setEnabled(False)
        
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        server = self.server_input.text().strip()
        
        # Validar que se ingresaron credenciales
        if not login or not password or not server:
            QMessageBox.warning(self, "Credenciales Faltantes", 
                              "Por favor ingresa login, contraseña y servidor antes de conectar.")
            self.connect_btn.setEnabled(True)
            return
        
        # Debug: mostrar credenciales limpias
        self.log(f"🔍 DEBUG: Credenciales limpias:")
        self.log(f"   📊 Login: '{login}' (longitud: {len(login)})")
        self.log(f"   📊 Password: '{password}' (longitud: {len(password)})")
        self.log(f"   📊 Server: '{server}' (longitud: {len(server)})")
        
        success = self.mt5_connector.connect(login=login, password=password, server=server)
        
        if success:
            self.log("✅ Conectado a MetaTrader 5")
            
            # Verificar que estamos en la cuenta correcta
            account_info = self.mt5_connector.get_account_info()
            if account_info:
                expected_login = str(login)
                actual_login = str(account_info.login)
                
                # Debug: mostrar valores exactos para comparación
                self.log(f"🔍 DEBUG: Comparando cuentas:")
                self.log(f"   📊 Login esperado: '{expected_login}' (tipo: {type(expected_login)})")
                self.log(f"   📊 Login actual: '{actual_login}' (tipo: {type(actual_login)})")
                self.log(f"   📊 ¿Son iguales? {expected_login == actual_login}")
                
                if expected_login == actual_login:
                    self.log(f"✅ Conectado a la cuenta correcta: {actual_login}")
                    self.status_bar.showMessage(f"Conectado a MT5 - Cuenta: {actual_login}")
                else:
                    self.log(f"⚠️ ADVERTENCIA: Conectado a cuenta {actual_login} en lugar de {expected_login}")
                    QMessageBox.warning(self, "Cuenta Incorrecta", 
                                      f"Se conectó a la cuenta {actual_login} en lugar de {expected_login}.\n\n"
                                      "Esto puede indicar que MT5 está usando credenciales guardadas.\n"
                                      "Cierra MT5 completamente y vuelve a intentar.")
                    self.status_bar.showMessage(f"⚠️ Cuenta incorrecta: {actual_login}")
            
            self.load_trades_btn.setEnabled(True)
        else:
            self.log("❌ Error de conexión a MetaTrader 5")
            QMessageBox.critical(self, "Error de Conexión", 
                               "No se pudo conectar a MetaTrader 5.\n\n"
                               "Verifica que:\n"
                               "1. MT5 esté cerrado completamente\n"
                               "2. Las credenciales sean correctas\n"
                               "3. El servidor sea válido")
        
        self.connect_btn.setEnabled(True)
    
    def force_disconnect_mt5(self):
        """Desconecta forzadamente de MetaTrader 5"""
        self.log("🔌 Desconectando forzadamente de MetaTrader 5...")
        self.mt5_connector.disconnect()
        self.log("✅ Desconexión forzada completada")
        self.status_bar.showMessage("Desconectado forzadamente")
    
    def check_connection_status(self):
        """Verifica el estado actual de la conexión a MT5"""
        self.log("🔍 Verificando estado de conexión a MT5...")
        if self.mt5_connector.connected:
            self.log("✅ MT5 está conectado.")
            QMessageBox.information(self, "Estado de Conexión", "MT5 está conectado.")
        else:
            self.log("❌ MT5 no está conectado.")
            QMessageBox.warning(self, "Estado de Conexión", "MT5 no está conectado. Por favor, inténtalo de nuevo.")
    
    def load_trades(self):
        """Carga las operaciones de MT5"""
        if not self.mt5_connector.connected:
            self.log("❌ No conectado a MT5")
            return
        
        self.log("📥 Cargando operaciones...")
        self.load_trades_btn.setEnabled(False)
        
        # Obtener operaciones crudas
        raw_trades = self.mt5_connector.get_raw_trades()
        
        if raw_trades:
            # Procesar operaciones
            self.trades_data = self.trade_tracker.process_trades(raw_trades)
            
            if self.trades_data:
                # Aplicar comentarios guardados
                account_id = self.mt5_connector.current_login
                if account_id:
                    self.trades_data = self.comments_manager.apply_comments_to_trades(self.trades_data, account_id)
                
                self.log(f"✅ Cargadas {len(self.trades_data)} operaciones")
                self.export_btn.setEnabled(True)
            else:
                self.log("❌ No se encontraron operaciones válidas")
        else:
            self.log("❌ No se encontraron operaciones")
        
        self.update_trades_table()
        self.load_trades_btn.setEnabled(True)
    
    def update_trades_table(self):
        """Actualiza la tabla de operaciones"""
        self.trades_table.setRowCount(len(self.trades_data))
        
        headers = ['Position ID (Ticket)', 'Símbolo', 'Tipo', 'Volumen', 'Precio', 'Beneficio', 'Fecha Apertura', 'Fecha Cierre', 'Comentario']
        
        for row, trade in enumerate(self.trades_data):
            # Insertar datos en la tabla (solo lectura)
            for col in range(8):  # Primeras 8 columnas son solo lectura
                value = trade.get(['position_id', 'symbol', 'type', 'volume', 'price', 'profit', 'opening_time', 'closing_time'][col], '')
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Hacer no editable
                
                # Sin estilo especial - todas las columnas se ven iguales
                
                self.trades_table.setItem(row, col, item)
            
            # Columna de comentarios (editable)
            comment_item = QTableWidgetItem(str(trade.get('comment', '')))
            comment_item.setFlags(comment_item.flags() | Qt.ItemIsEditable)  # Hacer editable
            self.trades_table.setItem(row, 8, comment_item)
            
            # Colorear filas según beneficio (incluyendo todas las columnas)
            profit = trade.get('profit', 0)
            if isinstance(profit, (int, float)):
                if profit > 0:
                    for col in range(0, 9):  # Incluir todas las columnas (0-8)
                        self.trades_table.item(row, col).setBackground(QColor(200, 255, 200))
                elif profit < 0:
                    for col in range(0, 9):  # Incluir todas las columnas (0-8)
                        self.trades_table.item(row, col).setBackground(QColor(255, 200, 200))
    
    def refresh_trades(self):
        """Actualiza las operaciones"""
        self.load_trades()
    
    def export_trades(self):
        """Exporta las operaciones de forma incremental"""
        if not self.trades_data:
            self.log("❌ No hay operaciones para exportar")
            return
        
        # Obtener el account_id de la conexión MT5
        account_id = self.mt5_connector.current_login
        if not account_id:
            self.log("❌ No se puede obtener el ID de la cuenta")
            return
        
        try:
            self.log(f"📤 Exportando operaciones para cuenta {account_id}...")
            format_choice = self.format_combo.currentText()
            
            if format_choice in ["CSV", "Ambos"]:
                csv_path = self.file_manager.save_to_csv(self.trades_data, account_id)
                self.log(f"✅ CSV guardado en: {csv_path}")
            
            if format_choice in ["XLSX", "Ambos"]:
                xlsx_path = self.file_manager.save_to_xlsx(self.trades_data, account_id)
                self.log(f"✅ XLSX guardado en: {xlsx_path}")
            
            self.log("✅ Exportación incremental completada")
            
        except PermissionError as e:
            self.log(f"❌ Error de permisos: {e}")
            QMessageBox.warning(
                self, 
                "⚠️ Archivo Abierto",
                f"ERROR: {e}\n\n"
                "SOLUCIÓN:\n"
                "1. Cierra Excel completamente\n"
                "2. Cierra cualquier editor de texto que tenga abierto el archivo\n"
                "3. Vuelve a exportar\n\n"
                "El archivo debe estar cerrado para poder actualizarlo."
            )
        except Exception as e:
            self.log(f"❌ Error al exportar: {e}")
            QMessageBox.critical(self, "Error de Exportación", f"Error al exportar: {e}")
    
    def open_output_folder(self):
        """Abre la carpeta de salida"""
        self.file_manager.open_output_folder()
        self.log("📁 Carpeta de salida abierta")
    
    def open_instagram(self):
        """Abre Instagram de XTRADE"""
        import webbrowser
        url = "https://www.instagram.com/xtrade_pr/"
        webbrowser.open(url)
        self.log("📷 Abriendo Instagram de XTRADE")
    
    def open_youtube(self):
        """Abre YouTube de XTRADE"""
        import webbrowser
        url = "https://youtube.com/@xtrade_pr?si=waZHfIh_jlytOgGN"
        webbrowser.open(url)
        self.log("📺 Abriendo YouTube de XTRADE")
    
    def open_telegram(self):
        """Abre Telegram de XTRADE"""
        import webbrowser
        url = "https://t.me/XtradeTelegram"
        webbrowser.open(url)
        self.log("💬 Abriendo Telegram de XTRADE")
    
    def open_tiktok(self):
        """Abre TikTok de XTRADE"""
        import webbrowser
        url = "https://www.tiktok.com/@xtrade_pr?is_from_webapp=1&sender_device=pc"
        webbrowser.open(url)
        self.log("🎵 Abriendo TikTok de XTRADE")
    
    def open_telegram_community(self):
        """Abre el grupo de Telegram de la comunidad"""
        import webbrowser
        url = "https://t.me/XtradeTelegram"
        webbrowser.open(url)
        self.log("🚀 Abriendo comunidad de XTRADE en Telegram")
    
    def show_about_dialog(self):
        """Muestra la ventana 'Acerca de XTRADE'"""
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("Acerca de XTRADE")
        about_dialog.setIcon(QMessageBox.Information)
        
        # Crear contenido personalizado
        about_text = """
        <div style='text-align: center; margin: 20px;'>
            <h2 style='color: #2E86AB; margin-bottom: 20px;'>🚀 XTRADE</h2>
            
            <p style='font-size: 14px; line-height: 1.6; margin-bottom: 20px;'>
                Este proyecto nació para ayudar a los traders a registrar y analizar 
                sus operaciones de una forma más automatizada y profesional.
            </p>
            
            <p style='font-size: 14px; line-height: 1.6; margin-bottom: 20px;'>
                Si tienes preguntas, sugerencias para mejorar el proyecto, 
                o quieres formar parte de nuestra comunidad de traders, 
                ¡únete a nosotros!
            </p>
            
            <div style='margin: 20px 0;'>
                <a href='https://t.me/XtradeTelegram' 
                   style='background-color: #0088CC; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold;'>
                    💬 Únete a nuestra comunidad en Telegram
                </a>
            </div>
            
            <p style='font-size: 12px; color: #666; margin-top: 20px;'>
                © 2025 XTRADE - Todos los derechos reservados
            </p>
        </div>
        """
        
        about_dialog.setText(about_text)
        about_dialog.setTextFormat(Qt.RichText)
        
        # Botones
        telegram_btn = about_dialog.addButton("💬 Telegram", QMessageBox.ActionRole)
        close_btn = about_dialog.addButton("Cerrar", QMessageBox.RejectRole)
        
        about_dialog.exec_()
        
        # Manejar clic en botón de Telegram
        if about_dialog.clickedButton() == telegram_btn:
            self.open_telegram_community()
    
    def clear_trades(self):
        """Limpia la tabla de operaciones"""
        self.trades_data = []
        self.trades_table.setRowCount(0)
        self.log("🗑️ Tabla limpiada")
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        self.mt5_connector.disconnect()
        event.accept()

