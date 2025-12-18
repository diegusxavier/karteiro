# src/seed.py
import sys
import os
import yaml
from dotenv import load_dotenv

# Ajusta o path para conseguir importar os módulos irmãos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import User, Source, Interest

# Carrega variáveis de ambiente (.env) para pegar os emails
load_dotenv()

def load_yaml_config():
    """Lê o arquivo YAML antigo"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "settings.yaml")
    
    if not os.path.exists(config_path):
        print(f"❌ Arquivo não encontrado: {config_path}")
        return None
        
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def seed_data():
    db = SessionLocal()
    config = load_yaml_config()
    
    if not config:
        return

    print("🌱 Iniciando migração de dados (Seed)...")

    # 1. Cria (ou recupera) o Usuário Principal
    # Pegamos os dados do .env que você já usa
    user_email = os.getenv("SENDER_EMAIL", "usuario@exemplo.com")
    kindle_email = os.getenv("KINDLE_EMAIL", "kindle@exemplo.com")
    
    # Verifica se o usuário já existe
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        print(f"👤 Criando novo usuário: {user_email}")
        user = User(
            name="Admin", # Nome genérico, pode mudar depois
            email=user_email,
            kindle_email=kindle_email,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user) # Recarrega o objeto com o ID gerado pelo banco
    else:
        print(f"👤 Usuário encontrado: {user.email} (ID: {user.id})")

    # 2. Migrar Fontes (Sources)
    print("📰 Migrando fontes de notícias...")
    
    # Opcional: Limpar fontes antigas para não duplicar se rodar 2x
    # db.query(Source).filter(Source.user_id == user.id).delete()
    
    sources_list = config.get('sources', [])
    count_sources = 0
    
    for src in sources_list:
        # Verifica se essa fonte já existe para esse usuário
        exists = db.query(Source).filter(
            Source.user_id == user.id,
            Source.url == src['url']
        ).first()
        
        if not exists:
            new_source = Source(
                user_id=user.id,
                name=src['name'],
                url=src['url'],
                is_active=True
            )
            db.add(new_source)
            count_sources += 1
    
    print(f"   ✅ {count_sources} novas fontes adicionadas.")

    # 3. Migrar Interesses (Tópicos)
    print("🧠 Migrando tópicos de interesse...")
    
    # Limpa tópicos antigos para garantir que a lista do banco fique igual à do YAML
    db.query(Interest).filter(Interest.user_id == user.id).delete()
    
    topics_list = config.get('preferences', {}).get('topics', [])
    for topic in topics_list:
        new_interest = Interest(
            user_id=user.id,
            keyword=topic
        )
        db.add(new_interest)
    
    print(f"   ✅ {len(topics_list)} tópicos atualizados.")

    # Salva tudo
    db.commit()
    db.close()
    print("🏁 Migração concluída com sucesso!")

if __name__ == "__main__":
    seed_data()