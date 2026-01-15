from dbmanager import *
from PyQt6.QtWidgets import QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget,QLineEdit, QLabel, QMessageBox
from werkzeug.security import check_password_hash # <--- Importe isso

from config import DATABASE_URL

#abre a janela principal que guarda os 2 botões. o de ir inserir um funcionario e o de inserir uma refeição
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sistema Empresa")
        self.resize(300, 200)

        layout = QVBoxLayout()
        
        # Botão 1 de inserir funcionario
        btn_func = QPushButton("Registrar Funcionários")
        btn_func.clicked.connect(self.abrir_tela_funcionario)
        
        # Botão 2 de inserir refeicao
        btn_ref = QPushButton("Registrar Refeição")
        btn_ref.clicked.connect(self.abrir_tela_refeicao)

        #adiciona os botões a tela principal
        layout.addWidget(btn_func)
        layout.addWidget(btn_ref)

        #define um container e inseri o layout nele
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def abrir_tela_funcionario(self):
        self.janela_func = tela_funcionario() # Cria a janela
        self.janela_func.show() # Mostra a janela

    def abrir_tela_refeicao(self):
        self.janela_ref = tela_refeicao() # Cria a janela
        self.janela_ref.show() # Mostra a janela

#janela de erro
class ErrorWindow():    
    @staticmethod
    def exibir_erro(mensagem):  # Adicionamos o parâmetro 'mensagem'
        msg = QMessageBox()
        msg.setWindowTitle("Erro")
        msg.setText(mensagem)   # O texto agora é dinâmico
        msg.exec()

#janela de notificação
class NotiificationWindow():    
    @staticmethod
    def exibir_notificacao(mensagem):  # Adicionamos o parâmetro 'mensagem'
        msg = QMessageBox()
        msg.setWindowTitle("Notificação")
        msg.setText(mensagem)   # O texto agora é dinâmico
        msg.exec()

#constroi as janelas de inserir funcionario e recebe os inputs
class tela_funcionario(QWidget):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("inserir funcionario")
        self.banco = dbmanager(DATABASE_URL)

        # Layout e Widgets
        layout = QVBoxLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome")
        layout.addWidget(self.input_nome)

        # Inputs necessários (simulando que você tem eles)
        self.input_cpffunc = QLineEdit()
        self.input_cpffunc.setPlaceholderText("CPF")
        layout.addWidget(self.input_cpffunc)

        self.input_senhafunc = QLineEdit()
        self.input_senhafunc.setPlaceholderText("Senha")
        layout.addWidget(self.input_senhafunc)

        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Empresa")
        layout.addWidget(self.input_empresa)

        self.input_cargo = QLineEdit()
        self.input_cargo.setPlaceholderText("Cargo")
        layout.addWidget(self.input_cargo)

        button = QPushButton("Registrar")
        button.clicked.connect(self.criarfuncionario)
        layout.addWidget(button)

        self.setLayout(layout)

    #inseri os dados pegos pela a janela
    def criarfuncionario(self):

        nome = self.input_nome.text()
        cpf = self.input_cpffunc.text()
        senha = self.input_senhafunc.text() 
        cargo = self.input_cargo.text()
        empresa = self.input_empresa.text()

        if nome and cpf and senha and cargo and empresa:

            if self.banco.inserirfuncionario(cpf,nome,empresa,cargo,senha):

                notf = NotiificationWindow()
                notf.exibir_notificacao("funcionario inserido com sucesso")

            else:

                err = ErrorWindow()
                err.exibir_erro("algo deu errado")


        else:

            err = ErrorWindow()
    
            err.exibir_erro("dados insulficiente")

            print("erro dados insulficientes")

class tela_refeicao(QWidget):
    def __init__(self):

        super().__init__()
        self.banco = dbmanager(DATABASE_URL)
        self.setWindowTitle("Refeição")

        # Layout e Widgets
        layout = QVBoxLayout()

        # Inputs necessários (simulando que você tem eles)
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("CPF")
        layout.addWidget(self.input_cpf)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        layout.addWidget(self.input_senha)

        self.combo = QComboBox()
        self.combo.addItems(["Café da manhã", "Almoço", "Jantar"])
        layout.addWidget(self.combo)

        button = QPushButton("Registrar")
        button.clicked.connect(self.botaorefeicao)
        layout.addWidget(button)

        self.setLayout(layout)

    def botaorefeicao(self):
        cpf_digitado = self.input_cpf.text()
        senha_digitada = self.input_senha.text()
        tipo_escolhido = self.combo.currentText()

        if cpf_digitado and senha_digitada and tipo_escolhido:
            
            # 1. Busca o usuário no banco primeiro
            usuario = self.banco.get_colaborador_by_cpf(cpf_digitado)

            # 2. Verifica se usuário existe E se a senha bate com o Hash
            if usuario and check_password_hash(usuario.senha, senha_digitada):
                
                # 3. Se deu certo, registra a refeição (sem passar a senha)
                sucesso = self.banco.refeicao(cpf_digitado, tipo_escolhido)
                
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Refeição registrada!")
                    self.close() # Fecha a janela ou limpa os campos
                else:
                    err = ErrorWindow()
                    err.exibir_erro("Erro ao gravar no banco")
            else:
                err = ErrorWindow()
                err.exibir_erro("Senha incorreta ou CPF não encontrado")

        else:
            err = ErrorWindow()
            err.exibir_erro("Preencha todos os campos")