import pandas as pd
from dbmanager import *
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QComboBox, QVBoxLayout, 
                             QWidget, QLineEdit, QLabel, QMessageBox, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout)
from datetime import datetime
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

        # Botão 3 de ver relatorio
        btn_relatorio = QPushButton("Ver Relatório do Dia")
        btn_relatorio.clicked.connect(self.abrir_tela_relatorio)

        #adiciona os botões a tela principal
        layout.addWidget(btn_func)
        layout.addWidget(btn_ref)
        layout.addWidget(btn_relatorio)

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

    def abrir_tela_relatorio(self):
        self.janela_rel = tela_relatorio()
        self.janela_rel.show()

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

class tela_relatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relatório Diário")
        self.resize(600, 400) # Janela mais larga para caber a tabela
        self.banco = dbmanager(DATABASE_URL)
        self.lista_atual = [] # <--- Variável para guardar os dados da busca

        layout = QVBoxLayout()

        # --- ÁREA DE BUSCA ---
        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText("Digite a data (ex: 15/01/2026)")
        layout.addWidget(self.input_data)

        btn_buscar = QPushButton("Buscar Refeições")
        btn_buscar.clicked.connect(self.buscar_dados)
        layout.addWidget(btn_buscar)

        # --- ÁREA DE RESUMO (Labels lado a lado) ---
        layout_resumo = QHBoxLayout() # Horizontal
        
        self.lbl_cafe = QLabel("☕ Cafés: 0")
        self.lbl_almoco = QLabel("🍛 Almoços: 0")
        self.lbl_jantar = QLabel("🍲 Jantares: 0")
        
        # Deixando o texto negrito e maior
        estilo = "font-size: 14px; font-weight: bold; color: #333;"
        self.lbl_cafe.setStyleSheet(estilo)
        self.lbl_almoco.setStyleSheet(estilo)
        self.lbl_jantar.setStyleSheet(estilo)

        layout_resumo.addWidget(self.lbl_cafe)
        layout_resumo.addWidget(self.lbl_almoco)
        layout_resumo.addWidget(self.lbl_jantar)
        layout.addLayout(layout_resumo)

        # --- TABELA ---
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Hora", "Nome", "Cargo", "Refeição"])
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela)

        # --- BOTÃO EXPORTAR (NOVO) ---
        btn_exportar = QPushButton("📥 Exportar para Excel")
        btn_exportar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        btn_exportar.clicked.connect(self.gerar_excel) # Conecta na função nova
        layout.addWidget(btn_exportar)

        self.setLayout(layout)

    def buscar_dados(self):
        data_texto = self.input_data.text()
        
        if not data_texto:
            QMessageBox.warning(self, "Atenção", "Digite uma data!")
            return

        # 1. Busca no Banco
        self.lista_atual = self.banco.quant_refei_detl(data_texto)
        lista_refeicoes = self.lista_atual
        
        # Se a lista vier vazia
        if not lista_refeicoes:
            QMessageBox.information(self, "Info", "Nenhuma refeição encontrada neste dia.")
            self.limpar_tudo()
            return

        # 2. Faz a Contagem (Resumo)
        qtd_cafe = 0
        qtd_almoco = 0
        qtd_jantar = 0

        # Limpa a tabela antes de preencher
        self.tabela.setRowCount(0)

        # 3. Preenche a Tabela e Conta
        for linha, ref in enumerate(lista_refeicoes):
            # Contagem
            if ref.tipo == "Café da manhã": qtd_cafe += 1
            elif ref.tipo == "Almoço": qtd_almoco += 1
            elif ref.tipo == "Jantar": qtd_jantar += 1

            # Adiciona linha na tabela
            self.tabela.insertRow(linha)
            
            # Formata hora
            hora = ref.data.strftime("%H:%M")
            
            # Pega dados (Graças ao joinedload isso não vai travar!)
            nome = ref.funcionario.nome
            cargo = ref.funcionario.cargo
            tipo = ref.tipo

            # Coloca nas células (Linha, Coluna, Item)
            self.tabela.setItem(linha, 0, QTableWidgetItem(hora))
            self.tabela.setItem(linha, 1, QTableWidgetItem(nome))
            self.tabela.setItem(linha, 2, QTableWidgetItem(cargo))
            self.tabela.setItem(linha, 3, QTableWidgetItem(tipo))

        # 4. Atualiza os Labels do topo
        self.lbl_cafe.setText(f"☕ Cafés: {qtd_cafe}")
        self.lbl_almoco.setText(f"🍛 Almoços: {qtd_almoco}")
        self.lbl_jantar.setText(f"🍲 Jantares: {qtd_jantar}")

    def limpar_tudo(self):
        self.tabela.setRowCount(0)
        self.lista_atual = []
        self.lbl_cafe.setText("☕ Cafés: 0")
        self.lbl_almoco.setText("🍛 Almoços: 0")
        self.lbl_jantar.setText("🍲 Jantares: 0")

    def gerar_excel(self):
        if not self.lista_atual:
            QMessageBox.warning(self, "Erro", "Faça uma busca primeiro para ter dados para exportar.")
            return

        try:
            # 1. Abre janela para escolher onde salvar
            caminho_arquivo, _ = QFileDialog.getSaveFileName(
                self, 
                "Salvar Relatório", 
                "relatorio_refeicoes.xlsx", 
                "Arquivos Excel (*.xlsx)"
            )

            if caminho_arquivo:
                # 2. Transforma os dados do banco em um formato que o Pandas entende (Lista de Dicionários)
                dados_para_excel = []
                for ref in self.lista_atual:
                    dados_para_excel.append({
                        "Data": ref.data.strftime("%d/%m/%Y"),
                        "Hora": ref.data.strftime("%H:%M"),
                        "Nome do Funcionário": ref.funcionario.nome,
                        "CPF": ref.funcionario_cpf,
                        "Empresa": ref.funcionario.empresa,
                        "Cargo": ref.funcionario.cargo,
                        "Refeição": ref.tipo
                    })

                # 3. Cria o DataFrame e Salva
                df = pd.DataFrame(dados_para_excel)
                df.to_excel(caminho_arquivo, index=False) # index=False tira a coluna de numeração 0,1,2...

                QMessageBox.information(self, "Sucesso", "Relatório exportado com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar Excel: {e}")

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