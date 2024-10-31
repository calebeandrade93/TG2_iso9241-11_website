import bcrypt

def hash_password(password):
    # Gerar um salt e hash a senha
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def check_password(password, hashed_password):
    # Verificar a senha
    return bcrypt.checkpw(password.encode(), hashed_password)
