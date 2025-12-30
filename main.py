from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import img2pdf
import io
import pypdf
from PIL import Image

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "API is running"}

@app.post("/convert-to-pdf/")
async def convert_to_pdf(files: list[UploadFile] = File(...)):
    pdf_buffers = []

    # Loop through each uploaded file
    for file in files:
        content = await file.read()

        # IMAGE → PDF
        if file.content_type and file.content_type.startswith("image/"):
            try:
                # Convert the raw image bytes to PDF bytes
                pdf_bytes = img2pdf.convert(content)
                buf = io.BytesIO(pdf_bytes)
                pdf_buffers.append(buf)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image convert error: {str(e)}")

        # ALREADY PDF → just add
        elif file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            buf = io.BytesIO(content)
            pdf_buffers.append(buf)

        else:
            # Unsupported file format
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")

    # If only 1 PDF buffer, return it directly
    if len(pdf_buffers) == 1:
        buf = pdf_buffers[0]
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=converted.pdf"},
        )

    # If multiple files → merge into one PDF
    merger = pypdf.PdfWriter()
    for buf in pdf_buffers:
        buf.seek(0)
        reader = pypdf.PdfReader(buf)
        merger.append(reader)

    result_buf = io.BytesIO()
    merger.write(result_buf)
    result_buf.seek(0)

    return StreamingResponse(
        result_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )
