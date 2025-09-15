#!/usr/bin/env python3
"""
MT5 Tracker - Updater Standalone
Programa independiente que maneja las actualizaciones automáticas.
"""

import sys
import os
import time
import zipfile
import shutil
import subprocess
import json
from pathlib import Path

def log(message):
    """Log con timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def wait_for_process_end(process_name, timeout=30):
    """Espera a que un proceso termine"""
    log(f"Esperando a que termine {process_name}...")
    
    import psutil
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        found = False
        for proc in psutil.process_iter(['name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found:
            log(f"✅ {process_name} terminado")
            return True
            
        time.sleep(1)
    
    log(f"⚠️ Timeout esperando que termine {process_name}")
    return False

def backup_installation(install_dir):
    """Crear backup de la instalación actual"""
    backup_dir = install_dir / "backup"
    
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir()
    
    # Hacer backup de archivos críticos
    critical_files = ["installer.exe", "config_simple.json"]
    
    for filename in critical_files:
        src_file = install_dir / filename
        if src_file.exists():
            shutil.copy2(src_file, backup_dir / filename)
            log(f"📋 Backup creado: {filename}")

def restore_backup(install_dir):
    """Restaurar backup en caso de error"""
    backup_dir = install_dir / "backup"
    
    if not backup_dir.exists():
        log("❌ No hay backup disponible")
        return False
    
    log("🔄 Restaurando backup...")
    
    for backup_file in backup_dir.iterdir():
        if backup_file.is_file():
            target_file = install_dir / backup_file.name
            shutil.copy2(backup_file, target_file)
            log(f"📋 Restaurado: {backup_file.name}")
    
    return True

def extract_update(zip_path, install_dir):
    """Extraer archivos de actualización"""
    log(f"📦 Extrayendo {zip_path}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Listar archivos que se van a extraer
            file_list = zip_ref.namelist()
            log(f"📁 Archivos a extraer: {len(file_list)}")
            
            for file_info in zip_ref.infolist():
                log(f"   - {file_info.filename}")
            
            # Extraer archivos excluyendo updater.exe para evitar conflictos
            for file_info in zip_ref.infolist():
                if file_info.filename != "updater.exe":  # No reemplazar el updater que está ejecutándose
                    zip_ref.extract(file_info, install_dir)
                    log(f"✅ Extraído: {file_info.filename}")
                else:
                    log(f"⏭️ Omitido: {file_info.filename} (en uso)")
            
        log("✅ Extracción completada")
        return True
        
    except Exception as e:
        log(f"❌ Error al extraer: {e}")
        return False

def cleanup_temp_files(install_dir):
    """Limpiar archivos temporales"""
    temp_files = [
        "update.zip",
        "checksums.txt.new",
        "backup"
    ]
    
    for temp_file in temp_files:
        temp_path = install_dir / temp_file
        try:
            if temp_path.exists():
                if temp_path.is_dir():
                    shutil.rmtree(temp_path)
                else:
                    temp_path.unlink()
                log(f"🧹 Eliminado: {temp_file}")
        except Exception as e:
            log(f"⚠️ No se pudo eliminar {temp_file}: {e}")

def restart_application(install_dir):
    """Reiniciar la aplicación principal"""
    app_exe = install_dir / "installer.exe"
    
    if not app_exe.exists():
        log("❌ No se encontró installer.exe")
        return False
    
    log("🚀 Reiniciando aplicación...")
    
    try:
        # Usar subprocess.Popen para no bloquear
        subprocess.Popen([str(app_exe)], cwd=str(install_dir))
        log("✅ Aplicación reiniciada")
        return True
    except Exception as e:
        log(f"❌ Error al reiniciar: {e}")
        return False

def main():
    """Función principal del updater"""
    print("=" * 60)
    print("🔄 MT5 Tracker - Updater")
    print("=" * 60)
    
    if len(sys.argv) != 3:
        log("❌ Uso: updater.exe <zip_path> <install_dir>")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    zip_path = Path(sys.argv[1])
    install_dir = Path(sys.argv[2])
    
    log(f"📦 Archivo de actualización: {zip_path}")
    log(f"📁 Directorio de instalación: {install_dir}")
    
    # Verificar que los archivos existen
    if not zip_path.exists():
        log(f"❌ No se encontró el archivo: {zip_path}")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    if not install_dir.exists():
        log(f"❌ No se encontró el directorio: {install_dir}")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    # Paso 1: Esperar a que termine la aplicación principal
    wait_for_process_end("installer.exe")
    
    # Paso 2: Crear backup
    backup_installation(install_dir)
    
    # Paso 3: Extraer actualización
    success = extract_update(zip_path, install_dir)
    
    if success:
        log("✅ Actualización completada exitosamente")
        
        # Paso 4: Limpiar archivos temporales
        cleanup_temp_files(install_dir)
        
        # Paso 5: Reiniciar aplicación
        restart_application(install_dir)
        
    else:
        log("❌ Error durante la actualización")
        
        # Restaurar backup
        if restore_backup(install_dir):
            log("✅ Backup restaurado")
            restart_application(install_dir)
        else:
            log("❌ No se pudo restaurar el backup")
            input("Presiona Enter para salir...")
            sys.exit(1)
    
    log("🎉 Proceso de actualización terminado")
    
    # Esperar un poco antes de cerrar
    time.sleep(2)

if __name__ == "__main__":
    main()

