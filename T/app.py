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
    return render_template('verify.html', username=session['username'])

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

@app.route('/download_signature/<filename>')
def download_signature(filename):
    sig_path = os.path.join(SIGNATURE_FOLDER, filename)
    return send_file(sig_path, as_attachment=True)

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

    # Upload file và chữ ký từ người dùng
    file = request.files['file']
    signature_file = request.files['signature']

    if not file or not signature_file:
        return render_template('verify.html', username=session['username'], verification_result=False)

    # Lưu tạm file và chữ ký
    temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    temp_sig_path = os.path.join(UPLOAD_FOLDER, signature_file.filename)

    file.save(temp_file_path)
    signature_file.save(temp_sig_path)

    # Xác minh bằng public key
    public_key_path = os.path.join(KEY_FOLDER, 'public.pem')
    valid = verify_signature(temp_file_path, temp_sig_path, public_key_path)

    return render_template('verify.html', username=session['username'], verification_result=valid)

if __name__ == '__main__':
    app.run(debug=True)
