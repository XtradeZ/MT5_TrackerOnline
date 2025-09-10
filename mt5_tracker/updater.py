from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon

import requests
import hashlib
import subprocess
import tempfile
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QTextEdit, QProgressBar, QMessageBox, QSplitter,
                             QGroupBox, QLineEdit, QComboBox, QHeaderView, QInputDialog,
                             QMenu, QDialog)


APP_VERSION = "1.0.0"
GITHUB_REPO = "XtradeZ/MT5_TrackerOnline"


class UpdateWorker(QThread):
    """
    Worker para descargar la actualización en segundo plano.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, download_url, checksum_url, temp_dir):
        super().__init__()
        self.download_url = download_url
        self.checksum_url = checksum_url
        self.temp_dir = temp_dir
        self.installer_path = ""
        self.checksum_path = ""

    def run(self):
        try:
            # Descargar instalador
            self.installer_path = self._download_file(self.download_url, "installer.exe")
            
            # Descargar checksum
            self.checksum_path = self._download_file(self.checksum_url, "checksums.txt")

            self.finished.emit(self.installer_path, self.checksum_path)

        except Exception as e:
            self.error.emit(f"Error durante la descarga: {e}")

    def _download_file(self, url, filename):
        """Descarga un archivo desde una URL y reporta el progreso."""
        local_filename = os.path.join(self.temp_dir, filename)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = 0
        
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if total_size > 0:
                        progress = int((bytes_downloaded / total_size) * 100)
                        if filename == "installer.exe": # Solo reportar progreso para el archivo grande
                            self.progress.emit(progress)
        
        return local_filename


class Updater:
    """
    Gestiona la lógica de auto-actualización.
    """
    def __init__(self):
        self.api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    def check_for_updates(self):
        """
        Comprueba si hay una nueva versión disponible en GitHub.
        Retorna la información de la release si hay actualización, sino None.
        """
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release.get('tag_name', '0.0.0').lstrip('v')
            
            # Comparar versiones
            if latest_version > APP_VERSION:
                return latest_release
        except requests.RequestException as e:
            print(f"Error al verificar actualizaciones: {e}")
            return None
        return None

    @staticmethod
    def verify_checksum(installer_path, checksum_path):
        """
        Verifica el hash SHA256 del instalador.
        """
        try:
            with open(installer_path, 'rb') as f:
                installer_hash = hashlib.sha256(f.read()).hexdigest()
            
            with open(checksum_path, 'r') as f:
                # Buscar el hash que corresponde al instalador
                for line in f:
                    if "installer.exe" in line:
                        expected_hash = line.split()[0]
                        return installer_hash == expected_hash
        except Exception as e:
            print(f"Error al verificar checksum: {e}")
            return False
        return False

    @staticmethod
    def run_installer(installer_path):
        """
        Ejecuta el instalador y cierra la aplicación actual.
        """
        try:
            # Iniciar el instalador en un nuevo proceso
            subprocess.Popen([installer_path])
            # Cerrar la aplicación actual
            QApplication.instance().quit()
        except Exception as e:
            print(f"Error al ejecutar el instalador: {e}")
            QMessageBox.critical(None, "Error de Instalación", 
                               f"No se pudo iniciar el instalador: {e}")


class UpdateProgressDialog(QDialog):
    """
    Diálogo para mostrar el progreso de la descarga de la actualización.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Actualizando aplicación")
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Iniciando descarga...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Ocultar el botón de cerrar
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowSystemMenuHint, False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Descargando... {value}%")
