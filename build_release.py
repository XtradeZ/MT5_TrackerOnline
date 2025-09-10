#!/usr/bin/env python3
"""
Script para crear el ejecutable final de MT5 Tracker
"""

import subprocess
import sys
import os
import shutil

def main():
    print("🚀 Creando ejecutable final de MT5 Tracker...")
    
    # Limpiar archivos anteriores
    if os.path.exists("dist"):
        print("🧹 Limpiando archivos anteriores...")
        shutil.rmtree("dist")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Comando de PyInstaller para el ejecutable final
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=installer',
        '--onefile',
        '--windowed',  # Sin consola
        '--add-data=assets;assets',
        '--add-data=config_simple.json;.',  # Incluir config en el ejecutable
        '--icon=assets/images/Logo.png',
        '--clean',
        'main.py'
    ]
    
    print("📦 Ejecutando PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ ¡Ejecutable creado exitosamente!")
        print("📁 El archivo se encuentra en: dist/installer.exe")
        
        # Verificar que el archivo se creó
        if os.path.exists("dist/installer.exe"):
            size = os.path.getsize("dist/installer.exe")
            print(f"📊 Tamaño del ejecutable: {size // (1024*1024)} MB")
        
        # Copiar archivos necesarios
        print("📋 Copiando archivos adicionales...")
        if os.path.exists("config_simple.json"):
            shutil.copy2("config_simple.json", "dist/")
            print("✅ config_simple.json copiado")
        
        # Generar checksums.txt
        print("🔐 Generando checksums...")
        result = subprocess.run([
            'powershell', '-Command', 
            'Get-FileHash -Algorithm SHA256 "dist/installer.exe" | Select-Object -ExpandProperty Hash'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            hash_value = result.stdout.strip()
            with open("dist/checksums.txt", "w") as f:
                f.write(f"{hash_value}  installer.exe\n")
            print("✅ checksums.txt generado")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear el ejecutable: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Listo! Tu aplicación MT5 Tracker está empaquetada y lista para distribuir.")
    else:
        print("\n❌ Hubo un error durante el empaquetado.")
