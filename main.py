from fastapi.responses import FileResponse, PlainTextResponse

# ... (imports remain the same) ...

app = FastAPI()

@app.get("/")
async def main():
    return FileResponse("index.html")

@app.post("/ocr/image", response_class=PlainTextResponse)
# ... (rest of the code) ...

@app.post("/ocr/image", response_class=PlainTextResponse)
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
        
        return text.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
