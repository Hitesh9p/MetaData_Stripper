# app.py
from flask import Flask, render_template_string, request, send_file, flash, redirect, url_for
from PIL import Image
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Change in production!

# Supported image formats
SUPPORTED_FORMATS = {'jpg', 'jpeg', 'png', 'webp'}

# Temporary directory for processed files
TEMP_DIR = tempfile.mkdtemp(prefix='image_cleaner_')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route: Handle image uploads and process them
    Returns: Rendered HTML template with upload form or download links
    """
    if request.method == 'POST':
        # Check if files were uploaded
        if 'images' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        
        files = request.files.getlist('images')
        
        # Validate and process files
        valid_files = []
        for file in files:
            if file.filename == '':
                continue
            if file and allowed_file(file.filename):
                valid_files.append(file)
            elif file.filename:
                flash(f'Unsupported file format: {file.filename}')
        
        if not valid_files:
            flash('No valid image files uploaded')
            return redirect(request.url)
        
        # Process each image
        cleaned_files = []
        for file in valid_files:
            try:
                # Secure filename and determine format
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                
                # Open image with PIL
                image = Image.open(file.stream)
                
                # Create a new image without metadata
                # This approach recreates the image, effectively removing all metadata
                if image.mode in ('RGBA', 'LA', 'RGBX'):
                    # Preserve alpha channel if present
                    new_image = Image.new(image.mode, image.size)
                    new_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                else:
                    # Standard RGB or L (grayscale)
                    new_image = Image.new(image.mode, image.size)
                    new_image.paste(image)
                
                # Save to BytesIO object with original format
                img_io = BytesIO()
                
                # Preserve quality for JPEG
                save_kwargs = {}
                if ext in ('jpg', 'jpeg'):
                    save_kwargs['quality'] = 95  # High quality, adjust as needed
                    save_kwargs['optimize'] = True
                
                # Ensure format is properly specified
                pil_format = 'JPEG' if ext in ('jpg', 'jpeg') else ext.upper()
                new_image.save(img_io, format=pil_format, **save_kwargs)
                img_io.seek(0)
                
                # Generate cleaned filename
                clean_filename = f"cleaned_{filename}"
                cleaned_files.append((img_io, clean_filename))
                
                logger.info(f"Successfully processed {filename}")
                
            except Exception as e:
                flash(f"Error processing {file.filename}: {str(e)}")
                logger.error(f"Error processing {file.filename}: {str(e)}")
        
        # If we have cleaned files, prepare for download
        if cleaned_files:
            # Single file: direct download
            if len(cleaned_files) == 1:
                img_io, filename = cleaned_files[0]
                return send_file(
                    img_io,
                    mimetype=f'image/{ext}',
                    as_attachment=True,
                    download_name=filename
                )
            # Multiple files: create ZIP archive
            else:
                # Create a temporary ZIP file
                import zipfile
                zip_io = BytesIO()
                with zipfile.ZipFile(zip_io, 'w') as zf:
                    for img_io, filename in cleaned_files:
                        zf.writestr(filename, img_io.getvalue())
                zip_io.seek(0)
                
                return send_file(
                    zip_io,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='cleaned_images.zip'
                )
    
    # Render upload form (GET request or after processing)
    return render_template_string(HTML_TEMPLATE)

def allowed_file(filename):
    """
    Check if uploaded file has a supported extension
    Args:
        filename (str): Name of the uploaded file
    Returns:
        bool: True if file extension is supported
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_FORMATS

@app.teardown_appcontext
def cleanup(exception):
    """
    Clean up temporary directory when app shuts down
    """
    pass  # We'll manually clean up in exit handler

def cleanup_temp_dir():
    """
    Remove temporary directory and its contents
    """
    try:
        shutil.rmtree(TEMP_DIR)
        logger.info(f"Cleaned up temporary directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary directory: {e}")

import atexit
atexit.register(cleanup_temp_dir)

# HTML Template for the upload interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Metadata Remover</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 3px dashed #ccc;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background-color: #fafafa;
            transition: border-color 0.3s;
        }
        .upload-area:hover {
            border-color: #999;
        }
        .upload-area.active {
            border-color: #4CAF50;
            background-color: #f0fff0;
        }
        input[type="file"] {
            display: none;
        }
        .upload-btn {
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .upload-btn:hover {
            background-color: #45a049;
        }
        .submit-btn {
            background-color: #008CBA;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
            margin-top: 20px;
        }
        .submit-btn:hover {
            background-color: #007B9A;
        }
        .messages {
            margin: 20px 0;
            padding: 10px;
            border-radius: 4px;
        }
        .alert {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        footer {
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .file-list {
            margin: 15px 0;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
            max-height: 150px;
            overflow-y: auto;
        }
        .instructions {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            border: 1px solid #fadeb6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📷 Image Metadata Remover</h1>
        
        <div class="instructions">
            <strong>Instructions:</strong> Upload your image(s) and download clean versions with all metadata removed.
            Supported formats: JPG, JPEG, PNG, WEBP.
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="messages">
                    {% for category, message in messages %}
                        <div class="alert">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <form method="POST" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-area" id="dropZone">
                <p>Drag & drop images here or</p>
                <label for="imageUpload" class="upload-btn">Choose Files</label>
                <input type="file" id="imageUpload" name="images" accept=".jpg,.jpeg,.png,.webp" multiple>
                <p><small>Supports JPG, JPEG, PNG, WEBP formats</small></p>
                <div class="file-list" id="fileList" style="display:none;"></div>
            </div>
            <button type="submit" class="submit-btn">Remove Metadata</button>
        </form>
    </div>
    
    <footer>
        &copy; 2025 Image Metadata Remover | Your privacy matters - all processing happens server-side and files are deleted after processing
    </footer>
    
    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('imageUpload');
        const fileList = document.getElementById('fileList');
        
        // Handle file selection via button
        fileInput.addEventListener('change', function(e) {
            updateFileList(this.files);
        });
        
        // Handle drag and drop
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('active');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('active');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('active');
            
            // Trigger file input change
            const dt = e.dataTransfer;
            const files = dt.files;
            
            // Create DataTransfer object to simulate file input
            const input = document.getElementById('imageUpload');
            const dataTransfer = new DataTransfer();
            
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            
            input.files = dataTransfer.files;
            updateFileList(files);
        });
        
        function updateFileList(files) {
            if (files.length === 0) return;
            
            fileList.innerHTML = '';
            fileList.style.display = 'block';
            
            const heading = document.createElement('p');
            heading.innerHTML = '<strong>Selected files:</strong>';
            fileList.appendChild(heading);
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const fileItem = document.createElement('p');
                fileItem.innerHTML = `• ${file.name} (${formatFileSize(file.size)})`;
                fileList.appendChild(fileItem);
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("Starting Image Metadata Remover...")
    print("Visit http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Run Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cleanup_temp_dir()