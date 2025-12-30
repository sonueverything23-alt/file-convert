from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import img2pdf
import io

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "API is running"}

@app.post("/convert-to-pdf/")
async def convert_to_pdf(file: UploadFile = File(...)):
    content = await file.read()

    # IMAGE → PDF
    if file.content_type and file.content_type.startswith("image/"):
        try:
            pdf_bytes = img2pdf.convert(content)
            buf = io.BytesIO(pdf_bytes)

            return StreamingResponse(
                buf,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=converted.pdf"
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # WORD → PDF (not implemented)
    elif file.filename.lower().endswith((".docx", ".doc")):
        raise HTTPException(
            status_code=501,
            detail="Word to PDF conversion not implemented yet",
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
