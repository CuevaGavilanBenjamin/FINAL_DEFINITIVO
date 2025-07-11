#!/usr/bin/env python3
"""
Test SFTP Server - Servidor SFTP simplificado para debugging
"""

import paramiko
import threading
import socket
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Generar host key
HOST_KEY = paramiko.RSAKey.generate(2048)

# Configuración
UPLOAD_DIR = Path("upload")
UPLOAD_DIR.mkdir(exist_ok=True)
AUTH_KEY_PATH = Path("authorized_keys/client.pub")

class TestSFTPHandle(paramiko.SFTPHandle):
    def stat(self):
        try:
            return paramiko.SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError:
            return paramiko.SFTP_FAILURE

    def chattr(self, attr):
        return paramiko.SFTP_OK

class TestSFTPServer(paramiko.SFTPServerInterface):
    ROOT = UPLOAD_DIR

    def _realpath(self, path):
        return self.ROOT / os.path.basename(path)

    def list_folder(self, path):
        path = self._realpath(path)
        try:
            out = []
            if path.exists():
                for fname in path.iterdir():
                    attr = paramiko.SFTPAttributes.from_stat(fname.stat())
                    attr.filename = fname.name
                    out.append(attr)
            return out
        except OSError:
            return paramiko.SFTP_FAILURE

    def stat(self, path):
        path = self._realpath(path)
        try:
            return paramiko.SFTPAttributes.from_stat(path.stat())
        except OSError:
            return paramiko.SFTP_FAILURE

    def lstat(self, path):
        path = self._realpath(path)
        try:
            return paramiko.SFTPAttributes.from_stat(path.lstat())
        except OSError:
            return paramiko.SFTP_FAILURE

    def open(self, path, flags, attr):
        path = self._realpath(path)
        try:
            binary_flag = getattr(os, 'O_BINARY', 0)
            flags |= binary_flag
            mode = getattr(attr, 'st_mode', None)
            if mode is not None:
                fd = os.open(path, flags, mode)
            else:
                fd = os.open(path, flags, 0o666)
        except OSError as e:
            logger.error(f"Error opening file {path}: {e}")
            return paramiko.SFTP_FAILURE
        
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            paramiko.SFTPServer.set_file_attr(path, attr)
        
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                fstr = 'ab'
            else:
                fstr = 'wb'
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                fstr = 'a+b'
            else:
                fstr = 'r+b'
        else:
            fstr = 'rb'
        
        try:
            f = os.fdopen(fd, fstr)
        except OSError:
            return paramiko.SFTP_FAILURE
        
        fobj = TestSFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        
        logger.info(f"File uploaded: {path.name}")
        return fobj

    def remove(self, path):
        path = self._realpath(path)
        try:
            path.unlink()
        except OSError:
            return paramiko.SFTP_FAILURE
        return paramiko.SFTP_OK

    def rename(self, oldpath, newpath):
        oldpath = self._realpath(oldpath)
        newpath = self._realpath(newpath)
        try:
            oldpath.rename(newpath)
        except OSError:
            return paramiko.SFTP_FAILURE
        return paramiko.SFTP_OK

    def mkdir(self, path, attr):
        path = self._realpath(path)
        try:
            path.mkdir()
            if attr is not None:
                paramiko.SFTPServer.set_file_attr(path, attr)
        except OSError:
            return paramiko.SFTP_FAILURE
        return paramiko.SFTP_OK

    def rmdir(self, path):
        path = self._realpath(path)
        try:
            path.rmdir()
        except OSError:
            return paramiko.SFTP_FAILURE
        return paramiko.SFTP_OK

class TestSSHServer(paramiko.ServerInterface):
    def check_auth_publickey(self, username, key):
        if username != 'drywall_user':
            return paramiko.AUTH_FAILED
        
        try:
            with open(AUTH_KEY_PATH, 'r') as f:
                auth_key_data = f.read().strip()
            
            # Parsear la clave autorizada
            key_parts = auth_key_data.split()
            if len(key_parts) >= 2:
                key_type = key_parts[0]
                key_data = key_parts[1]
                
                if key_type == 'ssh-rsa':
                    import base64
                    auth_key = paramiko.RSAKey(data=base64.b64decode(key_data))
                    if key.get_base64() == auth_key.get_base64():
                        logger.info(f"Authentication successful for {username}")
                        return paramiko.AUTH_SUCCESSFUL
        except Exception as e:
            logger.error(f"Auth error: {e}")
        
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_client(client_socket, addr):
    try:
        logger.info(f"Connection from {addr}")
        
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        
        server = TestSSHServer()
        transport.set_server(server)
        
        # Start SSH server
        transport.start_server()
        
        # Wait for authentication
        channel = transport.accept(timeout=60)
        if channel is None:
            logger.error("No channel established")
            return
        
        # Start SFTP subsystem
        sftp_server = paramiko.SFTPServer(channel, TestSFTPServer)
        
        # Keep connection alive
        while transport.is_active():
            if not channel.active:
                break
            channel.recv(1024)
            
    except Exception as e:
        logger.error(f"Error handling client {addr}: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass

def start_sftp_server(port=2222):
    logger.info(f"Starting SFTP server on port {port}")
    
    # Verificar que existe la clave autorizada
    if not AUTH_KEY_PATH.exists():
        logger.error(f"Authorized key not found: {AUTH_KEY_PATH}")
        return
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        logger.info(f"SFTP server listening on port {port}")
        
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, addr)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        logger.info("Shutting down SFTP server")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_sftp_server()
