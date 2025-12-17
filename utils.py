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
            Each question MUST have exactly 5 options (A, B, C, D, E).
            The quiz and all questions/answers must be generated in the {language} language.
            
            Reference Text:
            {text}
            
            IMPORTANT FORMATTING INSTRUCTIONS:
            1. Number each question clearly (1., 2., 3., etc.)
            2. Put each question on its own line
            3. Add a blank line after each question text before the options
            4. Put each option (A, B, C, D, E) on a separate line
            5. Add proper spacing between options for readability
            6. Add a blank line between each complete question block
            7. At the end, provide an "ANSWERS:" section with the correct answers listed clearly (1. A, 2. C, etc.)
            
            Example format:
            
            1. What is the capital of France?
            
            A) London
            B) Paris
            C) Berlin
            D) Madrid
            E) Rome
            
            2. Which element has the symbol 'O'?
            
            A) Gold
            B) Silver
            C) Oxygen
            D) Iron
            E) Carbon
            
            ANSWERS:
            1. B
            2. C
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
