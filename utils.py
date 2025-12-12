import os
from pypdf import PdfReader
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import BaseOutputParser

class QuizParser(BaseOutputParser):
    def parse(self, text: str):
        return text

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_quiz_chain(api_key, quiz_type="Classic", language="English"):
    try:
        if not api_key:
            return None
            
        llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash", temperature=0.7)
        
        if quiz_type == "Test":
            template = """
            You are an expert quiz maker. 
            Create a multiple-choice quiz with {number} questions based on the reference text provided below.
            The questions should be appropriate for {level} level students.
            Each question MUST have exactly 5 options (A, B, C, D, E).
            The quiz and all questions/answers must be generated in the {language} language.
            
            Reference Text:
            {text}
            
            Format the output as a numbered list of questions, followed by a numbered list of answers at the very end.
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
