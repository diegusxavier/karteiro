import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.password = os.getenv("EMAIL_PASSWORD")
        
        # O kindle_email padrão do .env fica como fallback
        self.default_kindle_email = os.getenv("KINDLE_EMAIL")

    def send_pdf(self, pdf_path, target_email=None):
        """
        Envia o PDF. Se target_email for informado, usa ele. 
        Senão, usa o padrão do .env.
        """
        recipient = target_email or self.default_kindle_email
        
        if not recipient:
            print("❌ Erro: Nenhum e-mail de destino informado.")
            return False

        print(f"📧 Enviando de {self.sender_email} para {recipient}...")

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = "" 

        msg.attach(MIMEText("", 'plain'))

        try:
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(pdf_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            print("📩 E-mail enviado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Falha no envio do e-mail: {e}")
            return False