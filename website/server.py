import os

from flask import Flask, request, render_template, redirect, url_for, session
from services.register_validation import RegisterValidation
from services.retry_email import RetryEmail
from services.mongodb import Mongodb 
from services.encrypt_service import hash_password, check_password
from services.forgot_password import ForgotPassword
from services.build_template import BuildTemplate
from dotenv import load_dotenv
from datetime import datetime
from bson.objectid import ObjectId

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
            session['user_id'] = str(user['_id']) # Guardar o ID do usuário na sessão
            return redirect(url_for('user_page'))
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
    if request.method == 'POST':
        email = request.form['email'].strip()
        phone = request.form['telefone'].strip()

        if not "@" in email or not "." in email:
            print('Formato de email inválido')
            return redirect(url_for('forgot_password', message='Formato de e-mail inválido.'))
        
        user = db_client.get_user(email)

        if not user:
            print('Usuário não cadastrado')
            return redirect(url_for('forgot_password', message='Usuário não cadastrado'))
        
        if phone != user.get('phone'):
            print('Numero de telefone incorreto com o cadastrado.')
            return redirect(url_for('forgot_password', message='Número de telefone incorreto com o cadastrado.'))
        fgt = ForgotPassword(email)
        
        is_email_sent, message, new_pwd = fgt.send_forgot_password_email()
        if not is_email_sent:
            print(message)
            return redirect(url_for('forgot_password', message=message))
        
        new_pwd_hash = hash_password(new_pwd)
        
        db_client.update_user(email, {'pwd_hash': new_pwd_hash})
        print('Nova senha cadastrada com sucesso.')
        return redirect(url_for('login', message=message))

    return render_template('forgot_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        old_password = request.form['senha_antiga'].strip()
        new_password = request.form['nova_senha'].strip()
        confirm_new_password = request.form['confirma_nova_senha'].strip()

        if not "@" in email or not "." in email:
            print('Formato de email inválido')
            return redirect(url_for('change_password', message='Formato de e-mail inválido.'))
        
        user = db_client.get_user(email)
        if not user:
            print('Usuário não cadastrado')
            return redirect(url_for('change_password', message='Usuário não cadastrado'))
        
        if not check_password(old_password, user.get('pwd_hash')):
            print('Senha antiga incorreta')
            return redirect(url_for('change_password', message='Senha antiga incorreta'))
        
        if new_password != confirm_new_password:
            print('Nova senha e confirmação de nova senha não conferem')
            return redirect(url_for('change_password', message='Nova senha e confirmação de nova senha não conferem'))
        
        register_validation = RegisterValidation(user.get('name'), email, new_password, confirm_new_password, user.get('phone'))

        is_password_valid, message = register_validation.validate_password()
        if not is_password_valid:
            print(message)
            return redirect(url_for('change_password', message=message))
        
        new_pwd_hash = hash_password(new_password)
        
        db_client.update_user(email, {'pwd_hash': new_pwd_hash})
        print('Senha alterada com sucesso.')
        return redirect(url_for('user_page', message='Senha alterada com sucesso'))

    return render_template('change_password.html')

@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    if 'user_id' not in session:
        print('Usuario nao logado')
        return redirect(url_for('login', message='Faça login para acessar a página do usuário.'))

    user_id = session['user_id']
    user = db_client.get_user_by_id(ObjectId(user_id))
    user_name = user.get('name').split(' ')[0].capitalize()
    checklists = db_client.get_user_checklist(user_id)
    print(checklists)

    return render_template('user_page.html', user_name=user_name, user_checklists=checklists)

@app.route('/checklist', methods=['GET', 'POST'])
def checklist():

    questions = db_client.get_questions()

    if request.method == 'POST':
        checklist_id = request.form['checklist_id']
        
        checklist = db_client.get_checklist_by_id(ObjectId(checklist_id))
        print(checklist)

        user_answers = checklist.get('answers')

        template = BuildTemplate.build(questions, user_answers)
        print('Template finalizado:' + str(template))

        return render_template('checklist.html', template=template)
        
    template = BuildTemplate.build(questions)
    print('Template usuário nao logado finalizado:' + str(template))
    return render_template('checklist.html', template=template)

@app.route('/change_phone', methods=['GET', 'POST'])
def change_phone():

    if request.method == 'POST':
        email = request.form['email'].strip()
        old_number = request.form['telefone_antigo'].strip()
        new_number = request.form['telefone_novo'].strip()
        password = request.form['senha'].strip()

        if not "@" in email or not "." in email:
            print('Formato de email inválido')
            return redirect(url_for('change_phone', message='Formato de e-mail inválido.'))
        
        user = db_client.get_user(email)
        if not user:
            print('Usuário não cadastrado')
            return redirect(url_for('change_phone', message='Usuário não cadastrado'))
        
        if not check_password(password, user.get('pwd_hash')):
            print('Senha incorreta')
            return redirect(url_for('change_phone', message='Senha incorreta'))
        
        if user.get('phone') != old_number:
            print('Telefone antigo incorreto')
            return redirect(url_for('change_phone', message='Telefone antigo incorreto'))
        
        db_client.update_user(email, {'phone': new_number})
        print('Telefone alterado com sucesso.')
        return redirect(url_for('user_page', message='Telefone alterado com sucesso'))

    return render_template('change_phone.html')

@app.route('/delete_checklist', methods=['POST'])
def delete_checklist():
    if request.method == 'POST':
        checklist_id = request.form['checklist_id']
        db_client.db.userChecklist.delete_one({"_id": ObjectId(checklist_id)})
        return redirect(url_for('user_page', message='Checklist deletado com sucesso.'))

    return redirect(url_for('user_page', message='Erro ao deletar checklist.'))