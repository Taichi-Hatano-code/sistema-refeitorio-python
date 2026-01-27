import sys
import os
import webbrowser
import socket
import threading
from time import sleep

# Importa Flask e Waitress
from waitress import serve
from web_site import app  # Certifique-se que o arquivo se chama web_site.py

# Importa PyQt
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
    # Roda o site na porta 8080 liberado para a rede
    serve(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Configuração de pastas (importante para o .exe ou Linux)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        app.template_folder = os.path.join(base_dir, 'templates')
        app.static_folder = os.path.join(base_dir, 'static')
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Mostra IPs no terminal
    meu_ip = get_ip()
    print("="*40)
    print(f" SISTEMA INICIADO")
    print(f" > Acesso Local: http://localhost:8080")
    print(f" > Acesso Celular: http://{meu_ip}:8080")
    print("="*40)

    # 1. Inicia o Servidor (Flask) em segundo plano
    t = threading.Thread(target=rodar_servidor)
    t.daemon = True
    t.start()

    # 2. Inicia a Interface Gráfica (Janela)
    app_qt = QApplication(sys.argv)
    window = janela.MainWindow()
    window.show()
    
    # Mantém o programa rodando até fechar a janela
    sys.exit(app_qt.exec())