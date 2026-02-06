from sqlalchemy import create_engine, select, Date, cast
from sqlalchemy.orm import Session, joinedload
from werkzeug.security import generate_password_hash
from datetime import datetime
import models
import os

from config import DATABASE_URL, SECRET_KEY

class dbmanager():
    def __init__(self, url):

        self.engine = create_engine(url)

        models.Base.metadata.create_all(self.engine)

    def inserirfuncionario(self,cpf2,nome2,empresa2,cargo2,senha2):

        with Session(self.engine) as session:
            try:

                senhacripto = generate_password_hash(senha2)

                # --- CREATE (Criar) ---
                novo_usuario = models.Colaborador(cpf = cpf2, nome = nome2, empresa = empresa2, cargo = cargo2, senha = senhacripto)
                
                # Adicionamos à "área de preparação" da sessão
                session.add_all([novo_usuario])
                
                # Confirmamos a gravação no banco
                session.commit()

                return True
            
            except Exception as e:
                session.rollback()
                print(f"error ao salvar {e}")

                return False
            
    def refeicao(self,cpf2,tipo2):
    
        with Session(self.engine) as session:
                try:
                    # --- CREATE (Criar) ---
                    nova_refeicao = models.Refeicao(funcionario_cpf = cpf2,tipo = tipo2)
                    
                    # Adicionamos à "área de preparação" da sessão
                    session.add_all([nova_refeicao])
                    
                    # Confirmamos a gravação no banco
                    session.commit()

                    return True
                
                except Exception as e:
                    session.rollback()
                    print(f"error ao salvar {e}")

                    return False
                
    def refeicaoADM(self,cpf2,tipo2,quant):
    
        with Session(self.engine) as session:
                try:

                    quantidade = int(quant)

                    lista_para_salvar = []

                    for _ in range(quantidade):
                        # --- CREATE (Criar) ---
                        nova_refeicao = models.Refeicao(funcionario_cpf = cpf2,tipo = tipo2)
                        lista_para_salvar.append(nova_refeicao)


                    # Adicionamos à "área de preparação" da sessão
                    session.add_all(lista_para_salvar)
                    
                    # Confirmamos a gravação no banco
                    session.commit()

                    return True
                
                except Exception as e:
                    session.rollback()
                    print(f"error ao salvar {e}")

                    return False

    def get_colaborador_by_cpf(self, cpf_busca):
        with Session(self.engine) as session:
            try:
                # 1. Monta o Select: "Selecione o Colaborador onde o cpf é igual ao cpf_busca"
                stmt = select(models.Colaborador).where(models.Colaborador.cpf == cpf_busca)
                
                # 2. Executa e pega o primeiro resultado escalar (o objeto)
                # Se não achar ninguém, retorna None
                usuario = session.scalars(stmt).first()
                
                return usuario
                
            except Exception as e:
                print(f"Erro ao buscar usuário: {e}")
                return None

    def quant_refei_detl(self,date):
        with Session(self.engine) as session:
            try:

                data_formatada = datetime.strptime(date, "%d/%m/%Y").date()

                # 1. Monta o Select: "Selecione o Colaborador onde o cpf é igual ao cpf_busca"
                stmt = select(models.Refeicao).options(joinedload(models.Refeicao.funcionario)).where(
                    cast(models.Refeicao.data, Date) == data_formatada
                )

                # 2. Executa e pega o primeiro resultado escalar (o objeto)
                # Se não achar ninguém, retorna None
                refeicoes = session.scalars(stmt).all()

                return refeicoes
                
            except Exception as e:
                print(f"Erro ao buscar usuário: {e}")
                return 
            
    # No seu dbmanager ou arquivo de queries:
    def verificar_duplicidade(self, cpf, tipo_refeicao):
        # 1. Removemos 'session' dos argumentos e abrimos ela aqui dentro
        with Session(self.engine) as session:
            try:
                # 2. Calculamos a data aqui dentro mesmo
                hoje = datetime.now().date()
                
                stmt = select(models.Refeicao).where(
                    models.Refeicao.funcionario_cpf == cpf,
                    models.Refeicao.tipo == tipo_refeicao,
                    cast(models.Refeicao.data, Date) == hoje
                )
                
                resultado = session.scalars(stmt).first()
                
                # Retorna True se achou algo, False se não achou
                return resultado is not None

            except Exception as e:
                print(f"Erro na verificação: {e}")
                return False