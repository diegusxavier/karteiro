import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class NewsCurator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Erro: GEMINI_API_KEY não encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def filter_candidates(self, candidates_list, topics, limit=7):
        """
        Analisa as notícias baseada em uma lista de tópicos (strings).
        """
        if not candidates_list:
            return []

        topics_str = ", ".join(topics) if topics else "Notícias Gerais"
        
        candidates_text = ""
        for item in candidates_list:
            candidates_text += f"ID: {item['id']} | Título: {item['title']} | Fonte: {item['source']}\n"

        prompt = f"""
        Você é um editor chefe pessoal. Seu usuário tem interesse nestes tópicos: {topics_str}.
        Selecione até {limit} notícias relevantes da lista abaixo.
        
        LISTA DE CANDIDATOS:
        {candidates_text}
        
        FORMATO DE RESPOSTA:
        Retorne APENAS um JSON (Array de Strings) com os IDs.
        Exemplo: ["id_1", "id_2"]
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            selected_ids = json.loads(response.text)
            
            # Garante que o retorno é uma lista
            if isinstance(selected_ids, dict):
                selected_ids = next(iter(selected_ids.values())) if isinstance(next(iter(selected_ids.values())), list) else []

            return [item for item in candidates_list if item['id'] in selected_ids]
        except Exception as e:
            print(f"❌ Erro na filtragem: {e}")
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

