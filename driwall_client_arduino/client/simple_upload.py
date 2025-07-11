#!/usr/bin/env python3
"""
Generar datos y subirlos via SFTP
"""

import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Ejecutar comando y retornar si fue exitoso"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else str(e)

def main():
    print("DRYWALL - Generador y Subida SFTP")
    print("=" * 40)
    
    # Generar datos
    print("\nGenerando datos de humedad...")
    success, output = run_command(["python", "generate_humidity.py", "-n", "25", "--format", "csv"])
    
    if not success:
        print(f"ERROR generando datos: {output}")
        return 1
    
    # Extraer nombre del archivo
    filename = None
    for line in output.split('\n'):
        if '[FILE] Archivo:' in line:
            filename = line.split('Archivo: ')[1].strip()
            break
    
    if not filename:
        print("ERROR: No se pudo determinar el archivo generado")
        return 1
    
    print(f"OK: Archivo generado: {filename}")
    
    # Subir archivo
    print(f"\nSubiendo {filename}...")
    success, output = run_command(["python", "upload.py", filename])
    
    if not success:
        print(f"ERROR subiendo: {output}")
        return 1
    
    print("SUCCESS: Proceso completado!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
