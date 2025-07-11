#!/usr/bin/env python3
"""
Cliente SFTP simplificado para debug
"""

import paramiko
import os
import sys
from pathlib import Path

def test_connection():
    """Test básico de conexión SSH"""
    print("🔍 Testing SSH connection...")
    
    # Configuración
    hostname = 'localhost'
    port = 2222
    username = 'drywall_user'
    key_path = 'keys/drywall_key'
    
    try:
        # Verificar clave
        if not os.path.exists(key_path):
            print(f"❌ Clave no encontrada: {key_path}")
            return False
        
        print(f"✅ Clave encontrada: {key_path}")
        
        # Cargar clave
        try:
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            print("✅ Clave cargada correctamente")
        except Exception as e:
            print(f"❌ Error cargando clave: {e}")
            return False
        
        # Crear cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"🔗 Conectando a {hostname}:{port}...")
        
        # Conectar con timeout corto
        ssh_client.connect(
            hostname=hostname,
            port=port,
            username=username,
            pkey=private_key,
            timeout=10,  # Timeout corto para debug
            banner_timeout=10,
            auth_timeout=10
        )
        
        print("✅ Conexión SSH exitosa")
        
        # Test básico SFTP
        sftp = ssh_client.open_sftp()
        print("✅ Canal SFTP abierto")
        
        # Listar directorio
        try:
            files = sftp.listdir('/upload')
            print(f"✅ Directorio /upload tiene {len(files)} archivos")
        except:
            print("⚠️ Directorio /upload no existe o está vacío")
        
        # Cerrar
        sftp.close()
        ssh_client.close()
        print("✅ Conexión cerrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
