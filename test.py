import spacy
import textract
from spacy.pipeline import EntityRuler

output_file = open("test_output.txt", "w+")
filename = "resume/resume_xiaomeng zhang__.pdf"

text = textract.process(filename)
text = text.decode("utf-8")

nlp = spacy.load("en_core_web_lg")
ruler = EntityRuler(nlp)
patterns = [
            {"label": "DATE", "pattern": [{"LOWER": "present"}]},
            {"label": "DATE", "pattern": [{"LOWER": "now"}]},
            {"label": "DATE", "pattern": [{"LOWER": "current"}]},
            {"label": "ORG", "pattern": [{"LOWER": "llc"}]}]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler, before='ner')
doc = nlp(text)
for i in range(len(doc.ents) - 1):
    string = ""
    ent = doc.ents[i]
    j = i + 1
    if ent.label_ == "ORG":
        while j < len(doc.ents) and doc.ents[j].start_char - ent.end_char <= 100:
            ent_next = doc.ents[j]
            if ent_next.label_ == "DATE":
                ent_next_date = doc.ents[j + 1]
                if ent_next_date.label_ == "DATE" and ent_next_date.start_char - ent_next.end_char <= 10:
                    string += "company: " + ent.text.strip().rstrip('-').rstrip() + ", date: " + \
                              ent_next.text.strip().rstrip('-') + " - " + ent_next_date.text.strip() + "\n"
                else:
                    string += "company: " + ent.text.strip().rstrip('-').rstrip() + ", date: " + \
                              ent_next.text + "\n"
                output_file.write(string)
                break
            j += 1
output_file.close()
