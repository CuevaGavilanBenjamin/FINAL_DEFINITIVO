#!/usr/bin/env python3
"""
Cliente SFTP simple para subir archivos CSV
"""

import paramiko
import os
import sys
from datetime import datetime
from pathlib import Path

class SFTPClient:
    def __init__(self, hostname='localhost', port=2222, username='drywall_user', key_path='keys/drywall_key'):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_path = key_path
        self.ssh_client = None
        self.sftp_client = None
    
    def connect(self):
        """Conectar al servidor SFTP"""
        try:
            if not os.path.exists(self.key_path):
                print(f"ERROR: Clave no encontrada: {self.key_path}")
                return False
            
            print(f"Conectando a {self.hostname}:{self.port}")
            
            # Cargar clave privada
            private_key = paramiko.RSAKey.from_private_key_file(self.key_path)
            
            # Crear cliente SSH
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Conectar
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=private_key,
                timeout=15
            )
            
            # Crear cliente SFTP
            self.sftp_client = self.ssh_client.open_sftp()
            print("OK: Conexion exitosa")
            return True
            
        except Exception as e:
            print(f"ERROR: Error al conectar: {e}")
            return False
    
    def upload_file(self, local_file):
        """Subir archivo al servidor"""
        try:
            if not self.sftp_client:
                print("ERROR: No hay conexion SFTP")
                return False
            
            local_path = Path(local_file)
            if not local_path.exists():
                print(f"ERROR: Archivo no encontrado: {local_file}")
                return False
            
            # Nombre con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            remote_filename = f"{timestamp}_{local_path.name}"
            
            print(f"Subiendo: {local_file} -> {remote_filename}")
            
            # Subir archivo
            self.sftp_client.put(str(local_path), remote_filename)
            
            print("OK: Archivo subido exitosamente")
            return True
            
        except Exception as e:
            print(f"ERROR: Error al subir: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
            print("Conexion cerrada")
        except Exception as e:
            print(f"WARNING: Error al cerrar: {e}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python sftp_upload.py <archivo_csv>")
        return 1
    
    archivo = sys.argv[1]
    
    client = SFTPClient()
    
    if not client.connect():
        return 1
    
    try:
        if client.upload_file(archivo):
            print("SUCCESS: Subida completada!")
            return 0
        else:
            return 1
    finally:
        client.disconnect()

if __name__ == "__main__":
    sys.exit(main())
