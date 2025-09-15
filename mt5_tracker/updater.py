import requests
import hashlib
import subprocess
import tempfile
import os
import time
import sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QProgressBar, QMessageBox, QDialog


APP_VERSION = "1.0.1"
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
            # Descargar update.zip
            self.zip_path = self._download_file(self.download_url, "update.zip")
            
            # Descargar checksum
            self.checksum_path = self._download_file(self.checksum_url, "checksums.txt")

            self.finished.emit(self.zip_path, self.checksum_path)

        except Exception as e:
            self.error.emit(f"Error durante la descarga: {e}")

    def _download_file(self, url, filename):
        """Descarga un archivo desde una URL y reporta el progreso."""
        local_filename = os.path.join(self.temp_dir, filename)
        
        # Reintentos para descargas más robustas
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=60)
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
                                if filename == "update.zip": # Solo reportar progreso para el archivo grande
                                    self.progress.emit(progress)
                
                return local_filename
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Intento {attempt + 1} fallido, reintentando... {e}")
                time.sleep(2)


class Updater:
    """
    Gestiona la lógica de auto-actualización.
    """
    def __init__(self):
        self.api_url = f"https://github.com/{GITHUB_REPO}/releases/latest/download/update.json"
    
    def check_for_updates(self):
        """
        Comprueba si hay una nueva versión disponible en GitHub.
        Retorna la información de la release si hay actualización, sino None.
        """
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            update_info = response.json()
            latest_version = update_info.get('version', '0.0.0')
            
            # Comparar versiones
            if self._compare_versions(latest_version, APP_VERSION):
                return update_info
        except requests.RequestException as e:
            print(f"Error al verificar actualizaciones: {e}")
            return None
        return None
    
    def _compare_versions(self, version1, version2):
        """Compara dos versiones semánticas"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        return version_tuple(version1) > version_tuple(version2)

    @staticmethod
    def verify_checksum(zip_path, checksum_path):
        """
        Verifica el hash SHA256 del archivo zip.
        """
        try:
            with open(zip_path, 'rb') as f:
                zip_hash = hashlib.sha256(f.read()).hexdigest()
            
            with open(checksum_path, 'r') as f:
                # Buscar el hash que corresponde al update.zip
                for line in f:
                    if "update.zip" in line:
                        expected_hash = line.split()[0]
                        return zip_hash == expected_hash
        except Exception as e:
            print(f"Error al verificar checksum: {e}")
            return False
        return False

    @staticmethod
    def run_updater(zip_path):
        """
        Ejecuta el updater independiente y cierra la aplicación actual.
        """
        try:
            # Obtener directorio de instalación
            install_dir = os.path.dirname(os.path.abspath(sys.executable))
            
            # Buscar updater.exe en el directorio de instalación
            updater_path = os.path.join(install_dir, "updater.exe")
            
            if not os.path.exists(updater_path):
                QMessageBox.critical(None, "Error de Actualización", 
                                   "No se encontró updater.exe en el directorio de instalación")
                return
            
            # Iniciar el updater con los parámetros necesarios
            subprocess.Popen([updater_path, zip_path, install_dir])
            
            # Cerrar la aplicación actual
            QApplication.instance().quit()
        except Exception as e:
            print(f"Error al ejecutar el updater: {e}")
            QMessageBox.critical(None, "Error de Actualización", 
                               f"No se pudo iniciar el updater: {e}")


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