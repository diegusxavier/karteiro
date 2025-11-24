import feedparser
import os
import requests
import uuid
from newspaper import Article
from datetime import datetime

class NewsScraper:
    def __init__(self, config):
        self.sources = config.get('sources', [])
        self.preferences = config.get('preferences', {})
        self.include_images = self.preferences.get('include_images', False)
        
        # Agora temos um limite de "candidatos" (olhar muitos) e "escolhidos" (baixar poucos)
        self.candidates_limit = 10 # Quantas manchetes olhar por site
        self.images_dir = os.path.join("data", "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def get_candidates(self):
        """
        Passo 1: Varre os RSS e retorna uma lista leve (apenas Título e Link)
        para a IA decidir o que vale a pena.
        """
        candidates = []
        print("🔎 Coletando manchetes candidatas...")

        for source in self.sources:
            try:
                feed = feedparser.parse(source['url'])
                # Pega os X primeiros itens do feed para análise
                for entry in feed.entries[:self.candidates_limit]:
                    candidates.append({
                        "id": str(uuid.uuid4()), # ID temporário para identificar a notícia
                        "title": entry.title,
                        "url": entry.link,
                        "source": source['name'],
                        "published": entry.get('published', '')
                    })
            except Exception as e:
                print(f"❌ [Erro no feed {source['name']}]: {e}")
        
        print(f"💬 Total de candidatos encontrados: {len(candidates)}")
        return candidates

    def download_article_content(self, url):
        """
        Passo 2: Baixa o conteúdo pesado APENAS das notícias aprovadas pela IA.
        """
        try:
            article = Article(url, language='pt')
            article.download()
            article.parse()
            
            # Baixa imagem
            local_image_path = None
            if self.include_images and article.top_image:
                local_image_path = self._download_image(article.top_image)

            return {
                "content": article.text,
                "image_url": article.top_image,
                "local_image_path": local_image_path,
                "authors": article.authors
            }
        except Exception as e:
            print(f"❌ [Erro ao baixar artigo {url}]: {e}")
            return None

    def _download_image(self, image_url):
        if not image_url: return None
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                filename = f"{uuid.uuid4()}.jpg"
                filepath = os.path.join(self.images_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
        except:
            return None
        return None