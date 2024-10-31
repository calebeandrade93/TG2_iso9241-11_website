import os
import smtplib
import ssl
import random

from email.message import EmailMessage

class RetryEmail:
    def __init__(self, email):
        self.email = email
        self.email_code = self.generate_random_number_sequence()

    def generate_random_number_sequence(self, length=8):
        return ''.join(str(random.randint(0, 9)) for _ in range(length))

    def send_retry_email(self):
        # Configuração do servidor SMTP
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = os.environ.get("SMTP_PORT")
        smtp_username = os.environ.get("EMAIL_USERNAME")
        smtp_password = os.environ.get("EMAIL_PASSWORD")

        body = f"""Olá, obrigado por seu cadastro.
        Estamos quase lá, só é necessário você confirmar o código fornecido neste email.

        Seu código de verificação é: {self.email_code}"""

        # Criação da mensagem de email
        msg = EmailMessage()
        msg['Subject'] = 'Código de Verificação TelaAudit'
        msg['From'] = smtp_username
        msg['To'] = self.email
        msg.set_content(body)

        context = ssl.create_default_context()

        try:
            print("Tentando conectar ao servidor SMTP...")
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
                print("Conexão estabelecida. Tentando fazer login...")
                server.login(smtp_username, smtp_password)
                print("Login bem-sucedido. Enviando email...")
                server.sendmail(smtp_username, self.email, msg.as_string())
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False, "Erro ao enviar email."
        
        return True, "Código de verificação reenviado com sucesso."