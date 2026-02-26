# 📷 Pure-Image Metadata Remover

A lightweight Flask-based web application that strips 100% of metadata from your images. 

Unlike many online tools that simply "hide" or "delete" specific EXIF tags, this tool **reconstructs** the image by extracting raw pixel data and pasting it onto a brand-new canvas. This process ensures that no hidden JSON data, thumbnails, or hardware signatures remain in the final file.

## ✨ Key Features
* **Total Privacy:** Recreates images from raw pixels to guarantee no metadata leakage.
* **Bulk Processing:** Upload multiple images at once and receive them back in a single `.zip` file.
* **Format Support:** Works with JPG, JPEG, PNG, and WEBP.
* **Memory Efficient:** Uses `BytesIO` for in-memory processing to avoid unnecessary disk writes.
* **Clean UI:** Simple drag-and-drop interface.



## 🚀 Why this is different?
Standard metadata removers often leave behind:
1.  **Software Signatures:** (e.g., "Adobe Photoshop 2024")
2.  **Thumbnail Data:** Hidden mini-versions of the original photo.
3.  **Padding/Null Data:** Hidden JSON strings in the file header.

**This tool prevents that.** By using the `Image.new()` and `paste()` method, we ensure only the visible pixels are saved.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hitesh9p/MetaData_Stripper
   cd MetaData_Stripper

2. **Install dependencies:**
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt   
3. **Run the app:**
    python app.py
4 **Visit broswer**
    Visit http://localhost:5000 in your browser.



🛡️ Privacy Note
This application is designed to be run locally. No images are stored permanently; they are processed in-memory or in temporary directories that are cleared immediately after the session ends.

---

### A few suggestions for your GitHub:

* **Requirements File:** Create a file named `requirements.txt` and add these lines so others can install it easily:
    ```text
    Flask==3.0.0
    Pillow==10.1.0
    Werkzeug==3.0.1
    ```
* **Deployment:** If you really want it online, I recommend **Render.com**. It’s free for small Python apps and connects directly to your GitHub.

Would you like me to help you create the `requirements.txt` file or explain how to set this up on Render?
