import os

from flask import Flask, request, render_template, redirect, url_for, session
from services.register_validation import RegisterValidation
from services.retry_email import RetryEmail
from services.mongodb import Mongodb 
from services.encrypt_service import hash_password, check_password
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = 'mysecretkey'
app.config['SESSION_PERMANENT'] = False  # Define a sessão como não permanente
db_client = Mongodb()
load_dotenv()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['senha'].strip()
        
        user = db_client.get_user(email)
        if user and check_password(password, user['pwd_hash']):
            session['user_id'] = str(user['_id'])  # Guardar o ID do usuário na sessão
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login', message="Email ou senha incorretos."))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop('user_id', None)
    if request.method == 'POST':
        name = request.form['nome'].strip()
        email = request.form['email'].strip()
        password = request.form['senha'].strip()
        confirm_password = request.form['confirma_senha'].strip()
        phone = request.form['telefone'].strip()

        if not "@" in email or not "." in email:
            return redirect(url_for('register', message='Formato de e-mail inválido.'))
        
        is_user_registered = db_client.get_user(email)
        if is_user_registered:
            print('Usuário já cadastrado')
            return redirect(url_for('login', message='Usuário já cadastrado'))

        register_validation = RegisterValidation(name, email, password, confirm_password, phone)

        is_password_valid, message = register_validation.validate_password()
        if not is_password_valid:
            print(message)
            return redirect(url_for('register', message=message))
        
        hashed_password = hash_password(password)

        is_email, message, email_code = register_validation.validate_email()
        if not is_email:
            print(message)
            return redirect(url_for('register', message=message))

        user = {
            "name": name,
            "email": email,
            "pwd_hash": hashed_password,
            "created_at": datetime.now(),
            "phone": phone,
            "email_code": email_code,
            "is_verified": False
        }
        
        db_client.insert_user(user)

        print(message)
        return redirect(url_for('verify_email', message=message))

    return render_template('register.html')

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    session.pop('user_id', None)
    if request.method == 'POST':
        email = request.form['email'].strip()
        email_code = request.form['email_code'].strip()

        if not "@" in email or not "." in email:
            print('Formato de email inválido')
            return redirect(url_for('verify_email', message='Formato de e-mail inválido.'))

        is_user_registered = db_client.get_user(email)
        if not is_user_registered:
            print('Usuário não cadastrado')
            return redirect(url_for('register', message='Usuário não cadastrado'))
        
        if email_code != is_user_registered.get('email_code'):
            print('Código de verificação incorreto')
            return redirect(url_for('verify_email', message='Código de verificação incorreto'))
        
        if is_user_registered.get('is_verified'):
            print('Email já verificado')
            return redirect(url_for('login', message='Email já verificado'))
        
        db_client.update_user(email, {'is_verified': True})
        print('Email verificado com sucesso')
        return redirect(url_for('login', message='Email verificado com sucesso'))

    return render_template('verify_email.html')

@app.route('/resend_email_code', methods=['GET', 'POST'])
def resend_email_code():
    session.pop('user_id', None)
    if request.method == 'POST':
        email = request.form['email'].strip()
        is_user_registered = db_client.get_user(email)

        if not "@" in email or not "." in email:
            print('formato invalido de email')
            return redirect(url_for('verify_email', message='Formato de e-mail inválido.'))

        if not is_user_registered:
            print('Usuário não cadastrado')
            return redirect(url_for('register', message='Usuário não cadastrado'))
        
        if is_user_registered.get('is_verified'):
            print('Email já verificado')
            return redirect(url_for('login', message='Email já verificado'))
        
        retry = RetryEmail(email)
        email_code = retry.email_code
        is_email_sent, message = retry.send_retry_email()
        if not is_email_sent:
            print(message)
            return redirect(url_for('resend_email_code', message=message))
        
        db_client.update_user(email, {'email_code': email_code})
        print('Código de verificação reenviado com sucesso')
        return redirect(url_for('verify_email', message='Código de verificação reenviado com sucesso'))

    return render_template('resend_email.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    session.pop('user_id', None)
    return render_template('forgot_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    return render_template('change_password.html')

@app.route('/user_page')
def user_page():
    return render_template('user_page.html')

@app.route('/new_checklist')
def new_checklist():
    return render_template('new_checklist.html')

@app.route('/checklist')
def checklist():
    return render_template('checklist.html')