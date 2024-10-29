from flask import Flask, request, render_template, redirect, url_for, flash
from services.register_validation import RegisterValidation

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']
        telefone = request.form['telefone']

        is_valid, message = RegisterValidation.validate_passwords(senha, confirma_senha)
        if not is_valid:
            flash(message)
            return redirect(url_for('register'))

        verification_code = RegisterValidation.generate_random_string()
        RegisterValidation.send_verification_email(email, verification_code)
        flash('Um e-mail de verificação foi enviado para o seu endereço de e-mail.')
        return redirect(url_for('login'))

    return render_template('register.html')
