from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Set up the upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulate login role (for now)
IS_ADMIN = True  # Change to False to simulate normal user

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Gallery route
@app.route('/gallery')
def gallery():
    photos = os.listdir(UPLOAD_FOLDER)
    return render_template('gallery.html', photos=photos, is_admin=IS_ADMIN)

# Upload route to handle photo uploads
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['photo']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for('gallery'))

# Delete route to handle photo deletion (for admins only)
@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if not IS_ADMIN:
        return "Unauthorized", 403
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True)
