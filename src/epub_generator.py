import os
import uuid
from ebooklib import epub
from datetime import datetime

class EpubGenerator:
    def __init__(self):
        self.css_style = '''
            body { font-family: "Bookerly", "Charis SIL", serif; margin: 5%; }
            h1 { text-align: center; color: #2C3E50; margin-bottom: 0.5em; }
            h2 { color: #8E44AD; margin-top: 1em; }
            h3 { color: #2980B9; }
            p { text-align: justify; line-height: 1.5; font-size: 1.1em; }
            a { color: #007BFF; text-decoration: none; }
            .meta { color: #7F8C8D; font-style: italic; font-size: 0.8em; margin-bottom: 1em; }
            .divider { text-align: center; margin: 2em 0; }
            img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
        '''

    def create_epub(self, briefing_text, articles_list, unselected_list=None, output_filename="daily_briefing.epub"):
        # 1. Configuração Básica do Livro
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(f"Jornal Karteiro - {datetime.now().strftime('%d/%m/%Y')}")
        book.set_language('pt-br')
        book.add_author('Github: diegusxavier')

        # Adiciona Estilo CSS
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=self.css_style)
        book.add_item(nav_css)

        chapters = []

        # 2. Capítulo: Capa / Briefing (Convertendo Markdown para HTML simples)
        # Nota: Para um HTML mais robusto, poderíamos usar a lib 'markdown', mas faremos substituições simples aqui
        briefing_html = f"<h1>Briefing do Dia</h1>"
        briefing_html += self._markdown_to_html(briefing_text)
        
        c_briefing = epub.EpubHtml(title='Briefing Executivo', file_name='briefing.xhtml', lang='pt-br')
        c_briefing.content = briefing_html
        c_briefing.add_item(nav_css)
        book.add_item(c_briefing)
        chapters.append(c_briefing)

        # 3. Capítulos: Artigos
        for idx, art in enumerate(articles_list):
            # Cria nome de arquivo único
            file_name = f'article_{idx}.xhtml'
            
            # Título e Metadados
            title = art.get('title', 'Sem Título')
            source = art.get('source', 'Fonte Desconhecida')
            url = art.get('url', '#')
            
            # Processamento de Imagem
            img_tag = ""
            if art.get('local_image_path') and os.path.exists(art['local_image_path']):
                try:
                    # Adiciona a imagem ao pacote EPUB
                    img_filename = f"img_{idx}.jpg"
                    with open(art['local_image_path'], 'rb') as f:
                        img_content = f.read()
                    
                    epub_img = epub.EpubItem(uid=f"img_{idx}", file_name=f"images/{img_filename}", media_type="image/jpeg", content=img_content)
                    book.add_item(epub_img)
                    img_tag = f'<img src="images/{img_filename}" alt="Imagem da Notícia" />'
                except Exception as e:
                    print(f"Erro ao anexar imagem EPUB: {e}")

            # Conteúdo (Resumo da IA)
            content_body = self._markdown_to_html(art.get('ai_summary', ''))

            # Monta o HTML do capítulo
            html_content = f"""
                <h1>{title}</h1>
                <p class="meta">Fonte: {source}</p>
                {img_tag}
                <div class="content">
                    {content_body}
                </div>
                <hr class="divider"/>
                <p style="text-align: center;">
                    <a href="{url}">🔗 Ler notícia original completa</a>
                </p>
            """

            chapter = epub.EpubHtml(title=title, file_name=file_name, lang='pt-br')
            chapter.content = html_content
            chapter.add_item(nav_css)
            
            book.add_item(chapter)
            chapters.append(chapter)
        # 3.5 Novo Capítulo: Outras Manchetes
        if unselected_list:
            unselected_html = "<h1>Outras Manchetes</h1><ul>"
            for item in unselected_list:
                source = item.get('source', '?')
                title = item.get('title', 'Sem título')
                url = item.get('url', '#')
                unselected_html += f'<li><strong>[{source}]</strong> <a href="{url}">{title}</a></li>'
            unselected_html += "</ul>"

            c_unselected = epub.EpubHtml(title='Outras Manchetes', file_name='extra.xhtml', lang='pt-br')
            c_unselected.content = unselected_html
            c_unselected.add_item(nav_css)
            book.add_item(c_unselected)
            chapters.append(c_unselected)

        # 4. Define o Sumário (TOC) e Ordem de Leitura (Spine)
        book.toc = (
            (epub.Section('Destaques'), (c_briefing, )),
            (epub.Section('Notícias'), chapters[1:]) # Pula o briefing na seção de notícias
        )

        book.spine = ['nav'] + chapters
        
        # Cria atalhos de navegação
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 5. Salva o Arquivo
        output_path = os.path.join("data", "output", "epubs", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        epub.write_epub(output_path, book, {})
        print(f"📘 EPUB gerado com sucesso em: {output_path}")
        return output_path

    def _markdown_to_html(self, text):
        """Conversor simples de MD para HTML para manter dependências leves"""
        html = text.replace('\n', '<br/>')
        # Negrito
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        # Itálico
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        # Headers (simples)
        html = re.sub(r'### (.*?)<br/>', r'<h3>\1</h3>', html)
        html = re.sub(r'## (.*?)<br/>', r'<h2>\1</h2>', html)
        # Bullets (simples - transforma linha com * ou - em item solto, idealmente seria <ul>)
        html = re.sub(r'<br/>(\*|-) (.*?)', r'<br/>• \2', html)
        
        return html