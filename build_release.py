#!/usr/bin/env python3
"""
Script para crear el sistema completo de MT5 Tracker con auto-actualización
Genera:
- installer.exe (aplicación principal)
- updater.exe (programa de actualización independiente)
- update.zip (paquete de distribución)
- checksums.txt (validación de seguridad)
"""

import subprocess
import sys
import os
import shutil
import zipfile
import hashlib
import json
from pathlib import Path

def build_main_app():
    """Construye la aplicación principal"""
    print("📦 Construyendo aplicación principal...")
    
    # Usar el Python del virtual environment si existe
    python_exe = Path("venv/Scripts/python.exe")
    if python_exe.exists():
        python_cmd = str(python_exe)
        print("🐍 Usando Python del virtual environment")
    else:
        python_cmd = sys.executable
        print("🐍 Usando Python del sistema")
    
    cmd = [
        python_cmd, '-m', 'PyInstaller',
        '--name=installer',
        '--onefile',
        '--windowed',  # Sin consola para la app principal
        '--add-data=assets;assets',
        '--add-data=config_simple.json;.',
        '--hidden-import=requests',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        '--hidden-import=charset_normalizer',
        '--hidden-import=mt5_tracker.updater',
        '--hidden-import=mt5_tracker.app',
        '--hidden-import=mt5_tracker.ui',
        '--hidden-import=mt5_tracker.tracker',
        '--hidden-import=mt5_tracker.connector',
        '--hidden-import=mt5_tracker.file_manager',
        '--hidden-import=mt5_tracker.comments_manager',
        '--clean',
        'main.py'
    ]
    
    # Añadir ícono solo si existe y tenemos Pillow
    try:
        import PIL
        icon_path = Path("assets/images/Logo.png")
        if icon_path.exists():
            cmd.insert(-1, f'--icon={icon_path}')
    except ImportError:
        print("⚠️ Pillow no disponible, construyendo sin ícono")
    
    print(f"🔧 Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True)
    print("✅ installer.exe creado")

def build_updater():
    """Construye el updater independiente"""
    print("📦 Construyendo updater independiente...")
    
    # Usar el mismo Python que para la app principal
    python_exe = Path("venv/Scripts/python.exe")
    python_cmd = str(python_exe) if python_exe.exists() else sys.executable
    
    cmd = [
        python_cmd, '-m', 'PyInstaller',
        '--name=updater',
        '--onefile',
        '--console',  # Con consola para mostrar progreso
        '--hidden-import=psutil',
        '--clean',
        'updater_standalone.py'
    ]
    
    # Añadir ícono solo si existe y tenemos Pillow
    try:
        import PIL
        icon_path = Path("assets/images/Logo.png")
        if icon_path.exists():
            cmd.insert(-1, f'--icon={icon_path}')
    except ImportError:
        pass
    
    print(f"🔧 Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True)
    print("✅ updater.exe creado")

def create_update_package():
    """Crea el paquete .zip para distribución"""
    print("📦 Creando paquete de actualización...")
    
    zip_path = Path("dist/update.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Añadir archivos principales
        zipf.write("dist/installer.exe", "installer.exe")
        zipf.write("dist/updater.exe", "updater.exe")
        zipf.write("config_simple.json", "config_simple.json")
        
        # Añadir carpeta assets
        for asset_file in Path("assets").rglob("*"):
            if asset_file.is_file():
                arcname = str(asset_file)
                zipf.write(asset_file, arcname)
    
    print(f"✅ Paquete creado: {zip_path}")
    return zip_path

def generate_checksums(zip_path):
    """Genera checksums para el paquete"""
    print("🔐 Generando checksums...")
    
    # Calcular hash del ZIP
    with open(zip_path, 'rb') as f:
        zip_hash = hashlib.sha256(f.read()).hexdigest().upper()
    
    # Crear checksums.txt
    checksums_path = Path("dist/checksums.txt")
    with open(checksums_path, 'w') as f:
        f.write(f"{zip_hash}  update.zip\n")
    
    print(f"✅ Checksum generado: {zip_hash[:16]}...")
    return checksums_path

def create_update_json(version):
    """Crea el archivo update.json para GitHub"""
    update_info = {
        "version": version,
        "url": f"https://github.com/XtradeZ/MT5_TrackerOnline/releases/download/v{version}/update.zip",
        "checksum_url": f"https://github.com/XtradeZ/MT5_TrackerOnline/releases/download/v{version}/checksums.txt",
        "release_notes": f"Actualización a la versión {version}",
        "required": False
    }
    
    update_json_path = Path("dist/update.json")
    with open(update_json_path, 'w', encoding='utf-8') as f:
        json.dump(update_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ update.json creado para versión {version}")
    return update_json_path

def cleanup_previous_builds():
    """Limpia construcciones previas de forma segura"""
    print("🧹 Limpiando archivos anteriores...")
    
    # Matar procesos que puedan estar bloqueando archivos
    try:
        subprocess.run(['taskkill', '/f', '/im', 'installer.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/f', '/im', 'updater.exe'], 
                      capture_output=True, check=False)
    except:
        pass
    
    # Eliminar archivos específicos primero
    for path in ["dist", "build"]:
        if os.path.exists(path):
            try:
                # Intentar eliminar archivos individuales primero
                if os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
            except Exception as e:
                print(f"⚠️ Advertencia: No se pudo limpiar {path}: {e}")
    
    # Eliminar archivos .spec
    for spec_file in Path(".").glob("*.spec"):
        try:
            spec_file.unlink()
        except:
            pass

def main():
    print("🚀 Construyendo sistema completo de MT5 Tracker...")
    print("=" * 60)
    
    # Obtener la versión actual del código
    sys.path.insert(0, str(Path(__file__).parent))
    from mt5_tracker.updater import APP_VERSION
    sys.path.pop(0)
    
    print(f"🏷️ Construyendo versión: {APP_VERSION}")
    
    # Limpiar archivos anteriores de forma segura
    cleanup_previous_builds()
    
    os.makedirs("dist", exist_ok=True)
    
    try:
        # Paso 1: Construir aplicación principal
        build_main_app()
        
        # Paso 2: Construir updater
        build_updater()
        
        # Paso 3: Copiar archivos necesarios
        print("📋 Copiando archivos adicionales...")
        shutil.copy2("config_simple.json", "dist/")
        
        # Paso 4: Crear paquete ZIP
        zip_path = create_update_package()
        
        # Paso 5: Generar checksums
        checksums_path = generate_checksums(zip_path)
        
        # Paso 6: Crear update.json
        update_json_path = create_update_json(APP_VERSION)
        
        # Resumen final
        print("\n" + "=" * 60)
        print("🎉 ¡SISTEMA COMPLETO GENERADO!")
        print("=" * 60)
        print("📁 PARA DISTRIBUCIÓN INICIAL (dar a nuevos usuarios):")
        initial_files = ["installer.exe", "updater.exe", "config_simple.json"]
        for filename in initial_files:
            file_path = Path("dist") / filename
            if file_path.exists():
                size = file_path.stat().st_size
                size_str = f"{size // (1024*1024)} MB" if size > 1024*1024 else f"{size // 1024} KB"
                print(f"   - {filename} ({size_str})")
        
        print("\n📦 PARA GITHUB RELEASES (actualizaciones automáticas):")
        release_files = ["update.zip", "checksums.txt", "update.json"]
        for filename in release_files:
            file_path = Path("dist") / filename
            if file_path.exists():
                size = file_path.stat().st_size
                size_str = f"{size // (1024*1024)} MB" if size > 1024*1024 else f"{size // 1024} KB"
                print(f"   - {filename} ({size_str})")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la construcción: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Listo! Tu aplicación MT5 Tracker está empaquetada y lista para distribuir.")
    else:
        print("\n❌ Hubo un error durante el empaquetado.")
