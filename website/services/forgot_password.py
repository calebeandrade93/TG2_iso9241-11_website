import os
import smtplib
import ssl
import random

from email.message import EmailMessage

class ForgotPassword:

    def __init__(self, email):
        self.email = email
        self.new_password = self.generate_new_password()

    def send_forgot_password_email(self):
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = os.environ.get("SMTP_PORT")
        smtp_username = os.environ.get("EMAIL_USERNAME")
        smtp_password = os.environ.get("EMAIL_PASSWORD")

        body = f"""Olá, você solicitou a redefinição de senha.
        Essa é a sua senha temporária: {self.new_password}, acesse seu perfil e altere-a o quanto antes."""
        
        msg = EmailMessage()
        msg['Subject'] = 'Redefinição de Senha TelaAudit'
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
        except smtplib.SMTPRecipientsRefused:
            print("O endereço de email do destinatário foi recusado.")
            return False, "Email não existente, por favor, informe um email válido."
        except smtplib.SMTPAuthenticationError:
            print("Erro de autenticação ao tentar enviar o email.")
            return False, "Erro ao cadastrar, por favor tente novamente."
        except smtplib.SMTPConnectError:
            print("Erro ao conectar ao servidor SMTP.")
            return False, "Erro ao cadastrar, por favor tente novamente."
        except smtplib.SMTPException as e:
            print(f"Ocorreu um erro ao enviar o email: {e}")
            return False, "Erro ao cadastrar, por favor tente novamente."
        except TimeoutError:
            print("A conexão com o servidor SMTP expirou.")
            return False, "Erro ao cadastrar, por favor tente novamente."
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False, "Erro ao enviar email. Contate o suporte."
        
        return True, "Email com nova senha enviado com sucesso.", self.new_password
    
    def generate_new_password(self):
        print('Gerando nova senha')
        new_password = ""
        for _ in range(10):
            new_password += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        self.new_password = new_password
        return new_password