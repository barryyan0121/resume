# Extract Company Names & Dates from resumes
## Abstract
The project uses `Spacy` to extract company names and dates
in different formats of resumes (in this case **.pdfs** and **.docx**) 
without additional trainings. It uses the basic model from `Spacy` without
tuning, so the accuracy is not satisfying. However, it shows an elementary
approach in natural language processing.
## Introduction
This is my first approach to `NLP`, and this project gives me an overview
of the industry. With a list of resumes written in different formats,
what would the most effective approach to extract the company titles,
and the corresponding dates? This is different from Named-entity recognition
in normal texts, as company names do not appear in complete sentences.
The basic model of `Spacy` is a multi-task CNN trained on OntoNotes with
blogs, news, and comments with an `NER` accuracy of 85%. Since the model
is for general purpose, it might not perform well for `NER` tasks for resumes.
In fact, when I tested it on an example resume, I see a lot of `NER` falsely
classified. It is then critical to improve on the results without access
to large number of training samples.
## Method
I set up `PyCharm` as my IDE and `Conda` as Python Interpreter because I could
not install numpy with wheel in virtualenv environment with M1 chip. I
used `Python 3.8`, and you can build the dependency as follows.
```
pip3 install -r requirements.txt
```
Here is a list of packages I used.
```python3
import fitz
import glob
import os
import docx2txt
import textract
from spacy.pipeline import EntityRuler
import spacy
```
I then looped through the resume folder and read the files into strings.
For PDF files, I used `PyMuPDF` to convert them to strings. For my 21 samples
of PDF files, it only failed to read one of them. For docx files, I used
`docx2txt` to convert them to strings. The conversion is not perfect for
any of the files, and I also tried to use `textract` as a general approach,
which works for general types of files. If I had files with various
extension names, I would prefer to use `textract`. It reads files into
bytes string, and you need to decode it with utf-8. I think `PyMuPDF`
works better for PDF files, since I only have two types of files. 
```python3
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
```
After read files into strings, I need to find a way to extract the
company names efficiently. The first thing came to my mind was to 
extract bold texts, since we would highlight the company names for
the most times. However, when I checked in the resumes, many of them
did not bold company names, so I had to find another approach. I then
realized that all resumes have a section titled `"Work Experience"`, either
in upper cases or in lower cases. So I searched the strings for the keyword
`"Experience"` or `"EXPERIENCE"`, and extracted the following strings. In
this way, if the NER recognized company names in the education or skills
section, we would be able to ignore them safely without doing additional
works.
```python3
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
```
I then moved to `NER` part. After reading several articles, I decided to use
`Spacy` instead of `NLTK`. `NLTK` is essentially a string processing library, where
each function takes strings as I/O. For a beginner, I think that `Spacy`'s
object-oriented approach seems more friendly. 
```python3
nlp = spacy.load("en_core_web_lg")
ruler = EntityRuler(nlp)
capitalized_word = "([A-Z][a-z]+)"
corporate_stopwords = "([Ii]nc|[Cc]orp|[Cc]o|[Ll]lc|[Ll]td)"
patterns = [
            {"label": "DATE", "pattern": [{"LOWER": "present"}]},
            {"label": "DATE", "pattern": [{"LOWER": "now"}]},
            {"label": "DATE", "pattern": [{"LOWER": "current"}]}]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler, before='ner')
```
Here I used the largest pretrained model of English in `Spacy`(742 MB), because
it recognized more entities than the other two smaller models. I then used
the `EntityRuler` to provide some patterns for the nlp object to match. In
this case, `present/current/now` can represent working time, so we add them
to the pattern dictionary for matches. I added the ruler before other pipelines
so that the `NER` would respect the existing entity spans and adjust its
predictions around it. I also tried to add company suffixes such as `LTD./LLC./CORP./CO.`
into `ORG` patterns, but it did not work well. The `NER` misidentified many
more entities with my written regex, so I commented it out.
```python3
doc = nlp(text)
for i in range(len(doc.ents) - 1):
    string = ""
    ent = doc.ents[i]
    j = i + 1
    if ent.label_ == "ORG":
        while j < len(doc.ents) and doc.ents[j].start_char - ent.end_char <= 50:
            ent_next = doc.ents[j]
            if ent_next.label_ == "DATE":
                ent_next_date = doc.ents[j + 1]
                if ent_next_date.label_ == "DATE" and ent_next_date.start_char - ent_next.end_char <= 10:
                    string += "Company: " + ent.text.strip().rstrip('-').rstrip() + ", Date: " + \
                              ent_next.text.strip().rstrip('-') + " - " + ent_next_date.text.strip() + "\n"
                else:
                    string += "Company: " + ent.text.strip().rstrip('-').rstrip() + ", Date: " + \
                              ent_next.text + "\n"
                output_file.write(string)
                break
            j += 1
```
I then did a simple filter rule by calculating the relative positions between
entity `ORG` and `DATE`. I noticed that after listing every company in the
resume, one will also add the corresponding time range. So I found every 
`ORG` with a following `DATE` that is within 50 characters. I choose 50
characters because sometime people will list their job titles after the
company names, and there will be trailing whitespaces as well. In this way,
I would be able to figure out the real company names along with the time
range, without having to worry too much about the companies mentioned in 
the working experience description, because they would less likely have a 
date following it.<br><br>
After some testings and examinations, I also realized that `Spacy` is not
identifying the `DATE` correctly, because sometimes it seemed not recognized
the `-` between the `DATE`. Instead, it identified them as two separate `DATE`.
One way to solve this is to check the entity right after it. If it is indeed
a `DATE`, we can then safely assume it connects with the previous `DATE`.
However, this solution is not perfectly accurate, because some resumes have
the following `DATE` formatted to the end of the next line, which will not be
the next entity. However, my solution already used time complexity of O(n^2).
So it seemed to work the best to just check the next entity instead of checking
the next `DATE` and calculating its relative position.
## Results & Discussion
I wrote the outputs to a text file with each of the file names, the
company names (`ORG`) within the resume, and the corresponding dates(`DATE`). Some
resumes seem to have better performance than others, and some are doing
poorly with nonsense outputs. I assume that part of the reason that the
program outputs more false company names is because I used a large pretrained
model without tuning. If I switched to the smallest network, I got significantly
fewer outputs, but it also gave away some correct results. I finally decided
to use the medium size, since it gave the most correct results. <br><br>
The results are in [`output.txt`](https://github.com/barryyan0121/resume/blob/master/output.txt), 
and the source code is in [`main.py`](https://github.com/barryyan0121/resume/blob/master/main.py). 
With such method of filtering, I was able to pull up company names and time ranges.
However, many of my outputs include false company names, which either belong to
other sections of the resumes, or are job titles/technology terms. I think that
if I use enough training data, the results will be improved significantly.

