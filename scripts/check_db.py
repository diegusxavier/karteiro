# check_db.py
from src.database import SessionLocal
from src.models import User

db = SessionLocal()
user = db.query(User).first()

if user:
    print(f"Usuário: {user.name} ({user.email})")
    print(f"Fontes: {len(user.sources)}")
    print(f"Tópicos: {[t.keyword for t in user.interests]}")
else:
    print("Banco vazio!")
db.close()