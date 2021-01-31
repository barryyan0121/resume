import fitz
import glob

filepath = "resume/*.pdf"
pdfs = glob.glob(filepath)
for pdfFile in pdfs:
<<<<<<< HEAD
    text = ""
    with fitz.open(pdfFile) as doc:
        for page in doc:
            text += page.getText()
    print(text)
=======
    doc = fitz.open(pdfFile)
>>>>>>> 467552ae0d818d515ad1136e4a08775dbc3bc3e3
