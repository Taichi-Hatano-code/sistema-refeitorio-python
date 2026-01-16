from dbmanager import dbmanager
from config import DATABASE_URL

banco = dbmanager(DATABASE_URL)

# Testa direto aqui
lista = banco.quant_refei_detl("15/01/2026")

# Cria um dicionário para guardar as contas
contagem = {
    "Café da manhã": 0,
    "Almoço": 0,
    "Jantar": 0
}

for ref in lista:
    # Se o tipo da refeição estiver no dicionário, soma +1
    if ref.tipo in contagem:
        contagem[ref.tipo] += 1

# Exibe tudo de uma vez
for tipo, quantidade in contagem.items():
    print(f"{tipo}: {quantidade}")

    
for ref in lista:
    # CUIDADO: Confira se no models.py é 'data' ou 'data_registro'
    # Vou usar data_registro pois é o padrão, mas se der erro mude para ref.data
    hora = ref.data.strftime("%H:%M") 
        
    tipo = ref.tipo
                
    # Agora isso VAI funcionar por causa do joinedload
    nome = ref.funcionario.nome 
    cargo = ref.funcionario.cargo

    print(f"TESTE SUCESSO: Às {hora}, {nome} ({cargo}) comeu: {tipo}")