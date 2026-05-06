import os
import re
import uuid
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

class Bookmark(Flowable):
    """
    Cria um marcador na barra lateral do PDF (Outline).
    """
    def __init__(self, title, level=0):
        Flowable.__init__(self)
        self.title = title
        self.level = level
        self.key = str(uuid.uuid4())

    def draw(self):
        # 1. Marca a posição atual na página
        self.canv.bookmarkPage(self.key)
        # 2. Adiciona o título ao índice lateral apontando para essa posição
        self.canv.addOutlineEntry(self.title, self.key, level=self.level)

class NewsFormatter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # --- ESTILOS PADRÃO (Ajustados para leitura normal) ---
        
        # Título Principal (Capa)
        self.styles.add(ParagraphStyle(
            name='BriefingTitle', 
            parent=self.styles['Title'], 
            fontSize=24,      # Reduzido de 32
            leading=30,       # Ajuste de entrelinha
            spaceAfter=20
        ))
        
        # Cabeçalhos de Seção (H2)
        self.styles.add(ParagraphStyle(
            name='SectionHeader', 
            parent=self.styles['Heading2'], 
            fontSize=18,      # Reduzido de 26
            leading=22,
            spaceBefore=15, 
            spaceAfter=10, 
            textColor=colors.darkblue
        ))
        
        # Sub-cabeçalhos (H3)
        self.styles.add(ParagraphStyle(
            name='SubHeader', 
            parent=self.styles['Heading3'], 
            fontSize=14,      # Reduzido de 22
            leading=18,
            spaceBefore=12, 
            spaceAfter=8
        ))
        
        # Título do Artigo
        self.styles.add(ParagraphStyle(
            name='ArticleTitle', 
            parent=self.styles['Heading1'], 
            fontSize=20,      # Reduzido de 28
            leading=24,
            spaceBefore=20, 
            spaceAfter=10, 
            textColor=colors.darkred
        ))
        
        # Metadados (Data, Fonte)
        self.styles.add(ParagraphStyle(
            name='Metadata', 
            parent=self.styles['Italic'], 
            fontSize=10,      # Reduzido de 14
            leading=12,
            textColor=colors.gray, 
            spaceAfter=10
        ))
        
        # CORPO DO TEXTO (Justificado)
        self.styles.add(ParagraphStyle(
            name='BodyTextCustom', 
            parent=self.styles['BodyText'], 
            fontSize=12,      # Reduzido de 18 (Padrão de documentos)
            leading=16,       # Entrelinha confortável para leitura
            spaceAfter=10,
            alignment=4       # Justificado
        ))
        
        # Links / Listas
        self.styles.add(ParagraphStyle(
            name='LinkItem', 
            parent=self.styles['BodyText'], 
            fontSize=12,      # Reduzido de 16
            leading=16, 
            spaceAfter=6
        ))

    def _parse_markdown_to_flowables(self, text):
        flowables = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            
            if line.startswith('# '): flowables.append(Paragraph(line[2:], self.styles['BriefingTitle']))
            elif line.startswith('## '): flowables.append(Paragraph(line[3:], self.styles['SectionHeader']))
            elif line.startswith('### '): flowables.append(Paragraph(line[4:], self.styles['SubHeader']))
            elif line.startswith('* ') or line.startswith('- '): flowables.append(Paragraph(f"• {line[2:]}", self.styles['BodyTextCustom']))
            else: flowables.append(Paragraph(line, self.styles['BodyTextCustom']))
        return flowables

    def create_pdf(self, briefing_text, articles_list, candidates_list=None, output_filename="daily_briefing.pdf"):
        output_path = os.path.join("data", "output", "pdfs", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A5, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
        story = []

        # IDs únicos para links internos
        for art in articles_list:
            art['internal_id'] = str(uuid.uuid4())

        # --- 1. Capa / Briefing ---
        date_str = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Edição de: {date_str}", self.styles['Metadata']))
        story.append(Spacer(1, 10))
        story.extend(self._parse_markdown_to_flowables(briefing_text))
        
        # Quebra para isolar o briefing
        story.append(PageBreak())

        # --- 2. Nesta Edição (Página Exclusiva) ---
        story.append(Paragraph("Nesta Edição", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        for art in articles_list:
            clean_title = escape(art['title'])
            # Link interno apontando para a âncora da notícia
            link_html = f'<a href="#{art["internal_id"]}" color="blue"><u>{clean_title}</u></a>'
            story.append(Paragraph(f"• {link_html}", self.styles['LinkItem']))

        # Quebra para isolar a lista de links das notícias reais
        story.append(PageBreak())

        # --- 3. Artigos (Deep Dive) ---
        for i, article in enumerate(articles_list):
            # Se não for o primeiro artigo, quebra a página (o primeiro já está quebrado pelo PageBreak acima)
            if i > 0:
                story.append(PageBreak())

            clean_title = escape(article['title'])
            
            # Bookmark na barra lateral
            story.append(Bookmark(clean_title, level=0))
            
            # Título com âncora (destino do link) e link externo (fonte)
            if article.get('url'):
                title_html = f'<a name="{article["internal_id"]}"/><a href="{article["url"]}" color="darkred">{clean_title}</a>'
            else:
                title_html = f'<a name="{article["internal_id"]}"/>{clean_title}'
            
            story.append(Paragraph(title_html, self.styles['ArticleTitle']))
            
            # Metadados
            source_info = f"Fonte: {article.get('source', 'Desconhecida')} | {article.get('published_at', '')}"
            story.append(Paragraph(source_info, self.styles['Metadata']))
            
            # Imagem
            if article.get('local_image_path') and os.path.exists(article['local_image_path']):
                try:
                    img = Image(article['local_image_path'])
                    available_width = 380 
                    aspect = img.imageHeight / float(img.imageWidth)
                    img.drawWidth = available_width
                    img.drawHeight = available_width * aspect
                    story.append(img)
                    story.append(Spacer(1, 15))
                except: pass

            # Conteúdo
            if 'ai_summary' in article:
                story.extend(self._parse_markdown_to_flowables(article['ai_summary']))
            
            # Rodapé visual
            story.append(Spacer(1, 25))
            story.append(Paragraph("_" * 30, self.styles['BodyTextCustom']))

        # --- 4. Lista de Candidatos ---
        if candidates_list:
            story.append(PageBreak())
            story.append(Paragraph("Outras Manchetes", self.styles['BriefingTitle']))
            story.append(Spacer(1, 15))

            for item in candidates_list:
                clean_title = escape(item['title'])
                url = item.get('url', '')
                source = item.get('source', '?')
                
                line_html = f'<b>[{source}]</b> <a href="{url}" color="blue">{clean_title}</a>'
                story.append(Paragraph(line_html, self.styles['LinkItem']))

        try:
            doc.build(story)
            print(f"PDF (XL + Sumário Exclusivo) gerado com sucesso em: {output_path}")
            return output_path
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return None