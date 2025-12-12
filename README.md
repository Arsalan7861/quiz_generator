# 📝 PDF Quiz Generator

A professional grade Streamlit application that uses Google's Gemini AI to generate customized quizzes from your PDF study materials. Perfect for students, teachers, and lifelong learners looking to test their knowledge.

## 🚀 Features

- **PDF Text Extraction**: Upload multiple PDF documents (lesson materials, textbooks, notes).
- **AI-Powered Generation**: Utilizes Google's Gemini Pro (`gemini-2.5-flash`) for high-quality question generation.
- **Customizable**:
  - Choose number of questions (1-20).
  - Select difficulty level (Easy, Intermediate, Advanced, Expert).
  - Quiz types: Classic (open/mixed) or Test (Multiple Choice with 5 options).
- **Instant Feedback**: Generates questions and answers separately for self-grading.
- **Downloadable**: Export your generated quiz as a text file.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Orchestration**: [LangChain](https://www.langchain.com/)
- **AI Model**: [Google Gemini](https://ai.google.dev/) via `langchain-google-genai`
- **PDF Processing**: `pypdf`

## 📋 Prerequisites

- Python 3.8 or higher installed on your system.
- An active Google Cloud Project with Gemini API access (or a key from Google AI Studio).

## ⚡ Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository (or download files)
Ensure you are in the project directory:
```bash
cd quiz_generator
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```powershell
python -m venv .venv
```

**macOS / Linux:**
```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows:**
```powershell
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
Install all required libraries using the requirements file:
```bash
pip install -r requirements.txt
```

## 🎮 How to Run

1. **Get your API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/).
   - Create an API Key.

2. **Start the Application**:
   Run the following command in your terminal (with the virtual environment activated):
   ```bash
   streamlit run app.py
   ```

3. **Using the App**:
   - Once the app opens in your browser (usually at `http://localhost:8501`):
   - Enter your **Google Gemini API Key** in the sidebar.
   - **Upload** your PDF documents.
   - Configure your quiz settings (Number of questions, Difficulty, Type).
   - Click **Generate Quiz**.

## 📂 Project Structure

```
quiz_generator/
├── app.py              # Main application entry point & UI
├── utils.py            # Helper functions (PDF processing, LangChain setup)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (optional)
└── README.md           # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
