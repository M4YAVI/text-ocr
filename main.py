from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import pytesseract
from PIL import Image
import io
import os
import shutil
import sys

# Configure Tesseract Path for Windows
if sys.platform.startswith("win"):
    tesseract_cmd = shutil.which("tesseract")
    if not tesseract_cmd:
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Users\sange\AppData\Local\Tesseract-OCR\tesseract.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <title>OCR API Tester</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
            .container { border: 2px dashed #ccc; padding: 2rem; text-align: center; border-radius: 8px; }
            #preview { max-width: 100%; margin-top: 1rem; border-radius: 4px; }
            #result { white-space: pre-wrap; background: #f5f5f5; padding: 1rem; margin-top: 1rem; border-radius: 4px; display: none; text-align: left; }
            button { background: #000; color: #fff; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin-top: 1rem; }
            button:disabled { opacity: 0.5; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <h1>Image-to-Text OCR API</h1>
        <div class="container">
            <input type="file" id="fileInput" accept="image/png, image/jpeg">
            <br>
            <img id="preview">
            <br>
            <button onclick="uploadImage()" id="uploadBtn">Extract Text</button>
        </div>
        <div id="result"></div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const preview = document.getElementById('preview');
            const result = document.getElementById('result');
            const uploadBtn = document.getElementById('uploadBtn');

            fileInput.onchange = () => {
                const file = fileInput.files[0];
                if (file) {
                    preview.src = URL.createObjectURL(file);
                }
            };

            async function uploadImage() {
                const file = fileInput.files[0];
                if (!file) return alert('Please select an image first');

                uploadBtn.disabled = true;
                uploadBtn.innerText = 'Processing...';
                result.style.display = 'none';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/ocr/image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        result.style.display = 'block';
                        result.textContent = JSON.stringify(data, null, 2);
                    } else {
                        alert('Error: ' + (data.detail || 'Unknown error'));
                    }
                } catch (e) {
                    alert('Error: ' + e.message);
                } finally {
                    uploadBtn.disabled = false;
                    uploadBtn.innerText = 'Extract Text';
                }
            }
        </script>
    </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def main():
    return HTML_CONTENT

@app.post("/ocr/image")
async def extract_text(file: UploadFile = File(...)):
    # 1. Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG and PNG are supported."
        )
    
    try:
        # 2. Open image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 3. Preprocess (Convert to grayscale)
        image = image.convert("L")
        
        # 4. Run Tesseract
        text = pytesseract.image_to_string(image)
        
        return {
            "filename": file.filename,
            "text": text.strip()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
