import streamlit as st
from utils import get_pdf_text, get_quiz_chain

def main():
    st.set_page_config(page_title="PDF Quiz Generator", page_icon="📝")
    
    st.header("📝 PDF Quiz Generator")
    st.subheader("Turn your lesson materials into a quiz!")

    # Sidebar for API Key and Inputs
    with st.sidebar:
        st.markdown("## Configuration")
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        
        st.markdown("---")
        
        pdf_docs = st.file_uploader(
            "Upload your Lesson Materials (PDF)", 
            accept_multiple_files=True,
            type=['pdf']
        )
        
    # Main Form
    with st.form("quiz_params"):
        col1, col2 = st.columns(2)
        
        with col1:
            question_count = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
            
        with col2:
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Intermediate", "Advanced", "Expert"])
            quiz_type = st.selectbox("Quiz Type", ["Classic", "Test"])
            language = st.selectbox("Language", ["English", "Turkish"])
            
        submitted = st.form_submit_button("Generate Quiz")

    if submitted:
        if not api_key:
            st.error("Please provide a Google Gemini API Key in the sidebar.")
            return
            
        if not pdf_docs:
            st.error("Please upload at least one PDF file.")
            return
            
        with st.spinner("Processing documents..."):
            raw_text = get_pdf_text(pdf_docs)
            
            if not raw_text:
                st.warning("Could not extract text from the uploaded files. Please check existing PDFs.")
                return
                
        with st.spinner("Generating Quiz..."):
            chain = get_quiz_chain(api_key, quiz_type, language)
            if chain:
                response = chain.invoke({
                    "text": raw_text,
                    "number": question_count,
                    "level": difficulty,
                    "language": language
                })
                
                st.success("Quiz Generated!")
                st.markdown("---")
                st.markdown(response)
                
                # Optional: Download button logic could go here
                st.download_button(
                    label="Download Quiz",
                    data=str(response),
                    file_name="generated_quiz.txt",
                    mime="text/plain"
                )

if __name__ == '__main__':
    main()
