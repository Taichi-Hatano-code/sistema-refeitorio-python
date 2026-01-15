from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

# Importa as configurações prontas
from config import DATABASE_URL, SECRET_KEY 
from dbmanager import *
from models import *

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
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_colaborador_by_cpf(cpf)
        
        # Verifica se usuário existe e a senha bate
        if user and check_password_hash(user.senha, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required # <--- Protege a rota. Só logado entra.
def dashboard():
    return render_template('dashboard.html')

@app.route('/registrar_refeicao', methods=['POST'])
@login_required
def registrar_refeicao():
    # Pega o valor do input hidden (Cafe, Almoco ou Jantar)
    tipo_escolhido = request.form.get('tipo_refeicao')
    
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

@app.route('/logout')
@login_required
def logout():
    logout_user() # Limpa o cookie
    return redirect(url_for('home'))

if __name__ == "__main__":
    # host='0.0.0.0' libera o acesso para a rede
    # port=5000 é a porta padrão (você pode mudar se quiser)
    app.run(host='0.0.0.0', port=5000, debug=True)