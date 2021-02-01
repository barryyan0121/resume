import fitz
import glob
import os
import docx2txt
import textract
from spacy.pipeline import EntityRuler
import spacy
nlp = spacy.load("en_core_web_lg")
ruler = EntityRuler(nlp)
patterns = [{"label": "ORG", "pattern": [{"LOWER": "ltd"}, {"LOWER": "llc"}, {"LOWER": "corp"}, {"LOWER": "inc"}]},
            {"label": "DATE", "pattern": [{"LOWER": "-"}, {"LOWER": " - "}, {"LOWER": "present"}, {"LOWER": "now"}]}]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)

# read files into text

# filepath = "resume/*"
# paths = glob.glob(filepath)
# for filename in paths:
#     text = ""
#     ext = os.path.splitext(filename)[-1].lower()
#     if ext == '.pdf':
#         with fitz.open(filename) as doc:
#             for page in doc:
#                 text += page.getText()
#     elif ext == '.docx':
#         text = docx2txt.process(filename)
#     else:
#         print(filename, " is not a pdf or docx file!")

    # extract company names

filename = "resume/AASHISH MAHAJAN.pdf"
#text = textract.process(filename)
#text = text.decode("utf-8")

text = ""
with fitz.open(filename) as doc:
    for page in doc:
        text += page.getText()

if 'Experience' in text:
    i = text.index('Experience')
else:
    print("Experience not found")
    if 'EXPERIENCE' in text:
        i = text.index('EXPERIENCE')
    else:
        print("EXPERIENCE not found either, move to next resume")
text = text[i:]
doc = nlp(text)
count = 0
for i in range(len(doc.ents) - 1):
    ent = doc.ents[i]
    ent_next = doc.ents[i + 1]
    if ent.label_ == "ORG" and ent_next.label_ == "DATE":
        count += 1
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        print(ent_next.text, ent_next.start_char, ent_next.end_char, ent_next.label_)
print(count)