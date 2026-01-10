import os
import yaml
from datetime import datetime
from dotenv import load_dotenv

from src.scraper import NewsScraper
from src.ai_curator import NewsCurator
from src.pdf_generator import NewsFormatter
from src.epub_generator import EpubGenerator
from src.emailer import EmailSender

load_dotenv()

def load_config():
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    topics = config['preferences']['topics']
    sources = config['sources']
    
    # Instancia as ferramentas
    scraper = NewsScraper()
    curator = NewsCurator()
    formatter = NewsFormatter()
    epub_gen = EpubGenerator()
    emailer = EmailSender()

    # --- ETAPA A: Coleta (O scraper agora imprime o próprio registro) ---
    candidates = scraper.get_candidates(sources, limit_per_source=5)
    
    if not candidates:
        print("📭 Nenhuma notícia encontrada nos feeds.")
        return

    # --- ETAPA B: Curadoria via IA ---
    print(f"🧠 IA analisando relevância para os tópicos: {', '.join(topics)}...")
    selected = curator.filter_candidates(candidates, topics, limit=2)


    if not selected:
        return

    # --- ETAPA C: Processamento ---
    processed_articles = []
    summaries = []
    
    print(f"⏳ Gerando resumos analíticos...")
    for item in selected:
        print(f"   📝 Processando: {item['title'][:50]}...")
        content_data = scraper.download_article_content(item['url'])
        
        if content_data:
            item.update(content_data)
            summary = curator.summarize_article(item)
            item['ai_summary'] = summary
            processed_articles.append(item)
            summaries.append(summary)

    # --- ETAPA D: Geração e Envio ---
    print(f"\n🎨 Finalizando edição do jornal...")
    briefing = curator.generate_briefing(summaries)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    epub_path = epub_gen.create_epub(briefing, processed_articles, output_filename=f"Jornal_{date_str}.epub")
    pdf_path = formatter.create_pdf(briefing, processed_articles, output_filename=f"Jornal_{date_str}.pdf")
    
    if epub_path:
        target = os.getenv("KINDLE_EMAIL")
        print(f"📤 Enviando para Kindle: {target}...")
        sent = emailer.send_pdf(epub_path, target_email=target)
        
        if sent:
            print(f"\n✨ SUCESSO! Edição concluída e enviada.")

if __name__ == "__main__":
    main()