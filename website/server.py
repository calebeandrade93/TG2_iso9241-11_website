import os

from flask import Flask, request, render_template, redirect, url_for, flash
from services.register_validation import RegisterValidation
from services.mongodb import Mongodb 
from services.encrypt_service import hash_password, check_password
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = 'mysecretkey'
db_client = Mongodb()
load_dotenv()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['nome']
        email = request.form['email']
        password = request.form['senha']
        confirm_password = request.form['confirma_senha']
        phone = request.form['telefone']
        
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
    if request.method == 'POST':
        email = request.form['email']
        email_code = request.form['email_code']

        

    return render_template('verify_email.html')
