import janela,sys,site
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

#inicia a janela
window = janela.MainWindow()

#mostra a janela
window.show()

sys.exit(app.exec())