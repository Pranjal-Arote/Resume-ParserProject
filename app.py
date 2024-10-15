from flask import Flask, render_template, request
import docx
import PyPDF2
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text


def extract_skills(text):
    predefined_skills = ['Python', 'Machine Learning', 'Data Analysis', 'Java', 'SQL', 'Excel', 'NLP', 'Cloud']
    skills_found = [skill for skill in predefined_skills if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return list(set(skills_found))


def extract_missing_skills(resume_skills, jd_skills):
    missing_skills = set(jd_skills) - set(resume_skills)
    return list(missing_skills)


def extract_experience(text):
    match = re.search(r'(\d+)\s+years\s+of\s+experience', text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} years"
    return "Experience not mentioned"


def extract_name(text):
    match = re.search(r'\b([A-Z][a-z]+\s[A-Z][a-z]+)\b', text)
    if match:
        return match.group(0)
    return "Name not found"


def extract_email(text):
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if match:
        return match.group(0)
    return "Email not found"

def extract_phone_number(text):
    match = re.search(r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b', text)
    if match:
        return match.group(0)
    return "Phone number not found"


def calculate_similarity(resume_skills, jd_skills):
    vectorizer = CountVectorizer().fit_transform([resume_skills, jd_skills])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1] * 100  

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume_file = request.files['resume']
        jd_file = request.files['jd']

       
        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        elif resume_file and resume_file.filename.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_file)
        else:
            resume_text = ""

        resume_skills = extract_skills(resume_text)
        resume_experience = extract_experience(resume_text)
        resume_name = extract_name(resume_text)
        resume_email = extract_email(resume_text)
        resume_phone = extract_phone_number(resume_text)

        
        if jd_file and jd_file.filename.endswith('.pdf'):
            jd_text = extract_text_from_pdf(jd_file)
        elif jd_file and jd_file.filename.endswith('.docx'):
            jd_text = extract_text_from_docx(jd_file)
        else:
            jd_text = ""

        jd_skills = extract_skills(jd_text)
        jd_experience = extract_experience(jd_text)

        
        matching_skills = set(resume_skills) & set(jd_skills)
        missing_skills = extract_missing_skills(resume_skills, jd_skills)
        similarity_score = calculate_similarity(" ".join(resume_skills), " ".join(jd_skills))

        return render_template('results.html',
                               resume_name=resume_name,
                               resume_email=resume_email,
                               resume_phone=resume_phone,
                               resume_skills=", ".join(resume_skills),
                               jd_skills=", ".join(jd_skills),
                               matching_skills=", ".join(matching_skills),
                               missing_skills=", ".join(missing_skills),
                               similarity_score=round(similarity_score, 2),
                               resume_experience=resume_experience,
                               jd_experience=jd_experience)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
