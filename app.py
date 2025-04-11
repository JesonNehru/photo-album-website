from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

# Blob storage setup
AZURE_STORAGE_CONNECTION_STRING = 'your_connection_string'  # Replace with your connection string
CONTAINER_NAME = 'your-container-name'  # Replace with your container name

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Fake user database (for testing)
USERS = {
    'admin': 'admin123'  # username: password
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload to Azure Blob Storage
def upload_to_blob_storage(file):
    # Connect to Azure Blob Service
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4().hex}.{file.filename.split('.')[-1]}"
    
    # Upload the file to Blob Storage
    blob_client = container_client.get_blob_client(unique_filename)
    blob_client.upload_blob(file, overwrite=True)  # Overwrite if file already exists
    
    return unique_filename  # Return the blob's name or URL

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
    # Get list of uploaded files in Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = container_client.list_blobs()
    photos = [blob.name for blob in blobs]  # Get blob names
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
        # Upload the file to Azure Blob Storage
        unique_filename = upload_to_blob_storage(file)
        return redirect(url_for('gallery'))
    else:
        return "Invalid file type", 400

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(filename)
    try:
        blob_client.delete_blob()  # Delete the blob from Azure Blob Storage
    except Exception as e:
        return f"Error deleting file: {e}", 500
    return redirect(url_for('gallery'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
