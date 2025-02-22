from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import shutil
from werkzeug.utils import secure_filename
from image_operations import encrypt_file, decrypt_file
from generate_pdf import generate_pdf
from extract_images_from_pdf import extract_images_from_pdf

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS_TEXT = {'txt', 'md', 'py'}
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/enimg', exist_ok=True)  # Create static directory for encrypted images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, file_type):
    if file_type == 'text':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_TEXT
    elif file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE
    return False

@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Dummy login (replace with real authentication)
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/encrypt', methods=['GET', 'POST'])
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files:
            flash('No files selected', 'error')
            return redirect(request.url)
        
        encrypted_images = []
        for file in files:
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename, 'text'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the file (encrypt)
                encrypted_image = encrypt_file(filepath)
                
                # Ensure the static/enimg directory exists
                os.makedirs('static/enimg', exist_ok=True)
                
                # Move the image to the static folder with proper path handling
                filename = os.path.basename(encrypted_image)
                static_image_path = os.path.join('static', 'enimg', filename)
                
                if not os.path.exists(static_image_path):
                    shutil.copy(encrypted_image, static_image_path)
                
                encrypted_images.append(static_image_path)
        
        # Generate PDF with encrypted images
        generate_pdf(encrypted_images)
        
        return render_template('encrypt_success.html', 
                               filename="encrypted_images.pdf")
    
    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, 'pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract images from PDF
            extracted_images = extract_images_from_pdf(filepath, 'temp')
            
            decrypted_files = []
            for image_path in extracted_images:
                # Process the image (decrypt)
                decrypted_file = decrypt_file(image_path)
                decrypted_files.append(decrypted_file)
            
            # Provide a zip file with decrypted files
            zip_path = create_zip(decrypted_files)
            
            return render_template('decrypt_success.html', 
                                   content="Decryption successful",
                                   filename="decrypted_files.zip",
                                   zip_path=zip_path)
    
    return render_template('decrypt.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)