import sys
import os
import json
from google import genai
from dotenv import load_dotenv

# --- CORREÇÃO DE PATH ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import User

load_dotenv()

class NewsCurator:
    def __init__(self):
        """
        Inicializa o cliente do Gemini.
        Não precisamos mais passar 'config' aqui, pois os tópicos virão por usuário.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Erro: GEMINI_API_KEY não encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        # Podemos definir o modelo padrão aqui ou no .env
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def filter_candidates(self, candidates_list, user: User, limit=7):
        """
        Analisa as notícias baseada nos interesses do Usuário (banco de dados).
        """
        if not candidates_list:
            return []

        print(f"🧠 IA Analisando {len(candidates_list)} manchetes para {user.name}...")
        
        # Converte a lista de objetos 'Interest' do banco para uma lista de strings
        user_topics = [i.keyword for i in user.interests]
        topics_str = ", ".join(user_topics)
        
        if not user_topics:
            print("⚠️ Usuário sem tópicos definidos. Usando genéricos.")
            topics_str = "Notícias Importantes, Tecnologia, Ciência, Economia"

        # Prepara a lista para o prompt
        candidates_text = ""
        for item in candidates_list:
            candidates_text += f"ID: {item['id']} | Título: {item['title']} | Fonte: {item['source']}\n"

        prompt = f"""
        Você é um editor chefe pessoal. Seu usuário tem interesse nestes tópicos: {topics_str}.
        
        Abaixo está uma lista de manchetes candidatas. 
        Sua tarefa é selecionar até {limit} das notícias mais relevantes e importantes baseadas nos interesses do usuário.
        Se houver notícias repetidas ou muito similares, escolha apenas a melhor fonte.
        
        LISTA DE CANDIDATOS:
        {candidates_text}
        
        FORMATO DE RESPOSTA:
        Retorne APENAS uma lista JSON (Array de Strings) com os IDs das notícias escolhidas.
        Exemplo: ["id_1", "id_2", "id_5"]
        """

        try:
            # Chamada à API (JSON Mode)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            selected_ids = json.loads(response.text)
            
            # Validação e correção caso a IA retorne dict em vez de list
            if isinstance(selected_ids, dict):
                for val in selected_ids.values():
                    if isinstance(val, list):
                        selected_ids = val
                        break
            
            if not isinstance(selected_ids, list):
                selected_ids = []

            # Filtra a lista original mantendo apenas os escolhidos
            final_selection = [item for item in candidates_list if item['id'] in selected_ids]
            
            print(f"🎯 IA selecionou {len(final_selection)} notícias relevantes.")
            return final_selection

        except Exception as e:
            print(f"❌ [Erro na filtragem da IA]: {e}")
            # Fallback: Se a IA falhar, retorna os primeiros itens para não ficar sem jornal
            return candidates_list[:limit]

    def summarize_article(self, article_data):
        # Mantemos igual, pois o resumo depende mais do conteúdo da notícia
        print(f"🤔 Resumindo: {article_data['title']}...")
        prompt = f"""
        Você é um analista de inteligência. Analise a notícia abaixo:
        Título: {article_data['title']}
        Conteúdo: {article_data['content'][:10000]}

        OBJETIVO:
        Escreva um relatório de resumo (Deep Dive) em Português do Brasil.
        
        FORMATO (Markdown):
        - Se o título original for em inglês, traduza-o.
        - Resumo de 2 a 3 parágrafos.
        - Lista de 3 "Pontos Chave".
        - Seção "Contexto": Por que isso importa?
        - Tom profissional e direto. Sem saudações.
        """
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            return f"## {article_data['title']}\n\nErro ao gerar resumo: {e}"

    def generate_briefing(self, summaries_list):
        # Mantemos igual (Capa do jornal)
        print("📝 Escrevendo Editorial (Briefing)...")
        combined_text = "\n---\n".join(summaries_list)
        prompt = f"""
        Atue como Editor Chefe. Escreva a CAPA (Briefing Executivo) do jornal com base nestes resumos:
        
        RESUMOS:
        {combined_text}
        
        ESTRUTURA (Markdown):
        # KARTEIRO
        ## Visão Geral
        Um parágrafo conectando os fatos do dia.
        ## Destaques
        Bullets rápidos dos temas principais.
        ## O que observar
        Tendências futuras.
        
        Seja conciso.
        """
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except:
            return "# Briefing\nErro ao gerar briefing."

# --- TESTE ISOLADO ---
if __name__ == "__main__":
    from src.database import SessionLocal
    from src.scraper import NewsScraper

    db = SessionLocal()
    user = db.query(User).first()
    
    if user:
        # 1. Coleta (Scraper)
        scraper = NewsScraper(db)
        # Limitamos a 2 por fonte para economizar tokens no teste
        candidates = scraper.get_candidates(user, limit_per_source=2)
        
        if candidates:
            # 2. Curadoria (IA)
            curator = NewsCurator()
            # Passamos o objeto user para ele pegar os interesses
            selected = curator.filter_candidates(candidates, user, limit=3)
            
            print("\n--- Resultado do Teste ---")
            for item in selected:
                print(f"✅ Aprovado: {item['title']}")
        else:
            print("Nenhum candidato encontrado (verifique se já não estão todos no histórico).")
    
    db.close()