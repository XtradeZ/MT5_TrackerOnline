"""
App - Entrypoint principal de la aplicación

Punto de entrada de la aplicación MT5 Trading Journal.
Crea la QApplication, instancia la UI y ejecuta el bucle principal.
"""

import sys
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import tempfile
import os
from PyQt5.QtWidgets import QMessageBox

from .ui import MT5TrackerApp
from .updater import Updater, UpdateProgressDialog, UpdateWorker, APP_VERSION

CONFIG_FILE = 'config_simple.json'

def handle_update(latest_release):
    """
    Gestiona el proceso de actualización.
    """
    latest_version = latest_release.get('tag_name', '0.0.0').lstrip('v')
    update_message = f"Nueva versión {latest_version} disponible. ¿Quieres actualizar ahora?"
    
    reply = QMessageBox.question(None, "Actualización Disponible", update_message,
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
        assets = latest_release.get('assets', [])
        installer_asset = next((a for a in assets if a['name'].endswith('.exe')), None)
        checksum_asset = next((a for a in assets if 'checksums' in a['name']), None)

        if not installer_asset or not checksum_asset:
            QMessageBox.critical(None, "Error de Actualización", "No se encontraron los archivos de instalación.")
            return False # Indica que no se pudo actualizar

        download_url = installer_asset['browser_download_url']
        checksum_url = checksum_asset['browser_download_url']

        temp_dir = tempfile.mkdtemp()
        progress_dialog = UpdateProgressDialog()
        
        update_worker = UpdateWorker(download_url, checksum_url, temp_dir)

        def on_finished(installer_path, checksum_path):
            progress_dialog.close()
            if Updater.verify_checksum(installer_path, checksum_path):
                Updater.run_installer(installer_path)
            else:
                QMessageBox.critical(None, "Error de Verificación", "El checksum del archivo no coincide. Se cancela la instalación.")
        
        def on_error(error_message):
            progress_dialog.close()
            QMessageBox.critical(None, "Error de Descarga", error_message)

        update_worker.progress.connect(progress_dialog.update_progress)
        update_worker.finished.connect(on_finished)
        update_worker.error.connect(on_error)

        update_worker.start()
        progress_dialog.exec_() # Muestra el diálogo de progreso y espera

        # Como la app se cierra si la actualización es exitosa, 
        # si llegamos aquí, es porque algo falló o el usuario canceló.
        return False # No continuar con la app normal

    return True # Continuar con la app normal

def load_config():
    """Carga la configuración desde el archivo JSON"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración '{CONFIG_FILE}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: El archivo de configuración '{CONFIG_FILE}' no es un JSON válido")
        return None

def main():
    """Función principal de la aplicación"""
    
    # Crear aplicación PyQt5 primero para poder mostrar diálogos
    app = QApplication(sys.argv)
    
    # Comprobar actualizaciones
    updater = Updater()
    latest_release = updater.check_for_updates()
    
    if latest_release:
        if not handle_update(latest_release):
             # Si handle_update devuelve False, significa que la actualización falló
             # o está en proceso, por lo que no debemos continuar.
             # Si la actualización fue exitosa, la app ya se habría cerrado.
             sys.exit(0)


    # Cargar configuración
    config = load_config()
    if not config:
        sys.exit(1) # Salir si no se puede cargar la configuración

    app.setStyle('Fusion')
    
    # Configurar atributos de la aplicación
    app.setApplicationName("MT5 Trading Journal")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("MT5 Trading Journal Team")
    
    # Crear y mostrar ventana principal
    window = MT5TrackerApp(config)
    window.show()
    
    # Ejecutar bucle principal
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
