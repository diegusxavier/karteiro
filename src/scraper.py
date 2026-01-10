import feedparser
import os
import uuid
from newspaper import Article

class NewsScraper:
    def __init__(self):
        self.images_dir = os.path.join("data", "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def get_candidates(self, sources_list, limit_per_source=5):
        """
        Varre os feeds RSS e imprime o progresso da coleta no terminal.
        """
        candidates = []
        
        print("\n" + "="*50)
        print("📡 INICIANDO COLETA DE NOTÍCIAS")
        print("="*50)
        
        print(f"🔎 Fontes configuradas: {len(sources_list)}")
        
        for source in sources_list:
            print(f"\n   📡 Conectando a: {source['name']}...")
            try:
                feed = feedparser.parse(source['url'])
                
                if not feed.entries:
                    print(f"      ⚠️  Nenhum item encontrado no feed.")
                    continue

                count_added = 0
                for entry in feed.entries[:limit_per_source]:
                    title = entry.title.strip()
                    link = entry.link.strip()
                    
                    candidates.append({
                        "id": str(uuid.uuid4()), 
                        "title": title,
                        "url": link,
                        "source": source['name'],
                        "published": entry.get('published', '')
                    })
                    count_added += 1
                    print(f"      • [ENCONTRADA] {title[:60]}...")
                
                print(f"      ✅ {count_added} notícias capturadas.")

            except Exception as e:
                print(f"❌ [Erro no feed {source.get('name')}]: {e}")
        
        print("\n" + "="*50)
        print(f"📊 FIM DA COLETA: {len(candidates)} candidatos no total.")
        print("="*50 + "\n")
        
        return candidates

    def download_article_content(self, url):
        """Baixa o conteúdo completo usando Newspaper3k"""
        try:
            article = Article(url, language='pt')
            article.download()
            article.parse()
            return {
                "content": article.text,
                "image_url": article.top_image
            }
        except Exception as e:
            print(f"❌ [Erro ao baixar conteúdo]: {e}")
            return None