import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

class NewsFormatter:
    def __init__(self):
        # Configuração de Estilos do PDF
        self.styles = getSampleStyleSheet()
        
        # Criando estilos personalizados
        self.styles.add(ParagraphStyle(name='BriefingTitle', parent=self.styles['Title'], fontSize=24, spaceAfter=20))
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.darkblue))
        self.styles.add(ParagraphStyle(name='SubHeader', parent=self.styles['Heading3'], fontSize=14, spaceBefore=10, spaceAfter=5))
        self.styles.add(ParagraphStyle(name='ArticleTitle', parent=self.styles['Heading1'], fontSize=18, spaceBefore=20, spaceAfter=10, textColor=colors.darkred))
        self.styles.add(ParagraphStyle(name='Metadata', parent=self.styles['Italic'], fontSize=9, textColor=colors.gray, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='BodyTextCustom', parent=self.styles['BodyText'], fontSize=11, leading=15, spaceAfter=8))
    
    def _parse_markdown_to_flowables(self, text):
        """
        Converte string Markdown simples em elementos do ReportLab (Flowables).
        Suporta: #, ##, ###, *, - e **bold**.
        """
        flowables = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Tratamento de Negrito (**texto**) para tags XML do ReportLab (<b>texto</b>)
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)

            # Cabeçalhos
            if line.startswith('# '):
                flowables.append(Paragraph(line[2:], self.styles['BriefingTitle']))
            elif line.startswith('## '):
                flowables.append(Paragraph(line[3:], self.styles['SectionHeader']))
            elif line.startswith('### '):
                flowables.append(Paragraph(line[4:], self.styles['SubHeader']))
            
            # Listas / Bullets
            elif line.startswith('* ') or line.startswith('- '):
                # Usa caractere de bullet point
                bullet_text = f"• {line[2:]}"
                flowables.append(Paragraph(bullet_text, self.styles['BodyTextCustom']))
            
            # Texto Normal
            else:
                flowables.append(Paragraph(line, self.styles['BodyTextCustom']))
                
        return flowables

    def create_pdf(self, briefing_text, articles_list, output_filename="daily_briefing.pdf"):
        """
        Gera o arquivo PDF final.
        """
        output_path = os.path.join("data", "output", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []

        # --- 1. Capa / Briefing ---
        # Data no topo
        date_str = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Edição de: {date_str}", self.styles['Metadata']))
        story.append(Spacer(1, 10))
        
        # Conteúdo do Briefing
        story.extend(self._parse_markdown_to_flowables(briefing_text))
        
        # Quebra de página após o briefing
        story.append(PageBreak())

        # --- 2. Artigos (Deep Dive) ---
        story.append(Paragraph("Deep Dive: Notícias Detalhadas", self.styles['BriefingTitle']))
        story.append(Spacer(1, 20))

        for article in articles_list:
            # Título do Artigo
            story.append(Paragraph(article['title'], self.styles['ArticleTitle']))
            
            # Metadados (Fonte)
            source_info = f"Fonte: {article.get('source', 'Desconhecida')} | {article.get('published_at', '')}"
            story.append(Paragraph(source_info, self.styles['Metadata']))
            
            # Imagem (se houver e arquivo existir)
            if article.get('local_image_path') and os.path.exists(article['local_image_path']):
                try:
                    # Redimensiona mantendo proporção (largura fixa de 400px)
                    img = Image(article['local_image_path'])
                    aspect = img.imageHeight / float(img.imageWidth)
                    img.drawWidth = 400
                    img.drawHeight = 400 * aspect
                    story.append(img)
                    story.append(Spacer(1, 10))
                except Exception as e:
                    print(f"❌ Erro ao inserir imagem no PDF: {e}")

            # Conteúdo do Resumo (Markdown processado)
            # O article['ai_summary'] será adicionado no main.py, aqui assumimos que existe
            if 'ai_summary' in article:
                story.extend(self._parse_markdown_to_flowables(article['ai_summary']))
            
            # Separador visual entre artigos
            story.append(Spacer(1, 20))
            story.append(Paragraph("_" * 50, self.styles['BodyText'])) # Linha horizontal simples
            story.append(Spacer(1, 20))

        # Gera o arquivo
        try:
            doc.build(story)
            print(f"📇 PDF gerado com sucesso em: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return None

if __name__ == "__main__":
    # Teste Rápido
    formatter = NewsFormatter()
    
    dummy_briefing = "# Briefing Executivo\n## Visão Geral\nHoje o mercado subiu.\n* Ponto 1\n* Ponto 2"
    dummy_articles = [
        {
            "title": "Teste de Artigo",
            "source": "CNN",
            "ai_summary": "## Manchete Incrível\nEste é um texto de teste com **negrito**.\n* Takeaway 1",
            "local_image_path": None
        }
    ]
    
    formatter.create_pdf(dummy_briefing, dummy_articles)