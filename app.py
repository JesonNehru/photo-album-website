from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fake user database (for testing)
USERS = {
    'admin': 'admin123'  # username: password
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['is_admin'] = True
            return redirect(url_for('gallery'))
        else:
            return "Invalid credentials", 403
    return render_template('login.html')

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
    file = request.files['photo']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for('gallery'))

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True)
