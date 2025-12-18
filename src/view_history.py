import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import NewsHistory, User

db = SessionLocal()

# Pega os 20 últimos itens do histórico
history = db.query(NewsHistory).order_by(NewsHistory.id.desc()).limit(20).all()

print(f"{'ID':<5} | {'DATA':<12} | {'TÍTULO'}")
print("-" * 80)

for item in history:
    # Corta o título se for muito longo para caber na tela
    title = (item.title[:60] + '..') if len(item.title) > 60 else item.title
    print(f"{item.id:<5} | {str(item.processed_at)[:10]:<12} | {title}")

print("-" * 80)
print(f"Total de notícias já memorizadas: {db.query(NewsHistory).count()}")

db.close()