from app import app
from flask import Flask, redirect, url_for, render_template, request, session, flash, request, abort
import sqlite3
import markdown
import bleach
import re
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from flask_wtf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer
import os
import re
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
import base64
import time
from flask import jsonify

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DJ~AuNK#nV-5kp.=F=kr~0LK][{kS@')
secret_key = app.config['SECRET_KEY']

serializer = URLSafeTimedSerializer(secret_key)



ALLOWED_TAGS = [
    'p', 'ul', 'img', 'li', 'ol', 'strong', 'em', 'a', 'blockquote', 'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br']
ALLOWED_ATTRIBUTES = {
     'a': ['href', 'title'],
    'img': ['src', 'alt']
}

def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_of_this_app (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                public_key BLOB NOT NULL,
                private_key BLOB NOT NULL,
                salt BLOB NOT NULL,
                iv BLOB NOT NULL,
                tag BLOB NOT NULL,
                encrypted_totp_secret BLOB NOT NULL,
                totp_iv BLOB NOT NULL, 
                totp_tag BLOB NOT NULL,
                topt_salt BLOB NOT NULL,
                reset_password_token TEXT,
                reset_password_salt BLOB
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes_of_this_app (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                author TEXT NOT NULL,
                signature BLOB NOT NULL,
                ip_address TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_of_this_app (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_details TEXT,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users_of_this_app(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes_of_this_app (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes_of_this_app(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users_of_this_app(id) ON DELETE CASCADE,
                UNIQUE(note_id, user_id)
            )
        ''')
        conn.commit()

init_db()
@app.route("/like/<int:note_id>", methods=["POST"])
def like_note(note_id):
    delay = 2
    start_time = time.time()
    
    username = session.get("user")
    ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))
    
    if not username:
        if time.time() - start_time < delay:
            time.sleep(delay - (time.time() - start_time))
        log_event("ERROR", "Like_attempt_not_logged", None, ip_address)
        return jsonify({"success": False, "message": "Musisz być zalogowany"}), 401
    
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Pobierz user_id
        cursor.execute("SELECT id FROM users_of_this_app WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            if time.time() - start_time < delay:
                time.sleep(delay - (time.time() - start_time))
            return jsonify({"success": False, "message": "Użytkownik nie istnieje"}), 404
        
        user_id = user[0]
        
        # Sprawdź czy notatka istnieje
        cursor.execute("SELECT id FROM notes_of_this_app WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            if time.time() - start_time < delay:
                time.sleep(delay - (time.time() - start_time))
            log_event("ERROR", f"Like_attempt_invalid_note_{note_id}", user_id, ip_address)
            return jsonify({"success": False, "message": "Notatka nie istnieje"}), 404
        
        # Sprawdź czy użytkownik już polubił tę notatkę
        cursor.execute(
            "SELECT id FROM likes_of_this_app WHERE note_id = ? AND user_id = ?",
            (note_id, user_id)
        )
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Usuń lajka (unlike)
            cursor.execute(
                "DELETE FROM likes_of_this_app WHERE note_id = ? AND user_id = ?",
                (note_id, user_id)
            )
            conn.commit()
            
            # Pobierz aktualną liczbę lajków
            cursor.execute("SELECT COUNT(*) FROM likes_of_this_app WHERE note_id = ?", (note_id,))
            like_count = cursor.fetchone()[0]
            
            log_event("UNLIKE", f"Note_{note_id}_unliked", user_id, ip_address)
            
            if time.time() - start_time < delay:
                time.sleep(delay - (time.time() - start_time))
            
            return jsonify({"success": True, "action": "unliked", "likes": like_count}), 200
        else:
            # Dodaj lajka
            try:
                cursor.execute(
                    "INSERT INTO likes_of_this_app (note_id, user_id) VALUES (?, ?)",
                    (note_id, user_id)
                )
                conn.commit()
                
                # Pobierz aktualną liczbę lajków
                cursor.execute("SELECT COUNT(*) FROM likes_of_this_app WHERE note_id = ?", (note_id,))
                like_count = cursor.fetchone()[0]
                
                log_event("LIKE", f"Note_{note_id}_liked", user_id, ip_address)
                
                if time.time() - start_time < delay:
                    time.sleep(delay - (time.time() - start_time))
                
                return jsonify({"success": True, "action": "liked", "likes": like_count}), 200
            except sqlite3.IntegrityError:
                if time.time() - start_time < delay:
                    time.sleep(delay - (time.time() - start_time))
                return jsonify({"success": False, "message": "Już polubiłeś tę notatkę"}), 400
            

def generate_key_from_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_data_gcm(data, key):
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return ciphertext, iv, encryptor.tag

def decrypt_data_gcm(ciphertext, key, iv, tag):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# @app.errorhandler(CSRFError)
# def handle_csrf_error(e):
#     flash("Nieprawidłowy token CSRF. Spróbuj ponownie.", "danger")
#     return redirect(url_for("index"))

@app.route("/render", methods=['GET', 'POST'])
def render():
    delay = 3
    start_time = time.time()
    if request.method == "POST":
        # csrf_token = request.form.get("csrf_token")
        # if not csrf_token or csrf_token != session.get("_csrf_token"):
        #     flash("Nieprawidłowy żeton CSRF.", "danger")
        #     abort(403)
        md = request.form.get("markdown", "")
        password = request.form.get("password", "")
        ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

        if len(md) > 1000:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Tekst jest zbyt długi!", "danger")
            return redirect(url_for("index"))
        
        username = session.get("user")
        if not username:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            log_event("ERROR", "Someone_not_logged", None, ip_address)
            flash("Musisz być zalogowany, aby dodać notatkę.", "danger")
            return redirect(url_for("index"))
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT id
                    FROM users_of_this_app
                    WHERE username = ?
                """, (username,))
            user = cursor.fetchone()
        if user:
            id = user[0]
        else:
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            return redirect(url_for("index"))

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, private_key, iv, tag, salt FROM users_of_this_app WHERE username = ?", (username,))
            user_data = cursor.fetchone()

        if not user_data or not check_password_hash(user_data[0], password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            log_event("LOGIN_ERROR", "Wrong_login_data", id, ip_address)
            flash("Nieprawidłowe hasło.", "danger")
            return redirect(url_for("index"))

        encrypted_private_key, iv, tag, salt = user_data[1], user_data[2], user_data[3], user_data[4]
        try:
            decryption_key = generate_key_from_password(password+secret_key, salt)
            private_key_bytes = decrypt_data_gcm(encrypted_private_key, decryption_key, iv, tag)
        except Exception as e:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            log_event("ERROR", "Key_error"+str(e), id, ip_address)
            flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))

        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )

        rendered = markdown.markdown(md)
        safe_rendered = bleach.clean(rendered, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

        signature = private_key.sign(
            safe_rendered.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        add_note_to_db(username, safe_rendered, signature, ip_address)
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        return render_template("markdown.html", rendered=safe_rendered, ip_address=ip_address)
    
    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("markdown.html", rendered="")


def add_note_to_db(username, message, signature, ip_address):
    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes_of_this_app (message, author, signature, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (message, username, sqlite3.Binary(signature), ip_address))
            conn.commit()
    except sqlite3.Error as e:
        raise
    
def log_event(event_type, event_details=None, user_id=None, ip_address = None):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs_of_this_app (event_type, event_details, user_id, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (event_type, event_details, user_id, ip_address))
        conn.commit()


# @app.route("/render/<rendered_id>")
# def render_old(rendered_id):
#     if int(rendered_id) > len(notes):
#         return "Wrong note id", 404

#     rendered = notes[int(rendered_id) - 1]
#     return render_template("markdown.html", rendered=rendered)

# Strona główna z formularzem logowania
@app.route("/", methods=["GET", "POST"])
def index():
    delay = 3
    start_time = time.time()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        totp_token = request.form.get("totp")

        ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

        if not username or not password or not totp_token:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Wszystkie pola są wymagane!", "danger")
            return redirect(url_for("index"))
        
        time_window = 10 * 60
        max_failed_attempts = 3

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM logs_of_this_app
                JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
                WHERE logs_of_this_app.event_type = ? 
                AND users_of_this_app.username = ? 
                AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
            """, ("LOGIN_ERROR", username, f"-{time_window}")
            )
            failed_attempts = cursor.fetchone()
            failed_attempts = failed_attempts[0]

            cursor.execute("""
                SELECT id
                FROM users_of_this_app
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            if user:
                id = user[0]
            else:
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            if failed_attempts >= max_failed_attempts:
                log_event("LOGIN_ERROR_MAX", "Too_many_login_errors", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Zbyt wiele nieudanych prób logowania. Spróbuj ponownie za kilka minut.", "danger")
                return redirect(url_for("index"))
            cursor.execute("""
                SELECT id , password, encrypted_totp_secret, totp_iv, totp_tag, topt_salt 
                FROM users_of_this_app 
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()

        if user:
            id, password2, encrypted_totp_secret, totp_iv, totp_tag, topt_salt = user

            if check_password_hash(password2, password):
                try:
                    encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
                    totp_secret = decrypt_data_gcm(
                        encrypted_totp_secret,
                        encryption_key_totp,
                        totp_iv,
                        totp_tag
                    ).decode("utf-8")
                except Exception as e:
                    log_event("ERROR", "Topt_error"+str(e), id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))

                totp = pyotp.TOTP(totp_secret)
                if totp.verify(totp_token):
                    session["user"] = username
                    log_event("LOGGED_IN", "User_logged_in", id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Zalogowano pomyślnie!", "success") 
                    return redirect(url_for("dashboard"))
                else:
                    log_event("LOGIN_ERROR", "Wrong_login_data", id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))
            else:
                log_event("LOGIN_ERROR", "Wrong_login_data", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))
        else:
            log_event("LOGIN_ERROR", "Wrong_login_data", None, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
        
    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("login.html")

@app.route("/verify", methods=["POST"])
def verify():
    delay = 4
    start_time = time.time()
    totp_token = request.form.get("totp_token")
    password = request.form.get("password")
    username = request.form.get("username")

    ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

    if not totp_token or not re.match(r"^\d{6}$", totp_token):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Podano nieprawidłowy kod TOTP. Spróbuj ponownie.", "danger")
        return redirect(url_for("index"))
    
    time_window = 10 * 60
    max_failed_attempts = 3

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
                SELECT COUNT(*)
                FROM logs_of_this_app
                JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
                WHERE logs_of_this_app.event_type = ? 
                AND users_of_this_app.username = ? 
                AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
            """, ("TOPT_ERROR", username, f"-{time_window}")
            )
        failed_attempts = cursor.fetchone()
        failed_attempts = failed_attempts[0]

        if failed_attempts >= max_failed_attempts:
            log_event("TOPT_ERROR_MAX", "Too_many_topt_errors", id, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Zbyt wiele nieudanych prób. Spróbuj ponownie za kilka minut.", "danger")
            return redirect(url_for("index"))


        cursor.execute(
            """
            SELECT id, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, password, id
            FROM users_of_this_app 
            WHERE username = ?
            """,
            (username,)
        )
        user_data = cursor.fetchone()
        if not user_data:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))

    id, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, password2, id = user_data

    if not check_password_hash(password2, password):
        log_event("TOPT_ERROR", "Wrong_data_verify", id, ip_address)
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Niepoprawne hasło lub kod TOTP. Spróbuj ponownie.", "danger")
        return redirect(url_for("index"))

    try:
        encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
        totp_secret = decrypt_data_gcm(
            encrypted_totp_secret,
            encryption_key_totp,
            totp_iv,
            totp_tag
        ).decode("utf-8")
    except Exception as e:
        log_event("ERROR", "Topt_verification_error"+str(e), id, ip_address)
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
        return redirect(url_for("index"))

    totp = pyotp.TOTP(totp_secret)
    if totp.verify(totp_token):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        return redirect(url_for("index"))
    else:
        flash("Niepoprawny kod TOTP. Spróbuj ponownie.", "danger")
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        log_event("TOPT_ERROR", "Wrong_data_verify", id, ip_address)
        return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    delay = 5
    start_time = time.time()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

        if len(username) < 4:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Nazwa użytkownika musi mieć co najmniej 4 znaki.", "danger")
            return redirect(url_for("register"))

        if not re.match("^[a-zA-Z0-9]+$", username):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Nazwa użytkownika może zawierać tylko wielkie i małe litery oraz cyfry.", "danger")
            return redirect(url_for("register"))

        if len(password) < 10:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi mieć co najmniej 10 znaków.", "danger")
            return redirect(url_for("register"))

        if not re.search(r'[A-Z]', password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną wielką literę.", "danger")
            return redirect(url_for("register"))

        if not re.search(r'[a-z]', password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną małą literę.", "danger")
            return redirect(url_for("register"))

        if not re.search(r'\d', password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną cyfrę.", "danger")
            return redirect(url_for("register"))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jeden znak specjalny (!@#$%^&*(),.?\":{}|<>).", "danger")
            return redirect(url_for("register"))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Podano nieprawidłowy adres email.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256:300000', salt_length=16)
        try: 
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            salt = os.urandom(16)
            encryption_key = generate_key_from_password(password+secret_key, salt)
            encrypted_private_key, iv, tag = encrypt_data_gcm(private_key_bytes, encryption_key)

            totp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(totp_secret)

            uri = totp.provisioning_uri(name=username, issuer_name="MyApp")
            qr_image = qrcode.make(uri)
            buffered = io.BytesIO()
            qr_image.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            salt_topt = os.urandom(16)
            encryption_key_totp = generate_key_from_password(secret_key, salt_topt)
            cipher_totp_secret, totp_iv, totp_tag = encrypt_data_gcm(totp_secret.encode(), encryption_key_totp)
        except Exception as e:
            log_event("ERROR", "Registration_error"+str(e), None, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
            

        try:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users_of_this_app (
                        username,
                        created_at,
                        email, 
                        password, 
                        public_key, 
                        private_key, 
                        salt, 
                        iv, 
                        tag, 
                        encrypted_totp_secret, 
                        totp_iv, 
                        totp_tag, 
                        topt_salt
                    )
                    VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        email, 
                        hashed_password, 
                        public_key_bytes, 
                        encrypted_private_key, 
                        salt, 
                        iv, 
                        tag, 
                        cipher_totp_secret, 
                        totp_iv, 
                        totp_tag, 
                        salt_topt
                    )
                )
                conn.commit()
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Rejestracja zakończona sukcesem!", "success")
                log_event("REGISTRATION_SUCCESS", "Registration_success", None, ip_address)
                return render_template("two_factor.html", qr_code_base64=qr_code_base64)
        except sqlite3.IntegrityError:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Użytkownik o podanej nazwie lub adresie email już istnieje!", "danger")
            return redirect(url_for("index"))
        
    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    delay = 5
    start_time = time.time()

    user_ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

    if "user" in session:
        username = session['user']

        notes = []

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Pobierz user_id zalogowanego użytkownika
            cursor.execute("SELECT id FROM users_of_this_app WHERE username = ?", (username,))
            current_user = cursor.fetchone()
            current_user_id = current_user[0] if current_user else None
            
            cursor.execute(
                """
                SELECT message, created_at, signature, ip_address, author, id 
                FROM notes_of_this_app 
                ORDER BY created_at DESC
                """
            )
            user_notes = cursor.fetchall()
            for note in user_notes:
                message, created_at, signature, ip_address, author, note_id = note
                base_64 = base64.b64encode(message.encode('utf-8')).decode('utf-8')

                cursor.execute(
                    """
                    SELECT id, public_key 
                    FROM users_of_this_app 
                    WHERE username = ?
                    """, 
                    (author,)
                )
                author_data = cursor.fetchone()
                if not author_data:
                    log_event("ERROR", "Missing note author", None, ip_address)
                    continue

                id, public_key_bytes = author_data
                public_key = serialization.load_pem_public_key(
                    public_key_bytes,
                    backend=default_backend()
                )

                try:
                    signature_bytes = signature
                    public_key.verify(
                        signature_bytes,
                        message.encode(),
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    public_key = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    public_key = public_key.decode('utf-8')

                    signature = base64.b64encode(signature).decode('utf-8')
                    
                    # Pobierz liczbę lajków dla notatki
                    cursor.execute("SELECT COUNT(*) FROM likes_of_this_app WHERE note_id = ?", (note_id,))
                    like_count = cursor.fetchone()[0]
                    
                    # Sprawdź czy zalogowany użytkownik polubił tę notatkę
                    user_liked = False
                    if current_user_id:
                        cursor.execute(
                            "SELECT id FROM likes_of_this_app WHERE note_id = ? AND user_id = ?",
                            (note_id, current_user_id)
                        )
                        user_liked = cursor.fetchone() is not None

                    notes.append({
                    "id": note_id,
                    "public_key": public_key,
                    "message": message,
                    "author": author,
                    "created_at": created_at,
                    "signature": signature,
                    "ip_address": ip_address,
                    "base_64": base_64,
                    "likes": like_count,
                    "user_liked": user_liked
                })
                except Exception as e:
                    log_event("ERROR", "Loading_messages_error"+str(e), id, user_ip_address)
        log_event("NOTES_LOADED", "Notes_loaded", None, user_ip_address)
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        return render_template("hello.html", username=username, notes=notes)
    else:
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Musisz być zalogowany, aby zobaczyć tę stronę.", "warning")
        log_event("ERROR", "Someone_not_logged", None, user_ip_address)
        return redirect(url_for("index"))
    
@app.route("/page/<user>")
def user_page(user):
    delay = 3
    start_time = time.time()

    user_ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

    if "user" in session:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT message, created_at, signature, ip_address, author 
                FROM notes_of_this_app
                WHERE author = ?
                """, 
                (user,)
            )
            user_notes = cursor.fetchall()
        notes = []
        for note in user_notes:
            message, created_at, signature, ip_address, author = note

            cursor.execute(
                 """
                SELECT id, public_key 
                FROM users_of_this_app 
                WHERE username = ?
                """, 
                (author,)
            )
            author_data = cursor.fetchone()
            if not author_data:
                continue
            id, public_key_bytes = author_data
            public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )

            try:
                signature_bytes = signature
                public_key.verify(
                    signature_bytes,
                    message.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                public_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                public_key = public_key.decode('utf-8')

                signature = base64.b64encode(signature).decode('utf-8')
                message = bleach.clean(message, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
                base_64 = base64.b64encode(message.encode('utf-8')).decode('utf-8')

                notes.append({
                    "base_64":base_64,
                    "public_key": public_key,
                    "message": message,
                    "author": author,
                    "created_at": created_at,
                    "signature": signature,
                    "ip_address": ip_address
            })
            except Exception as e:
                log_event("ERROR", "Loading_messages_error"+str(e), id, ip_address)

        log_event("NOTES_LOADED", "Notes_loaded", id, user_ip_address)
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        return render_template("user_page.html",user=author, notes=notes)
    else:
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Musisz być zalogowany, aby zobaczyć tę stronę.", "warning")
        log_event("ERROR", "Someone_not_logged", None , user_ip_address)
        return redirect(url_for("index"))

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    delay = 5
    start_time = time.time()

    ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        totp_token = request.form["totp"]

        

        if not username or not password or not totp_token:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Wszystkie pola są wymagane!", "danger")
            return redirect(url_for("index"))
        
        time_window = 10 * 60
        max_failed_attempts = 3

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM logs_of_this_app
                JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
                WHERE logs_of_this_app.event_type = ? 
                AND users_of_this_app.username = ? 
                AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
            """, ("CHANGE_PASSWORD_ERROR", username, f"-{time_window}")
            )
            failed_attempts = cursor.fetchone()
            failed_attempts = failed_attempts[0]

            cursor.execute("""
                SELECT id
                FROM users_of_this_app
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            if user:
                id = user[0]
            else:
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            if failed_attempts >= max_failed_attempts:
                log_event("CHANGE_PASSWORD_ERROR_MAX", "Too_many_change_password_errors", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Zbyt wiele nieudanych prób. Spróbuj ponownie za kilka minut.", "danger")
                return redirect(url_for("index"))
            cursor.execute("""
                SELECT id , password, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, email 
                FROM users_of_this_app 
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()

        if user:
            id, password2, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, email = user

            if check_password_hash(password2, password):
                try:
                    encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
                    totp_secret = decrypt_data_gcm(
                        encrypted_totp_secret,
                        encryption_key_totp,
                        totp_iv,
                        totp_tag
                    ).decode("utf-8")
                except Exception:
                    log_event("ERROR", "Topt_verification_error", id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))

                totp = pyotp.TOTP(totp_secret)
                if totp.verify(totp_token):
                    salt = os.urandom(16)
                    change_token = serializer.dumps(email, salt=salt)
                    print("Wysyłam taki token: "+ str(change_token)+" na taki adres "+str(email))
                    with sqlite3.connect("users.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE users_of_this_app 
                            SET reset_password_token = ?, reset_password_salt = ?
                            WHERE username = ?
                        """, (change_token, salt, username))
                        conn.commit()
                    return render_template("change_verify.html")
                else:
                    log_event("CHANGE_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))
            else:
                log_event("CHANGE_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))
        else:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
        

    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("change.html")

@app.route("/change_verify", methods=["POST"])
def change_verify():
    delay = 4
    start_time = time.time()
    reset_token = request.form.get("reset_token")
    totp_token = request.form.get("totp")
    password = request.form.get("password")
    username = request.form.get("username")
    new_password = request.form.get("new_password")

    ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

    if not username or not password or not totp_token or not reset_token or not new_password:
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Wszystkie pola są wymagane!", "danger")
        return render_template("change_verify.html")
    
    if len(new_password) < 10:
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Hasło musi mieć co najmniej 10 znaków.", "danger")
        return render_template("change_verify.html")

    if not re.search(r'[A-Z]', new_password):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Hasło musi zawierać co najmniej jedną wielką literę.", "danger")
        return render_template("change_verify.html")

    if not re.search(r'[a-z]', new_password):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Hasło musi zawierać co najmniej jedną małą literę.", "danger")
        return render_template("change_verify.html")

    if not re.search(r'\d', new_password):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Hasło musi zawierać co najmniej jedną cyfrę.", "danger")
        return render_template("change_verify.html")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Hasło musi zawierać co najmniej jeden znak specjalny (!@#$%^&*(),.?\":{}|<>).", "danger")
        return render_template("change_verify.html")

    time_window = 10 * 60
    max_failed_attempts = 3

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM logs_of_this_app
            JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
            WHERE logs_of_this_app.event_type = ? 
            AND users_of_this_app.username = ? 
            AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
        """, ("CHANGE_PASSWORD_ERROR", username, f"-{time_window}")
        )
        failed_attempts = cursor.fetchone()
        failed_attempts = failed_attempts[0]

        cursor.execute("""
            SELECT id
            FROM users_of_this_app
            WHERE username = ?
        """, (username,))
        user = cursor.fetchone()
        if user:
            id = user[0]
        else:
            id = None

        if failed_attempts >= max_failed_attempts:
            log_event("CHANGE_PASSWORD_ERROR_MAX", "Too_many_change_password_errors", id, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Zbyt wiele nieudanych prób. Spróbuj ponownie za kilka minut.", "danger")
            return redirect(url_for("index"))
        cursor.execute("""
            SELECT id , password, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, reset_password_salt, email
            FROM users_of_this_app 
            WHERE username = ?
        """, (username,))
        user = cursor.fetchone()

    if user:
        id, password2, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, reset_password_salt, email = user

        if check_password_hash(password2, password):
            try:
                encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
                totp_secret = decrypt_data_gcm(
                    encrypted_totp_secret,
                    encryption_key_totp,
                    totp_iv,
                    totp_tag
                ).decode("utf-8")
            except Exception as e:
                log_event("ERROR", "Topt_verification_error"+str(e), id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            totp = pyotp.TOTP(totp_secret)
            if totp.verify(totp_token):
                try:
                    what = serializer.loads(reset_token, salt=reset_password_salt, max_age=600)

                    if email == what:
                        cursor.execute("SELECT private_key, iv, tag, salt FROM users_of_this_app WHERE username = ?", (username,))
                        user_data = cursor.fetchone()

                        encrypted_private_key, iv, tag, salt = user_data[0], user_data[1], user_data[2], user_data[3]
                        try:
                            decryption_key = generate_key_from_password(password + secret_key, salt)
                            private_key_bytes = decrypt_data_gcm(encrypted_private_key, decryption_key, iv, tag)
                        except Exception as e:
                            if(time.time()-start_time<delay):
                                time.sleep(delay-(start_time-time.time()))
                            flash("Błąd podczas odszyfrowywania klucza prywatnego.", "danger")
                            return redirect(url_for("index"))

                        private_key = serialization.load_pem_private_key(
                            private_key_bytes,
                            password=None,
                            backend=default_backend()
                        )

                        private_key_bytes_to_encrypt = private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption()
                        )

                        salt = os.urandom(16)

                        encryption_key = generate_key_from_password(new_password + secret_key, salt)
                        encrypted_private_key, iv, tag = encrypt_data_gcm(private_key_bytes_to_encrypt, encryption_key)

                        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256:300000', salt_length=16)

                        with sqlite3.connect("users.db") as conn:
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE users_of_this_app 
                                SET password = ?, private_key = ?, salt = ?, iv = ?, tag = ?
                                WHERE username = ?
                            """, (hashed_password, encrypted_private_key, salt, iv, tag, username))
                            conn.commit()

                        flash("Hasło zmienione", "success")
                        if(time.time()-start_time<delay):
                            time.sleep(delay-(start_time-time.time()))
                        return redirect(url_for("index"))
                    else:
                        log_event("CHANGE_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                        if(time.time()-start_time<delay):
                            time.sleep(delay-(start_time-time.time()))
                        flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                        return redirect(url_for("index"))
                    
                except Exception as e:
                    log_event("ERROR", "Unexpected_error_change_password "+str(e), id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Wystąpił nieoczekiwany błąd. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))
            else:
                log_event("CHANGE_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))
        else:
            log_event("CHANGE_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
    else:
        if(time.time()-start_time<delay):
            time.sleep(delay-(start_time-time.time()))
        flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
        return redirect(url_for("index"))
    

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    delay = 5
    start_time = time.time()
    if request.method == "POST":
        username = request.form["username"]
        totp_token = request.form["totp"]

        ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

        if not username or not totp_token:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Wszystkie pola są wymagane!", "danger")
            return redirect(url_for("index"))
        
        time_window = 10 * 60
        max_failed_attempts = 3

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM logs_of_this_app
                JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
                WHERE logs_of_this_app.event_type = ? 
                AND users_of_this_app.username = ? 
                AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
            """, ("RESET_PASSWORD_ERROR", username, f"-{time_window}")
            )
            failed_attempts = cursor.fetchone()
            failed_attempts = failed_attempts[0]

            cursor.execute("""
                SELECT id
                FROM users_of_this_app
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            if user:
                id = user[0]
            else:
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            if failed_attempts >= max_failed_attempts:
                log_event("RESET_PASSWORD_ERROR_MAX", "Too_many_reset_password_errors", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Zbyt wiele nieudanych prób. Spróbuj ponownie za kilka minut.", "danger")
                return redirect(url_for("index"))
            cursor.execute("""
                SELECT id , encrypted_totp_secret, totp_iv, totp_tag, topt_salt, email 
                FROM users_of_this_app 
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()

        if user:
            id, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, email = user
            try:
                encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
                totp_secret = decrypt_data_gcm(
                    encrypted_totp_secret,
                    encryption_key_totp,
                    totp_iv,
                    totp_tag
                ).decode("utf-8")
            except Exception:
                log_event("ERROR", "Topt_verification_error", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            totp = pyotp.TOTP(totp_secret)
            if totp.verify(totp_token):
                salt = os.urandom(16)
                change_token = serializer.dumps(email, salt=salt)
                print("Wysyłam taki token: "+ str(change_token)+" na taki adres "+str(email)+" z takim linkiem: /reset_verify/"+str(change_token))
                with sqlite3.connect("users.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                            UPDATE users_of_this_app 
                            SET reset_password_token = ?, reset_password_salt = ?
                            WHERE username = ?
                        """, (change_token, salt, username))
                    conn.commit()
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Wysłano link do zmiany hasła na maila", "success")
                return redirect(url_for("index"))
            else:
                log_event("RESET_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))
        else:
            if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("reset.html")


@app.route("/reset_verify/<change_token>", methods=['GET', 'POST'])
def reset_verify(change_token):
    delay = 3
    start_time = time.time()
    if request.method == "POST":
        reset_token = request.form.get("reset_token")
        totp_token = request.form.get("totp")
        username = request.form.get("username")
        new_password = request.form.get("new_password")

        ip_address = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))

        if not username or not totp_token or not reset_token or not new_password:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Wszystkie pola są wymagane!", "danger")
            return redirect(url_for("index"))
        
        if len(new_password) < 10:
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi mieć co najmniej 10 znaków.", "danger")
            return redirect(url_for("index"))

        if not re.search(r'[A-Z]', new_password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną wielką literę.", "danger")
            return redirect(url_for("index"))

        if not re.search(r'[a-z]', new_password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną małą literę.", "danger")
            return redirect(url_for("index"))

        if not re.search(r'\d', new_password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jedną cyfrę.", "danger")
            return redirect(url_for("index"))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Hasło musi zawierać co najmniej jeden znak specjalny (!@#$%^&*(),.?\":{}|<>).", "danger")
            return redirect(url_for("index"))

        time_window = 10 * 60
        max_failed_attempts = 3

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM logs_of_this_app
                JOIN users_of_this_app ON logs_of_this_app.user_id = users_of_this_app.id
                WHERE logs_of_this_app.event_type = ? 
                AND users_of_this_app.username = ? 
                AND logs_of_this_app.timestamp > DATETIME('now', ? || ' seconds')
            """, ("RESET_PASSWORD_ERROR", username, f"-{time_window}")
            )
            failed_attempts = cursor.fetchone()
            failed_attempts = failed_attempts[0]

            cursor.execute("""
                SELECT id
                FROM users_of_this_app
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            if user:
                id = user[0]
            else:
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            if failed_attempts >= max_failed_attempts:
                log_event("RESET_PASSWORD_ERROR_MAX", "Too_many_change_password_errors", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Zbyt wiele nieudanych prób. Spróbuj ponownie za kilka minut.", "danger")
                return redirect(url_for("index"))
            cursor.execute("""
                SELECT id, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, reset_password_salt, email
                FROM users_of_this_app 
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()

        if user:
            id, encrypted_totp_secret, totp_iv, totp_tag, topt_salt, reset_password_salt, email = user

            try:
                encryption_key_totp = generate_key_from_password(secret_key, topt_salt)
                totp_secret = decrypt_data_gcm(
                    encrypted_totp_secret,
                    encryption_key_totp,
                    totp_iv,
                    totp_tag
                ).decode("utf-8")
            except Exception as e:
                log_event("ERROR", "Topt_verification_error"+str(e), id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Wystąpił błąd podczas weryfikacji. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))

            totp = pyotp.TOTP(totp_secret)
            if totp.verify(totp_token):
                try:
                    what = serializer.loads(reset_token, salt=reset_password_salt, max_age=600)

                    if email == what:
                        private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=2048,
                        backend=default_backend()
                        )
                        public_key = private_key.public_key()

                        private_key_bytes = private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption()
                        )

                        public_key_bytes = public_key.public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                        )

                        salt = os.urandom(16)
                        encryption_key = generate_key_from_password(new_password+secret_key, salt)
                        encrypted_private_key, iv, tag = encrypt_data_gcm(private_key_bytes, encryption_key)

                        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256:300000', salt_length=16)

                        with sqlite3.connect("users.db") as conn:
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE users_of_this_app 
                                SET password = ?, public_key = ?, private_key = ?, salt = ?, iv = ?, tag = ? 
                                WHERE username = ?
                            """, (hashed_password, public_key_bytes, encrypted_private_key, salt, iv, tag, username))
                            conn.commit()

                            cursor.execute(
                                """
                                SELECT id, message
                                FROM notes_of_this_app
                                WHERE author = ?
                                """, 
                                (username,)
                            )
                            user_notes = cursor.fetchall()
                            for note in user_notes:
                                note_id, message = note
                                safe_message = bleach.clean(message, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

                                signature = private_key.sign(
                                    safe_message.encode(),
                                    padding.PSS(
                                        mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.MAX_LENGTH
                                    ),
                                    hashes.SHA256()
                                )
                                cursor.execute("""
                                UPDATE notes_of_this_app 
                                SET message = ?, signature = ? 
                                WHERE id = ?
                                """, (safe_message, signature, note_id))
                            conn.commit()

                        if(time.time()-start_time<delay):
                            time.sleep(delay-(start_time-time.time()))
                        flash("Hasło zmienione", "success")
                        return redirect(url_for("index"))
                    else:
                        log_event("RESET_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                        if(time.time()-start_time<delay):
                            time.sleep(delay-(start_time-time.time()))
                        flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                        return redirect(url_for("index"))

                except Exception as e:
                    log_event("ERROR", "Unexpected_error_change_password "+str(e), id, ip_address)
                    if(time.time()-start_time<delay):
                        time.sleep(delay-(start_time-time.time()))
                    flash("Wystąpił nieoczekiwany błąd. Spróbuj ponownie.", "danger")
                    return redirect(url_for("index"))
            else:
                log_event("RESET_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
                if(time.time()-start_time<delay):
                    time.sleep(delay-(start_time-time.time()))
                flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
                return redirect(url_for("index"))
        else:
            log_event("RESET_PASSWORD_ERROR", "Wrong_data_change_password", id, ip_address)
            if(time.time()-start_time<delay):
                time.sleep(delay-(start_time-time.time()))
            flash("Niepoprawne dane. Spróbuj ponownie.", "danger")
            return redirect(url_for("index"))
        

    if(time.time()-start_time<delay):
        time.sleep(delay-(start_time-time.time()))
    return render_template("reset_verify.html")

@app.route("/logout", methods=["POST"])
def logout():
    start_time = time.time()
    session.pop("user", None)
    if(time.time()-start_time<1):
        time.sleep(1-(start_time-time.time()))
    flash("Wylogowano pomyślnie.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
