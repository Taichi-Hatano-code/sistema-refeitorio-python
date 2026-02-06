from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

# Importa as configurações prontas
from config import DATABASE_URL, SECRET_KEY 
from dbmanager import *
from models import *

from datetime import datetime

app = Flask(__name__)

# Usa a variável importada
app.secret_key = SECRET_KEY 

# Usa a URL importada
db = dbmanager(DATABASE_URL)    

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'login' # Nome da função da rota de login (para redirecionar quem tentar entrar sem logar)@app.route('/')

@login_manager.user_loader
def load_user(user_id):
    # O Flask pega o ID do cookie e passa para essa função.
    # Usamos o método que criamos no passo 2 para devolver o objeto.
    return db.get_colaborador_by_cpf(user_id)

@app.route('/')
def home():
    from datetime import datetime
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    lista = db.quant_refei_detl(hoje)
    
    # Estrutura: {'NomeEmpresa': [Cafe, Almoco, Jantar]}
    dados_por_empresa = {}
    
    if lista:
        for ref in lista:
            # Pega o nome da empresa (ou "Sem Empresa" se der erro)
            nome_empresa = ref.funcionario.empresa if ref.funcionario else "Outros"
            
            # Se a empresa não existe no dicionário, cria ela zerada
            if nome_empresa not in dados_por_empresa:
                dados_por_empresa[nome_empresa] = [0, 0, 0] # [Cafe, Almoco, Jantar]
            
            # Soma na posição correta da lista
            if "Café" in ref.tipo:
                dados_por_empresa[nome_empresa][0] += 1
            elif "Almoço" in ref.tipo:
                dados_por_empresa[nome_empresa][1] += 1
            elif "Jantar" in ref.tipo:
                dados_por_empresa[nome_empresa][2] += 1
            
    # Enviamos esse dicionário complexo para o HTML
    return render_template('index.html', dados=dados_por_empresa)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, nem mostra a tela de login, manda pro painel
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        cpf = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_colaborador_by_cpf(cpf)
        
        if user and check_password_hash(user.senha, password):
            login_user(user)
            
            # --- AQUI ESTÁ O TRUQUE ---
            # O Flask envia um parâmetro chamado 'next' quando bloqueia alguém.
            # Ex: /login?next=/paineladm
            next_page = request.args.get('next')
            
            # Se existir um 'next', mandamos o usuário para lá.
            # Se não, mandamos para o dashboard padrão.
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required # <--- Protege a rota. Só logado entra.
def dashboard():
    return render_template('dashboard.html')

@app.route('/paineladm')
@login_required
def paineladm():
    if current_user.cargo.lower() != 'admin':
        flash('⛔ Acesso Negado!')
        return redirect(url_for('dashboard'))

    from datetime import datetime
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    lista = db.quant_refei_detl(hoje)
    
    # 1. Totais Gerais (Para os Cards no topo da tela)
    totais = {
        "Cafe": 0, "Cafe_Autorizado": 0,
        "Almoco": 0, "Almoco_Autorizado": 0,
        "Jantar": 0, "Jantar_Autorizado": 0
    }

    # 2. Dados para o Gráfico (Agrupado por Empresa)
    # Estrutura: {'Empresa A': [QtdCafe, QtdAlmoco, QtdJantar]}
    dados_grafico = {}

    if lista:
        for ref in lista:
            # --- Lógica dos Totais (Mantive a sua original) ---
            cargo = ref.funcionario.cargo.lower() if ref.funcionario else ""
            eh_admin = (cargo == 'admin')

            if "Café" in ref.tipo:
                if eh_admin: totais["Cafe_Autorizado"] += 1
                else: totais["Cafe"] += 1
            elif "Almoço" in ref.tipo:
                if eh_admin: totais["Almoco_Autorizado"] += 1
                else: totais["Almoco"] += 1
            elif "Jantar" in ref.tipo:
                if eh_admin: totais["Jantar_Autorizado"] += 1
                else: totais["Jantar"] += 1

            # --- NOVA Lógica para o Gráfico (Por Empresa) ---
            # Pega o nome da empresa do funcionário
            nome_empresa = ref.funcionario.empresa if ref.funcionario else "Outros"

            if nome_empresa not in dados_grafico:
                dados_grafico[nome_empresa] = [0, 0, 0] # [Cafe, Almoco, Jantar]

            if "Café" in ref.tipo: dados_grafico[nome_empresa][0] += 1
            elif "Almoço" in ref.tipo: dados_grafico[nome_empresa][1] += 1
            elif "Jantar" in ref.tipo: dados_grafico[nome_empresa][2] += 1

    # Passamos AMBOS para o template: 'dados' (cards) e 'grafico' (chart.js)
    return render_template('paineladm.html', dados=totais, grafico=dados_grafico)

@app.route('/registrar_refeicao', methods=['POST'])
@login_required
def registrar_refeicao():
    # Pega o valor do input hidden (Cafe, Almoco ou Jantar)
    tipo_escolhido = request.form.get('tipo_refeicao')
    hora_atual = datetime.now().hour
    hoje = datetime.now().date()

    # --- VALIDAÇÃO DE HORÁRIO (Seu código atual) ---
    horarios = {
        "Café": (5, 10),
        "Almoço": (11, 15),
        "Jantar": (18, 22)
    }

    if tipo_escolhido in horarios:
        inicio, fim = horarios[tipo_escolhido]
        if not (inicio <= hora_atual < fim):
            flash(f'❌ Horário inválido para {tipo_escolhido}!')
            return redirect(url_for('dashboard')) # Talvez não precise de logout aqui
    
    # --- NOVA VALIDAÇÃO: DUPLICIDADE ---
    # Verifica se já existe registro para esse CPF + TIPO + DATA
    ja_existe = db.verificar_duplicidade(current_user.cpf, tipo_escolhido)    
    
    if ja_existe:
        flash(f'⚠️ Você já registrou seu {tipo_escolhido} hoje!')
        return redirect(url_for('dashboard'))
    
    # Usa o seu dbmanager. 
    # Nota: Como o usuário já está logado, usamos os dados dele direto do current_user
    sucesso = db.refeicao(
        cpf2=current_user.cpf,
        tipo2=tipo_escolhido
    )
    
# 3. Define a mensagem que vai aparecer na tela de LOGIN
    if sucesso:
        flash(f'✅ Sucesso! {tipo_escolhido} registrado para {current_user.nome}.')
    else:
        flash('❌ Erro ao registrar refeição. Tente novamente.')

    # 4. (O PULO DO GATO) Desloga o usuário e manda pro Login
    logout_user()
    return redirect(url_for('login'))

@app.route('/registrar_refeicao_bulk', methods=['POST'])
@login_required
def registrar_refeicao_bulk():  # <--- Mudei o nome para não conflitar
    # 1. Pega os dados do formulário novo
    tipo_escolhido = request.form.get('tipo_refeicao')
    quantidade = request.form.get('quantidade') # Pega o número que digitamos
    
    # 2. Chama a função corrigida do dbmanager
    sucesso = db.refeicaoADM(
        cpf2=current_user.cpf,
        tipo2=tipo_escolhido,
        quant=quantidade # Passa a quantidade para o loop
    )
    
    # 3. Feedback
    if sucesso:
        flash(f'✅ Sucesso! {quantidade} refeições ({tipo_escolhido}) registradas.')
    else:
        flash('❌ Erro ao registrar em lote. Verifique o banco de dados.')

    # Mantém o admin no painel em vez de deslogar
    return redirect(url_for('paineladm'))
    
# 3. Define a mensagem que vai aparecer na tela de LOGIN
    if sucesso:
        flash(f'✅ Sucesso! {tipo_escolhido} registrado para {current_user.nome}.')
    else:
        flash('❌ Erro ao registrar refeição. Tente novamente.')

    # 4. (O PULO DO GATO) Desloga o usuário e manda pro Login
    logout_user()
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user() # Limpa o cookie
    return redirect(url_for('home'))

if __name__ == "__main__":
    # host='0.0.0.0' libera o acesso para a rede
    # port=5000 é a porta padrão (você pode mudar se quiser)
    app.run(host='0.0.0.0', port=5000, debug=True)