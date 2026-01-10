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
    print("🚀 Iniciando Karteiro (Versão Sem Banco)...")
    config = load_config()
    
    # Extrai configurações do YAML
    topics = config['preferences']['topics']
    sources = config['sources']
    
    scraper = NewsScraper()
    curator = NewsCurator()
    formatter = NewsFormatter()
    epub_gen = EpubGenerator()
    emailer = EmailSender()

    # --- ETAPA A: Coleta ---
    candidates = scraper.get_candidates(sources, limit_per_source=5)
    
    # --- ETAPA B: Curadoria ---
    selected = curator.filter_candidates(candidates, topics, limit=7)
    
    # --- ETAPA C: Processamento ---
    processed_articles = []
    summaries = []
    for item in selected:
        content = scraper.download_article_content(item['url'])
        if content:
            item.update(content)
            summary = curator.summarize_article(item)
            item['ai_summary'] = summary
            processed_articles.append(item)
            summaries.append(summary)

    if not processed_articles:
        print("📭 Nenhuma notícia encontrada.")
        return

    # --- ETAPA D: Geração e Envio ---
    briefing = curator.generate_briefing(summaries)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    epub_path = epub_gen.create_epub(briefing, processed_articles, output_filename=f"Jornal_{date_str}.epub")
    
    if epub_path:
        # Nota: kindle_email deve estar no .env ou ser passado aqui
        target = os.getenv("KINDLE_EMAIL")
        emailer.send_pdf(epub_path, target_email=target)
        print("✅ Processo concluído!")

if __name__ == "__main__":
    main()