import os
from pypdf import PdfReader

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import BaseOutputParser

MODEL = "gemini-2.5-flash"

class QuizParser(BaseOutputParser):
    def parse(self, text: str):
        return text

def get_pdf_text(pdf_file):
    """Extract text from a PDF file"""
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_docx_text(docx_file):
    """Extract text from a Word (.docx) file"""
    try:
        from docx import Document
        text = ""
        doc = Document(docx_file)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError:
        return "Error: python-docx library not found. Please install it using 'pip install python-docx'"

def get_txt_text(txt_file):
    """Extract text from a TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        txt_file.seek(0)
        return txt_file.read().decode('latin-1')

def get_document_text(uploaded_files):
    """Extract text from multiple uploaded files (PDF, DOCX, TXT)"""
    text = ""
    for file in uploaded_files:
        file_extension = file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            text += get_pdf_text(file)
        elif file_extension == 'docx':
            text += get_docx_text(file)
        elif file_extension == 'txt':
            text += get_txt_text(file)
        else:
            print(f"Unsupported file type: {file.name}")
        
        # Add separator between documents
        text += "\n\n--- End of " + file.name + " ---\n\n"
    
    return text

def get_quiz_chain(api_key, quiz_type="Classic", language="English"):
    try:
        if not api_key:
            return None
            
        llm = ChatGoogleGenerativeAI(google_api_key=api_key, model=MODEL, temperature=0.7)
        
        if quiz_type == "Test":
            template = """
            You are an expert quiz maker. 
            Create a multiple-choice quiz with {number} questions based on the reference text provided below.
            The questions should be appropriate for {level} level students.
            
            Return the output STRICTLY as a VALID JSON ARRAY of objects.
            Each object must have the following structure:
            {{
                "question": "The question text",
                "options": ["Option A", "Option B", "Option C", "Option D", "Option E"],
                "correct_answer": "The correct option text (must match one of the options exactly)"
            }}

            The quiz and all questions/answers must be generated in the {language} language.
            
            Reference Text:
            {text}
            
            IMPORTANT:
            1. Return ONLY the JSON array.
            2. Do not include markdown formatting like ```json or ```.
            3. Ensure the JSON is valid and can be parsed.
            """

        else:
            template = """
            You are an expert quiz maker. 
            Create a quiz with {number} questions based on the reference text provided below.
            The questions should be appropriate for {level} level students.
            The quiz and all questions/answers must be generated in the {language} language.
            
            Reference Text:
            {text}
            
            Format the output as a numbered list of questions, followed by a numbered list of answers at the very end.
            """
        
        prompt = PromptTemplate(
            input_variables=["text", "number", "level", "language"],
            template=template
        )
        
        chain = prompt | llm | QuizParser()
        return chain
    except Exception as e:
        print(f"Error creating chain: {e}")
        return None

def get_abstract_chain(api_key, language="English"):
    try:
        if not api_key:
            return None
            
        llm = ChatGoogleGenerativeAI(google_api_key=api_key, model=MODEL, temperature=0.5)
        
        template = """
        You are an expert at summarizing documents.
        Create a concise abstract of the following text in {language}.
        The abstract should capture the main points and key ideas.
        
        Text:
        {text}
        
        Abstract:
        """
        
        prompt = PromptTemplate(
            input_variables=["text", "language"],
            template=template
        )
        
        chain = prompt | llm | QuizParser()
        return chain
    except Exception as e:
        print(f"Error creating abstract chain: {e}")
        return None
