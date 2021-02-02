import fitz
import glob
import os
import docx2txt
import textract
from spacy.pipeline import EntityRuler
import spacy

output_file = open("output.txt", "w+")

# spacy entity patterns
nlp = spacy.load("en_core_web_md")
ruler = EntityRuler(nlp)
capitalized_word = "([A-Z][a-z]+)"
corporate_stopwords = "(.+[Ii]nc|[Cc]orp|[Cc]o|[Ll]lc|[Ll]td)"
patterns = [
            {"label": "DATE", "pattern": [{"LOWER": "present"}]},
            {"label": "DATE", "pattern": [{"LOWER": "now"}]},
            {"label": "DATE", "pattern": [{"LOWER": "current"}]}]
#      {"label": "ORG", "pattern": [{"TEXT": {"REGEX": corporate_stopwords}}]}]

ruler.add_patterns(patterns)
nlp.add_pipe(ruler, before='ner')

# text = textract.process(filename)
# text = text.decode("utf-8")

# read files into text
filepath = "resume/*"
paths = glob.glob(filepath)
for filename in paths:
    text = ""
    ext = os.path.splitext(filename)[-1].lower()
    if ext == '.pdf':
        with fitz.open(filename) as doc:
            for page in doc:
                text += page.getText()
    elif ext == '.docx':
        text = docx2txt.process(filename)
    else:
        print(filename, " is not a pdf or docx file!")

    output_file.write(filename + "\n")
    # parse to experience to get company names
    if 'Experience' in text:
        i = text.index('Experience')
        text = text[i:]
    else:
        print("Keyword Experience not found in " + filename + ", search for keyword EXPERIENCE")
        if 'EXPERIENCE' in text:
            i = text.index('EXPERIENCE')
            text = text[i:]
        else:
            print("EXPERIENCE not found either in " + filename + ", move to next resume")

    doc = nlp(text)
    for i in range(len(doc.ents) - 1):
        string = ""
        ent = doc.ents[i]
        j = i + 1
        if ent.label_ == "ORG":
            while j < len(doc.ents) - 1 and doc.ents[j].start_char - ent.end_char <= 50:
                ent_next = doc.ents[j]
                if ent_next.label_ == "DATE":
                    ent_next_date = doc.ents[j + 1]
                    if ent_next_date.label_ == "DATE" and ent_next_date.start_char - ent_next.end_char <= 10:
                        string += "Company: " + ent.text.strip().rstrip('-').rstrip() + ", Date: " + \
                                  ent_next.text.strip().rstrip('-') + " - " + ent_next_date.text.strip() + "\n"
                    else:
                        string += "Company: " + ent.text.strip().rstrip('-').rstrip() + ", Date: " + \
                                  ent_next.text.strip() + "\n"
                    output_file.write(string)
                    break
                j += 1

    output_file.write("======================================================================================\n")

output_file.close()
