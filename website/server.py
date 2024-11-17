import io
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
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
app.config['SESSION_PERMANENT'] = False  
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
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
    
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
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('register'))
            
        
        is_user_registered = db_client.get_user(email)
        if is_user_registered:
            flash('Usuário já cadastrado', 'danger')
            return redirect(url_for('login'))

        register_validation = RegisterValidation(name, email, password, confirm_password, phone)

        is_password_valid, message = register_validation.validate_password()
        if not is_password_valid:
            flash(message, 'danger')
            return redirect(url_for('register'))
        
        hashed_password = hash_password(password)

        is_email, message, email_code = register_validation.validate_email()
        if not is_email:
            flash(message, 'danger')
            return redirect(url_for('register'))

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

        flash(message, 'success')
        return redirect(url_for('verify_email'))

    return render_template('register.html')

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    session.pop('user_id', None)
    if request.method == 'POST':
        email = request.form['email'].strip()
        email_code = request.form['email_code'].strip()

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('verify_email'))

        is_user_registered = db_client.get_user(email)
        if not is_user_registered:
            flash('Usuário não cadastrado', 'danger')
            return redirect(url_for('register'))
        
        if email_code != is_user_registered.get('email_code'):
            flash('Código de verificação incorreto', 'danger')
            return redirect(url_for('verify_email'))
        
        if is_user_registered.get('is_verified'):
            flash('Email já verificado', 'danger')
            return redirect(url_for('login'))
        
        db_client.update_user(email, {'is_verified': True})
        flash('Email verificado com sucesso', 'success')
        return redirect(url_for('login'))

    return render_template('verify_email.html')

@app.route('/resend_email_code', methods=['GET', 'POST'])
def resend_email_code():
    session.pop('user_id', None)
    if request.method == 'POST':
        email = request.form['email'].strip()
        is_user_registered = db_client.get_user(email)

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('verify_email'))

        if not is_user_registered:
            flash('Usuário não cadastrado', 'danger')
            return redirect(url_for('register'))
        
        if is_user_registered.get('is_verified'):
            flash('Email já verificado', 'danger')
            return redirect(url_for('login'))
        
        retry = RetryEmail(email)
        email_code = retry.email_code
        is_email_sent, message = retry.send_retry_email()
        if not is_email_sent:
            flash(message, 'danger')
            return redirect(url_for('resend_email_code'))
        
        db_client.update_user(email, {'email_code': email_code})
        flash('Código de verificação reenviado com sucesso', 'success')
        return redirect(url_for('verify_email'))

    return render_template('resend_email.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    session.pop('user_id', None)
    if request.method == 'POST':
        email = request.form['email'].strip()
        phone = request.form['telefone'].strip()

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('forgot_password'))
        
        user = db_client.get_user(email)

        if not user:
            flash('Usuário não cadastrado', 'danger')
            return redirect(url_for('forgot_password'))
        
        if phone != user.get('phone'):
            flash('Número de telefone incorreto com o cadastrado', 'danger')
            return redirect(url_for('forgot_password'))
        fgt = ForgotPassword(email)
        
        is_email_sent, message, new_pwd = fgt.send_forgot_password_email()
        if not is_email_sent:
            flash(message, 'danger')
            return redirect(url_for('forgot_password'))
        
        new_pwd_hash = hash_password(new_pwd)
        
        db_client.update_user(email, {'pwd_hash': new_pwd_hash})
        flash(message, 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        old_password = request.form['senha_antiga'].strip()
        new_password = request.form['nova_senha'].strip()
        confirm_new_password = request.form['confirma_nova_senha'].strip()

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('change_password'))
        
        user = db_client.get_user(email)
        if not user:
            flash('Usuário não cadastrado', 'danger')
            return redirect(url_for('change_password'))
        
        if not check_password(old_password, user.get('pwd_hash')):
            flash('Senha antiga incorreta', 'danger')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_new_password:
            flash('Nova senha e confirmação de nova senha não conferem', 'danger')
            return redirect(url_for('change_password'))
        
        register_validation = RegisterValidation(user.get('name'), email, new_password, confirm_new_password, user.get('phone'))

        is_password_valid, message = register_validation.validate_password()
        if not is_password_valid:
            flash(message, 'danger')
            return redirect(url_for('change_password'))
        
        new_pwd_hash = hash_password(new_password)
        
        db_client.update_user(email, {'pwd_hash': new_pwd_hash})
        flash('Senha alterada com sucesso', 'success')
        return redirect(url_for('user_page'))

    return render_template('change_password.html')

@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    if 'user_id' not in session:
        flash('Faça login para acessar a página do usuário.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db_client.get_user_by_id(ObjectId(user_id))
    user_name = user.get('name').split(' ')[0].capitalize()
    checklists = db_client.get_user_checklist(user_id)

    return render_template('user_page.html', user_name=user_name, user_checklists=checklists)

@app.route('/checklist', methods=['GET', 'POST'])
def checklist():

    questions = db_client.get_questions()

    if request.method == 'POST':
        checklist_id = request.form['checklist_id']
        
        checklist = db_client.get_checklist_by_id(ObjectId(checklist_id))
        print(checklist)

        user_answers = checklist.get('answers')
        checklist_id = checklist.get('_id')

        template = BuildTemplate.build_for_front(questions, user_answers)
        print('Template finalizado:' + str(template))

        return render_template('checklist.html', template=template, enumerate=enumerate, checklist_id=checklist_id)
        
    return render_template('checklist.html', template=template)

@app.route('/change_phone', methods=['GET', 'POST'])
def change_phone():

    if request.method == 'POST':
        email = request.form['email'].strip()
        old_number = request.form['telefone_antigo'].strip()
        new_number = request.form['telefone_novo'].strip()
        password = request.form['senha'].strip()

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('change_phone'))
        
        user = db_client.get_user(email)
        if not user:
            flash('Usuário não cadastrado', 'danger')
            return redirect(url_for('change_phone'))
        
        if not check_password(password, user.get('pwd_hash')):
            flash('Senha incorreta', 'danger')
            return redirect(url_for('change_phone'))
        
        if user.get('phone') != old_number:
            flash('Telefone antigo incorreto', 'danger')
            return redirect(url_for('change_phone'))
        
        db_client.update_user(email, {'phone': new_number})
        flash('Telefone alterado com sucesso', 'success')
        return redirect(url_for('user_page'))

    return render_template('change_phone.html')

@app.route('/delete_checklist', methods=['POST'])
def delete_checklist():
    if request.method == 'POST':
        checklist_id = request.form['checklist_id']
        db_client.db.userChecklist.delete_one({"_id": ObjectId(checklist_id)})
        flash('Checklist deletado com sucesso', 'success')
        return redirect(url_for('user_page'))

    return redirect(url_for('user_page', message='Erro ao deletar checklist.'))

@app.route('/save_checklist', methods=['POST'])
def save_checklist():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('Faça login para salvar o checklist.', 'danger')
            return redirect(url_for('login'))
        
        checklist_id = request.form.get('checklist_id')
        form_data = request.form.to_dict()
        answers = BuildTemplate.build_to_save(form_data)
        updated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        updates = {
            "answers": answers, 
            "updated_at": updated_at
        }

        db_client.update_user_checklist(ObjectId(checklist_id), updates)
        flash('Checklist atualizado com sucesso.', 'success')
        return redirect(url_for('user_page'))

    flash('Erro ao salvar checklist.', 'danger')
    return redirect(url_for('user_page'))

@app.route('/new_checklist', methods=['POST'])
def new_checklist():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('Faça login para criar um novo checklist.', 'danger')
            return redirect(url_for('login'))

        checklist_name = request.form.get('checklist_name')
        if not checklist_name:
            flash('Nome do checklist não pode estar vazio.', 'danger')
            return redirect(url_for('user_page'))

        # Criar um novo checklist
        new_checklist = {
            "user": user_id,
            "name": checklist_name,
            "answers": [],
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        db_client.db.userChecklist.insert_one(new_checklist)

        flash('Novo checklist criado com sucesso.', 'success')
        return redirect(url_for('user_page'))

    flash('Erro ao criar novo checklist.', 'danger')
    return redirect(url_for('user_page'))

@app.route('/export_checklist', methods=['POST'])
def export_checklist():
    if request.method == 'POST':
        checklist_id = request.form.get('checklist_id')
        checklist = db_client.get_checklist_by_id(ObjectId(checklist_id))
        questions = db_client.get_questions()
        user_answers = checklist.get('answers')

        template = BuildTemplate.build_for_front(questions, user_answers)

        pdf_content = BuildTemplate.build_pdf(template, 
                                                checklist.get('name'), 
                                                checklist.get('created_at'), 
                                                checklist.get('updated_at')
                                             )
        
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='checklist.pdf'
        )

    flash('Erro ao exportar checklist.', 'danger')
    return redirect(url_for('user_page'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['nome'].strip()
        email = request.form['email'].strip()
        message = request.form['mensagem'].strip()

        if not "@" in email or not "." in email:
            flash('Formato de email inválido', 'danger')
            return redirect(url_for('contact'))

        flash('E-mail enviado para o suporte.', 'success')
        return redirect(url_for('home'))

    return render_template('contact.html')        
