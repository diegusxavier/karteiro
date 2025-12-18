import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import dotenv

# Configurações de Conexão
# Nota: Como estamos rodando o script FORA do Docker (na venv), usamos 'localhost'.
# Se um dia o script python for para dentro do Docker, mudamos para 'db'.
DB_USER = os.getenv("DB_USER", "karteiro_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "karteiro_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "karteiro_db")

# URL de Conexão (Formato exigido pelo SQLAlchemy)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria o "motor" da conexão
engine = create_engine(DATABASE_URL)

# Cria a fábrica de sessões (usaremos isso para salvar/ler dados)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os Models
Base = declarative_base()

def get_db():
    """Função utilitária para pegar uma sessão de banco e fechar depois de usar"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Teste simples se rodar o arquivo direto
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("✅ Conexão com o PostgreSQL realizada com sucesso!")
    except Exception as e:
        print(f"❌ Falha ao conectar: {e}")