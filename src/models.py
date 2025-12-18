# src/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base, engine

# Tabela de Usuários
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    kindle_email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # MELHORIA: cascade="all, delete-orphan"
    # Se deletar o usuário, apaga automaticamente as fontes, interesses e histórico dele.
    sources = relationship("Source", back_populates="user", cascade="all, delete-orphan")
    interests = relationship("Interest", back_populates="user", cascade="all, delete-orphan")
    history = relationship("NewsHistory", back_populates="user", cascade="all, delete-orphan")

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
    keyword = Column(String, nullable=False)

    user = relationship("User", back_populates="interests")

# Tabela de Histórico de Notícias
class NewsHistory(Base):
    __tablename__ = "news_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    
    # REMOVIDO: index=True (Pois agora temos o índice composto abaixo)
    url = Column(String, nullable=False)
    
    # Mantido como String para compatibilidade com RSS variados. 
    # Idealmente, converteríamos para DateTime no futuro.
    published_at = Column(String, nullable=True)
    
    processed_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="history")

    # MELHORIA: Índice Composto
    # Cria uma "via expressa" de busca combinando ID do Usuário + URL
    __table_args__ = (
        Index('idx_user_url', 'user_id', 'url'),
    )

def init_db():
    print("🔄 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()