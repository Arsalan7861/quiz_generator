import streamlit as st
from utils import get_pdf_text, get_quiz_chain

def load_custom_css():
    """Load custom CSS from external file"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="AI Quiz Generator - Transform PDFs into Quizzes",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.markdown("<h1>🚀 AI Quiz Generator</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Transform your study materials into personalized quizzes powered by Google Gemini AI</div>", unsafe_allow_html=True)

    # Sidebar for API Key and PDF Upload
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        st.markdown("---")
        
        api_key = st.text_input(
            "🔑 Google Gemini API Key",
            type="password",
            help="Get your API key from Google AI Studio"
        )
        
        st.markdown("---")
        st.markdown("### 📄 Upload Documents")
        
        pdf_docs = st.file_uploader(
            "Drag and drop your PDF files here",
            accept_multiple_files=True,
            type=['pdf'],
            help="Upload one or more PDF documents containing your study material"
        )
        
        if pdf_docs:
            st.success(f"✅ {len(pdf_docs)} file(s) uploaded")
        
        st.markdown("---")
        st.markdown("""
        <div style='color: #94a3b8; font-size: 0.85rem; line-height: 1.6;'>
            <strong>💡 How it works:</strong><br>
            1. Upload your study materials<br>
            2. Configure quiz settings<br>
            3. Let AI generate your quiz<br>
            4. Download and study!
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    col_main1, col_main2 = st.columns([2, 1])
    
    with col_main1:
        # Quiz Configuration Form
        with st.form("quiz_params"):
            st.markdown("### 🎯 Quiz Configuration")
            st.markdown("Customize your quiz settings below")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                question_count = st.number_input(
                    "📝 Number of Questions",
                    min_value=1,
                    max_value=20,
                    value=5,
                    help="Choose how many questions you want"
                )
            
            with col2:
                difficulty = st.selectbox(
                    "⚡ Difficulty Level",
                    ["Easy", "Intermediate", "Advanced", "Expert"],
                    help="Select the difficulty level"
                )
            
            with col3:
                quiz_type = st.selectbox(
                    "📋 Quiz Type",
                    ["Classic", "Test"],
                    help="Classic: Mixed questions | Test: Multiple choice"
                )
            
            col4, col5 = st.columns(2)
            
            with col4:
                language = st.selectbox(
                    "🌍 Language",
                    ["English", "Turkish"],
                    help="Select the language for your quiz"
                )
            
            submitted = st.form_submit_button("✨ Generate Quiz", use_container_width=True)
        
        # Quiz Results Area
        if submitted:
            if not api_key:
                st.error("🔒 Please provide a Google Gemini API Key in the sidebar.")
                return
                
            if not pdf_docs:
                st.error("📄 Please upload at least one PDF file.")
                return
                
            with st.spinner("🔄 Processing your documents..."):
                raw_text = get_pdf_text(pdf_docs)
                
                if not raw_text:
                    st.warning("⚠️ Could not extract text from the uploaded files. Please check your PDFs.")
                    return
            
            with st.spinner("🤖 AI is generating your quiz..."):
                chain = get_quiz_chain(api_key, quiz_type, language)
                if chain:
                    response = chain.invoke({
                        "text": raw_text,
                        "number": question_count,
                        "level": difficulty,
                        "language": language
                    })
                    
                    st.success("🎉 Quiz Generated Successfully!")
                    
                    # Display quiz in a styled container
                    st.markdown("<div class='quiz-output'>", unsafe_allow_html=True)
                    st.markdown(response)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Quiz",
                        data=str(response),
                        file_name=f"quiz_{difficulty.lower()}_{question_count}q.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
    
    with col_main2:
        # Feature highlights
        st.markdown("### ✨ Features")
        
        st.markdown("""
        <div class='feature-card'>
            <h4>🎯 Smart Generation</h4>
            <p style='font-size: 0.9rem; color: #64748b;'>AI-powered question generation from your study materials</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
            <h4>🌍 Multi-Language</h4>
            <p style='font-size: 0.9rem; color: #64748b;'>Generate quizzes in English or Turkish</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
            <h4>⚡ Customizable</h4>
            <p style='font-size: 0.9rem; color: #64748b;'>Control difficulty, quantity, and quiz type</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
            <h4>📥 Downloadable</h4>
            <p style='font-size: 0.9rem; color: #64748b;'>Export your quizzes for offline study</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
