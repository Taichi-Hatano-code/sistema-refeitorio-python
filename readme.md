# Sistema de Controle de Refeições

Sistema híbrido (Web e Desktop) para gestão de refeitórios corporativos.

## 🚀 Tecnologias
- **Backend:** Python, SQLAlchemy, PostgreSQL
- **Web:** Flask, HTML/CSS (Jinja2)
- **Desktop:** PyQt6
- **Infra:** Docker Compose

## 🔧 Como rodar
1. Clone o repositório.
2. Crie um arquivo `.env` baseado nas configurações do docker-compose.
3. Suba o banco: `docker-compose up -d`
4. Instale as dependências: `pip install -r requirements.txt`
5. Rode o app: `python main.py` (Desktop) ou `python site.py` (Web).