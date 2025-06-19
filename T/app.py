from flask import Flask, render_template, request, send_file, redirect, session, url_for
import os
import shutil
from utils import generate_rsa_keys, sign_file, verify_signature

app = Flask(__name__)
app.secret_key = 'rsa_demo_secret_key'

UPLOAD_FOLDER = 'uploads'
SIGNATURE_FOLDER = 'signatures'
KEY_FOLDER = 'rsa_keys'
STATIC_KEY_FOLDER = os.path.join('static', 'rsa_keys')
RECEIVED_FOLDER = 'received'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNATURE_FOLDER, exist_ok=True)
os.makedirs(KEY_FOLDER, exist_ok=True)
os.makedirs(STATIC_KEY_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username.strip():
            session['username'] = username.strip()
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/generate', methods=['GET'])
def generate_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('generate.html', username=session['username'])

@app.route('/sign', methods=['GET'])
def sign_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('sign.html', username=session['username'])

@app.route('/verify', methods=['GET'])
def verify_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = session['username']
    inbox_path = os.path.join(RECEIVED_FOLDER, user)
    files = []
    if os.path.exists(inbox_path):
        for f in os.listdir(inbox_path):
            if not f.endswith('.sig'):
                sig = f + '.sig'
                if os.path.exists(os.path.join(inbox_path, sig)):
                    files.append((f, sig))
    return render_template('verify.html', username=user, files=files)

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    if 'username' not in session:
        return redirect(url_for('login'))

    generate_rsa_keys(KEY_FOLDER)
    shutil.copy(os.path.join(KEY_FOLDER, 'public.pem'), STATIC_KEY_FOLDER)
    shutil.copy(os.path.join(KEY_FOLDER, 'private.pem'), STATIC_KEY_FOLDER)
    return render_template('generate.html',
                           public_key_path='rsa_keys/public.pem',
                           private_key_path='rsa_keys/private.pem',
                           username=session['username'])

@app.route('/sign_file', methods=['POST'])
def sign_file_route():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    signature_path = os.path.join(SIGNATURE_FOLDER, filename + '.sig')
    sign_file(filepath, os.path.join(KEY_FOLDER, 'private.pem'), signature_path)

    with open(signature_path, 'rb') as f:
        signature_data = f.read()

    signature_hex = signature_data.hex()
    return render_template('confirmation.html',
                           filename=filename,
                           signature=signature_hex,
                           username=session['username'])

@app.route('/send_signed_file', methods=['POST'])
def send_signed_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    sender = session['username']
    recipient = request.form['recipient']
    filename = request.form['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    sig_path = os.path.join(SIGNATURE_FOLDER, filename + '.sig')

    recipient_folder = os.path.join(RECEIVED_FOLDER, recipient)
    os.makedirs(recipient_folder, exist_ok=True)

    shutil.copy(file_path, os.path.join(recipient_folder, filename))
    shutil.copy(sig_path, os.path.join(recipient_folder, filename + ".sig"))

    return f"✅ Đã gửi file '{filename}' từ {sender} đến {recipient}."

@app.route('/verify_file', methods=['POST'])
def verify_file_route():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.form['file_path']
    user = session['username']
    base_path = os.path.join(RECEIVED_FOLDER, user)

    filepath = os.path.join(base_path, file)
    sigpath = filepath + '.sig'

    public_key_path = os.path.join(KEY_FOLDER, 'public.pem')
    valid = verify_signature(filepath, sigpath, public_key_path)

    if valid:
        return send_file(filepath, as_attachment=True)
    return render_template('verify.html', username=user, verification_result=False)
if __name__ == '__main__':
    app.run(debug=True)
