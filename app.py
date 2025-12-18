import streamlit as st
import json
from utils import get_document_text, get_quiz_chain, get_abstract_chain

def load_custom_css():
    """Load custom CSS from external file"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="AI Quiz Generator - Transform PDFs into Quizzes",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Header with Material Icon
    st.markdown("""
    <h1>
        <span class="material-icons header-icon">quiz</span>
        AI Quiz Generator
    </h1>
    """, unsafe_allow_html=True)
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
        
        uploaded_docs = st.file_uploader(
            "Drag and drop your files here",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            help="Upload PDF, Word (.docx), or Text files containing your study material"
        )
        
        if uploaded_docs:
            st.success(f"✅ {len(uploaded_docs)} file(s) uploaded")
        
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
            
            col1, col2 = st.columns(2)
            
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
            
            col4, col5 = st.columns(2)
            
            with col4:
                language = st.selectbox(
                    "🌍 Language",
                    ["English", "Turkish"],
                    help="Select the language for your quiz"
                )
                
            with col5:
                quiz_type = st.selectbox(
                "📋 Quiz Type",
                ["Classic", "Test"],
                help="Classic: Mixed questions | Test: Multiple choice"
                )
            
            include_abstract = st.checkbox("📝 Include Abstract", help="Generate a summary/abstract of the content")
            
            submitted = st.form_submit_button("✨ Generate Quiz", use_container_width=True)
        
        # Quiz Results Area
        if submitted:
            if not api_key:
                st.error("🔒 Please provide a Google Gemini API Key in the sidebar.")
            elif not uploaded_docs:
                st.error("📄 Please upload at least one document file.")
            else:
                with st.spinner("🔄 Processing your documents..."):
                    raw_text = get_document_text(uploaded_docs)
                
                if not raw_text:
                    st.warning("⚠️ Could not extract text from the uploaded files. Please check your documents.")
                else:
                    with st.spinner("🤖 AI is generating your quiz..."):
                        if include_abstract:
                            abstract_chain = get_abstract_chain(api_key, language)
                            if abstract_chain:
                                abstract_resp = abstract_chain.invoke({"text": raw_text, "language": language})
                                st.session_state['abstract_text'] = abstract_resp
                        else:
                            st.session_state.pop('abstract_text', None)

                        chain = get_quiz_chain(api_key, quiz_type, language)
                        if chain:
                            response = chain.invoke({
                                "text": raw_text,
                                "number": question_count,
                                "level": difficulty,
                                "language": language
                            })
                            
                            st.session_state['quiz_data'] = response
                            st.session_state['quiz_type_current'] = quiz_type
                            
                            # Clear old quiz answers to prevent state conflicts
                            keys_to_remove = [k for k in st.session_state.keys() if k.startswith('question_')]
                            for k in keys_to_remove:
                                del st.session_state[k]
                                
                            if quiz_type == "Test":
                                st.session_state['quiz_submitted'] = False
                            
                            st.rerun()

        # Render Quiz if data exists
        if 'quiz_data' in st.session_state:
            st.markdown("---")
            
            if 'abstract_text' in st.session_state:
                st.subheader("📄 Abstract")
                st.info(st.session_state['abstract_text'])
                st.markdown("---")
                
            st.subheader("📝 Generated Quiz")
            
            # Handle Test Type (Interactive)
            if st.session_state.get('quiz_type_current') == "Test":
                try:
                    # Clean up potential markdown formatting from LLM
                    quiz_data_str = st.session_state['quiz_data']
                    if "```json" in quiz_data_str:
                         quiz_data_str = quiz_data_str.replace("```json", "").replace("```", "")
                    elif "```" in quiz_data_str:
                         quiz_data_str = quiz_data_str.replace("```", "")
                         
                    quiz_json = json.loads(quiz_data_str)
                    
                    with st.form("quiz_form"):
                        correct_answers = 0
                        total_questions = len(quiz_json)
                        
                        for i, q in enumerate(quiz_json):
                            st.markdown(f"**{i+1}. {q['question']}**")
                            st.radio(
                                f"Select answer for question {i+1}:",
                                q['options'],
                                key=f"question_{i}",
                                index=None,
                                label_visibility="collapsed"
                            )
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        submit_quiz = st.form_submit_button("Submit Answers", use_container_width=True)
                        
                        if submit_quiz:
                            st.session_state['quiz_submitted'] = True
                    
                    # Show results outside the form so they persist/update
                    if st.session_state.get('quiz_submitted', False):
                        score = 0
                        st.markdown("### 📊 Results")
                        for i, q in enumerate(quiz_json):
                            user_choice = st.session_state.get(f"question_{i}")
                            correct_choice = q['correct_answer']
                            
                            if user_choice == correct_choice:
                                score += 1
                                result_icon = "✅"
                                result_color = "green"
                            else:
                                result_icon = "❌"
                                result_color = "red"
                                
                            st.markdown(
                                f"<div style='padding: 10px; border-radius: 5px; background-color: rgba(255,255,255,0.05); margin-bottom: 5px;'>"
                                f"{result_icon} <strong>Q{i+1}:</strong> Your answer: <span style='color:{result_color}'>{user_choice}</span> | Correct: <span style='color:green'>{correct_choice}</span>"
                                f"</div>", 
                                unsafe_allow_html=True
                            )
                        
                        percentage = (score / total_questions) * 100
                        st.metric("Final Score", f"{score}/{total_questions}", f"{percentage:.1f}%")
                        
                except json.JSONDecodeError:
                    st.error("Error parsing quiz data. Falling back to text view.")
                    st.markdown(st.session_state['quiz_data'])

            # Handle Classic Type (Text)
            else:
                # Format as a blockquote > to use custom CSS styling while preserving markdown support
                quiz_text = st.session_state['quiz_data'].replace('\n', '\n> ')
                st.markdown(f"> {quiz_text}")
            
            # Download button (Common for both)
            st.download_button(
                label="⬇️ Download Quiz",
                data=str(st.session_state['quiz_data']),
                file_name=f"quiz_generated.txt",
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
