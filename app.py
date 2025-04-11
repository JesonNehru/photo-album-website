from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Fake user database (for testing)
USERS = {
    'admin': 'admin123'  # username: password
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['is_admin'] = True
            return redirect(url_for('gallery'))
        else:
            error = "Invalid credentials"
    return render_template('login.html', error=error)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    photos = os.listdir(UPLOAD_FOLDER)
    is_admin = session.get('is_admin', False)
    return render_template('gallery.html', photos=photos, is_admin=is_admin)

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('is_admin'):
        return "Unauthorized", 403
    if 'photo' not in request.files:
        return "No file part", 400
    file = request.files['photo']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"  # Optional for uniqueness
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        return redirect(url_for('gallery'))
    else:
        return "Invalid file type", 400

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
