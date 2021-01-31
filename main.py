import fitz
import glob

filepath = "resume/*.pdf"
pdfs = glob.glob(filepath)
for pdfFile in pdfs:
    doc = fitz.open(pdfFile)
