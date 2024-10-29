import re
import random
import string
import smtplib
from email.mime.text import MIMEText

class RegisterValidation:
    @staticmethod
    def validate_passwords(password, confirm_password):
        if password != confirm_password:
            return False, "As senhas não são iguais."
        
        if len(password) < 8 or len(password) > 18:
            return False, "A senha deve ter entre 8 e 18 caracteres."
        
        if not re.search(r"[A-Z]", password):
            return False, "A senha deve conter pelo menos uma letra maiúscula."
        
        if not re.search(r"[a-z]", password):
            return False, "A senha deve conter pelo menos uma letra minúscula."
        
        if not re.search(r"[0-9]", password):
            return False, "A senha deve conter pelo menos um número."
        
        return True, ""

    @staticmethod
    def generate_random_string(length=20):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    @staticmethod
    def send_verification_email(user_email, verification_code):
        sender_email = "seu_email@example.com"
        sender_password = "sua_senha"
        subject = "Código de Verificação"
        body = f"Seu código de verificação é: {verification_code}"

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email

        with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
