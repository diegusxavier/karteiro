import feedparser
import os
import requests
import uuid
from newspaper import Article

class NewsScraper:
    def __init__(self):
        self.images_dir = os.path.join("data", "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def get_candidates(self, sources_list, limit_per_source=5):
        """
        Varre os feeds RSS fornecidos e retorna candidatos.
        """
        candidates = []
        for source in sources_list:
            try:
                feed = feedparser.parse(source['url'])
                for entry in feed.entries[:limit_per_source]:
                    candidates.append({
                        "id": str(uuid.uuid4()), 
                        "title": entry.title.strip(),
                        "url": entry.link.strip(),
                        "source": source['name'],
                        "published": entry.get('published', '')
                    })
            except Exception as e:
                print(f"❌ Erro no feed {source.get('name')}: {e}")
        return candidates

    def download_article_content(self, url):
        try:
            article = Article(url, language='pt')
            article.download()
            article.parse()
            return {"content": article.text, "image_url": article.top_image}
        except Exception as e:
            print(f"❌ Erro ao baixar {url}: {e}")
            return None