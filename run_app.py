import sys
import os
import webbrowser
import socket
import threading
from time import sleep

# Importa o Flask e o Waitress
from waitress import serve
from site import app

# Importa o PyQt e a sua Janela
from PyQt6.QtWidgets import QApplication
import janela

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def rodar_servidor():
    """Função que fica rodando o site em background"""
    # O host='0.0.0.0' permite acesso pelo celular
    serve(app, host='0.0.0.0', port=8080)

def abrir_navegador():
    """Abre o navegador após 2 segundos"""
    sleep(2)
    webbrowser.open_new("http://localhost:8080")

if __name__ == '__main__':
    # 1. Configura pastas para funcionarem dentro do .exe (PyInstaller)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        # Ajusta pastas do Flask
        app.template_folder = os.path.join(base_dir, 'templates')
        app.static_folder = os.path.join(base_dir, 'static')
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Mostra informações no Console (A janela preta que abre atrás)
    meu_ip = get_ip()
    print("="*40)
    print(f" SISTEMA HÍBRIDO INICIADO")
    print(f" > App Desktop: Iniciando...")
    print(f" > Web Local: http://localhost:8080")
    print(f" > Web Celular: http://{meu_ip}:8080")
    print("="*40)

    # 3. Inicia o Servidor Web em uma THREAD (Fio paralelo)
    # daemon=True significa: