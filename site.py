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
    # 1. Lógica para contar as refeições de HOJE
    from datetime import datetime
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    lista = db.quant_refei_detl(hoje)
    
    totais = {"Cafe": 0, "Almoco": 0, "Jantar": 0}
    
    if lista:
        for ref in lista:
            if "Café" in ref.tipo: totais["Cafe"] += 1
            elif "Almoço" in ref.tipo: totais["Almoco"] += 1
            elif "Jantar" in ref.tipo: totais["Jantar"] += 1
            
    # 2. Passamos 'totais' para o index.html
    return render_template('index.html', dados=totais)

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
        flash('⛔ Acesso Negado! Você não tem permissão de administrador.')
        return redirect(url_for('dashboard')) # Manda de volta pro painel comum

    # 1. Pega a data de hoje
    from datetime import datetime
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    # 2. Busca os dados no banco
    lista = db.quant_refei_detl(hoje)
    
    # ... imports e data ...

    # 1. Prepara os totais (Agora com as categorias de "Autorizado")
    totais = {
        "Cafe": 0,   "Cafe_Autorizado": 0,
        "Almoco": 0, "Almoco_Autorizado": 0,
        "Jantar": 0, "Jantar_Autorizado": 0
    }
    
    if lista:
        for ref in lista:
            # Segurança: Verifica se existe funcionário vinculado para não dar erro
            cargo = ""
            if ref.funcionario:
                cargo = ref.funcionario.cargo.lower() # Converte para minúsculo para garantir

            # Verifica se é Admin
            eh_admin = (cargo == 'admin')

            # --- LÓGICA DO CAFÉ ---
            if "Café" in ref.tipo:
                if eh_admin:
                    totais["Cafe_Autorizado"] += 1
                else:
                    totais["Cafe"] += 1

            # --- LÓGICA DO ALMOÇO ---
            elif "Almoço" in ref.tipo:
                if eh_admin:
                    totais["Almoco_Autorizado"] += 1
                else:
                    totais["Almoco"] += 1

            # --- LÓGICA DO JANTAR ---
            elif "Jantar" in ref.tipo:
                if eh_admin:
                    totais["Jantar_Autorizado"] += 1
                else:
                    totais["Jantar"] += 1
    
    # Envia o dicionário completo para o HTML
    return render_template('paineladm.html', dados=totais)

@app.route('/registrar_refeicao', methods=['POST'])
@login_required
def registrar_refeicao():
    # Pega o valor do input hidden (Cafe, Almoco ou Jantar)
    tipo_escolhido = request.form.get('tipo_refeicao')
    
    hora_atual = datetime.now().hour

    if tipo_escolhido == "Café":
        if not (6<= hora_atual < 10):
            flash('❌ Horário inválido! O Café só é servido das 06:00 às 10:00.')
            logout_user()
            return redirect(url_for('login'))
    elif tipo_escolhido == "Almoço":
        if not (11 <= hora_atual < 15):
            flash('❌ Horário inválido! O Almoço só é servido das 11:00 às 15:00.')
            logout_user()
            return redirect(url_for('login'))
    elif tipo_escolhido == "Jantar":
        if not (18 <= hora_atual < 22):
            flash('❌ Horário inválido! O Jantar só é servido das 18:00 às 22:00.')
            logout_user()
            return redirect(url_for('login'))
    
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