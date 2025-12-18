# src/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base, engine

# Tabela de Usuários
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False) # Email pessoal
    kindle_email = Column(String, nullable=False) # Email do Kindle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relacionamentos (1 usuário tem várias fontes, interesses e histórico)
    sources = relationship("Source", back_populates="user")
    interests = relationship("Interest", back_populates="user")
    history = relationship("NewsHistory", back_populates="user")

# Tabela de Fontes (RSS)
class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sources")

# Tabela de Tópicos de Interesse
class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    keyword = Column(String, nullable=False) # Ex: "Inteligência Artificial"

    user = relationship("User", back_populates="interests")

# Tabela de Histórico de Notícias (Para não repetir)
class NewsHistory(Base):
    __tablename__ = "news_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True) # Indexado para busca rápida
    published_at = Column(String, nullable=True)
    processed_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="history")

# Função que cria as tabelas no banco de verdade
def init_db():
    print("🔄 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()