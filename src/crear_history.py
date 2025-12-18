import sys
import os

# Ajusta o path para encontrar os módulos src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import NewsHistory

def clear_history():
    print("🧹 Iniciando limpeza do histórico...")
    db = SessionLocal()
    
    try:
        # Deleta todos os registros da tabela news_history
        num_rows = db.query(NewsHistory).delete()
        db.commit()
        print(f"✅ Sucesso! {num_rows} itens foram removidos do histórico.")
        print("Agora o robô considerará todas as notícias como 'Novas' novamente.")
    except Exception as e:
        print(f"❌ Erro ao limpar histórico: {e}")
        db.rollback() # Desfaz caso dê erro no meio
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("Tem certeza que deseja APAGAR todo o histórico de notícias? (s/n): ")
    if confirm.lower() == 's':
        clear_history()
    else:
        print("Operação cancelada.")