from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import img2pdf
from PIL import Image
import io

app = FastAPI()

@app.get("/")
async def hello() -> str:
    return {"message" : "API is running"}

@app.post("/convert-to-pdf/")
async def convert_to_pdf(file: UploadFile = File(...), target: str = "pdf"):
    # Read bytes
    content = await file.read()

    if file.content_type.startswith("image/"):
        # IMAGE → PDF
        try:
            image = Image.open(io.BytesIO(content))
            buf = io.BytesIO()
            buf.write(img2pdf.convert(image.filename or "image"))
            buf.seek(0)
            return StreamingResponse(buf, media_type="application/pdf")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif file.filename.lower().endswith((".docx", ".doc")):
        # WORD → PDF (simple placeholder — you can refine)
        try:
            # For Word, you could use an external conversion
            raise NotImplementedError("Word → PDF requires external converter")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


