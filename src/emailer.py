import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self, config=None):
        """
        Inicializa o enviador de e-mail carregando tudo das variáveis de ambiente (.env).
        O parâmetro 'config' é mantido para compatibilidade, mas não é usado para credenciais.
        """
        # Carregando do .env
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.kindle_email = os.getenv("KINDLE_EMAIL")
        self.password = os.getenv("EMAIL_PASSWORD")
        
        # Validação de Segurança
        missing_vars = []
        if not self.sender_email: missing_vars.append("SENDER_EMAIL")
        if not self.kindle_email: missing_vars.append("KINDLE_EMAIL")
        if not self.password: missing_vars.append("EMAIL_PASSWORD")
        
        if missing_vars:
            raise ValueError(f"❌ Configurações de e-mail faltando no arquivo .env: {', '.join(missing_vars)}")

    def send_pdf(self, pdf_path):
        print(f"📧 Preparando envio de {self.sender_email} para {self.kindle_email}...")

        # Montando o Objeto do E-mail
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.kindle_email
        msg['Subject'] = "Convert" 

        body = ""
        msg.attach(MIMEText(body, 'plain'))

        # Anexando o PDF
        try:
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(pdf_path)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)

        except Exception as e:
            print(f"❌ Erro ao anexar arquivo: {e}")
            return False

        # Conexão e Envio (SMTP)
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls() # Criptografia TLS
            server.login(self.sender_email, self.password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.kindle_email, text)
            server.quit()
            print("📩 E-mail enviado com sucesso para o Kindle!")
            return True
        except Exception as e:
            print(f"❌ Falha no envio do e-mail: {e}")
            print("Dica: Verifique se a 'Senha de App' foi gerada corretamente e se o SMTP está liberado.")
            return False