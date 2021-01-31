import fitz
import glob

filepath = "resume/*.pdf"
pdfs = glob.glob(filepath)
for pdfFile in pdfs:
    text = ""
    with fitz.open(pdfFile) as doc:
        for page in doc:
            text += page.getText()
    print(text)
