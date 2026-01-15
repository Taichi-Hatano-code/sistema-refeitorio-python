import os
from dotenv import load_dotenv

# 1. Carrega o arquivo .env IMEDIATAMENTE
load_dotenv()

# 2. Pega as variáveis
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# 3. Monta a URL do banco (Para usar no SQLAlchemy)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 4. Pega a chave secreta (Para usar no Flask)
SECRET_KEY = os.getenv('FLASK_SECRET')