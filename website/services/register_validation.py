import random
import smtplib
import ssl
import os

from email.message import EmailMessage

class RegisterValidation:
    def __init__(self, name, email, password, confirm_password, phone):
        self.name = name
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.phone = phone
        self.email_code = self.generate_random_number_sequence()

    def validate_email(self):
        
        is_email_sent, message = self.send_verification_email()
        if not is_email_sent:
            return is_email_sent, message, None
        
        return True, "Código de verificação enviado para o email informado.", self.email_code

    def generate_random_number_sequence(self, length=8):
        return ''.join(str(random.randint(0, 9)) for _ in range(length))

    def send_verification_email(self):
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
            print("Email enviado com sucesso.")
            return True, "Email enviado com sucesso."
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
        
    def validate_password(self):
        if self.password != self.confirm_password:
            return False, "As senhas informadas não coincidem."
        if len(self.password) < 8 or len(self.password) > 20:
            return False, "A senha deve ter entre 8 e 20 caracteres."
        if not any(char.isdigit() for char in self.password):
            return False, "A senha deve conter pelo menos um número."
        if not any(char.isalpha() for char in self.password):
            return False, "A senha deve conter pelo menos uma letra."
        return True, ""