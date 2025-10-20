# QGen-AI : Q/A generator using RAG, Pinecone, and Tavily web search to create MCQs and short Q/A.

**QGenAI** is an intelligent quiz generator that instantly creates MCQs and short-answer questions from any document you upload (PDF, DOCX, etc.). It's built on a modern RAG (Retrieval-Augmented Generation) pipeline:
1. Documents are vectorized and stored in Pinecone.
2. When you write a query, LangChain retrieves the most relevant context from your files.
3. If that context is insufficient, Tavily automatically performs a real-time web search to find the missing information.
4. The final, enriched context is sent to Groq's high-speed LLMs to generate your questions, all presented in a sleek, responsive UI.

<img width="1904" height="856" alt="image" src="https://github.com/user-attachments/assets/4aba0e0a-a2e5-4081-b044-ace7c6297fee" />

---

## ✨ Features

* **Modern 3-Column UI:** A "cockpit" style interface with a collapsible control panel for maximum focus.
* **Multi-Format Document Upload:** Ingest PDFs, DOCX, PPTX, TXT, and even images (PNG/JPG) via Tesseract OCR.
* **Cloud Vector Database:** Powered by **Pinecone** for an efficient, scalable, and persistent knowledge base.
* **Dual Generation Modes:** Create both **Multiple Choice Questions (MCQ)** with explanations and **Short Q&A** pairs.
* **Smart Web Search:** Automatically uses **Tavily AI** to supplement context if your documents are missing information—just flip the toggle!
* **High-Speed Generation:** Uses the **Groq** gpt-oss-120b model for near-instant question generation.
* **Sleek UX:** Features include drag-and-drop file uploads, animated skeleton loaders, and non-blocking toast notifications.
* **Export Results:** Download your generated quizzes as a clean JSON file.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, TailwindCSS, Vanilla JavaScript
* **Backend:** Python 3, Flask
* **Database:** Pinecone (Vector DB)
* **AI & Data Orchestration:**
    * LangChain (Core framework)
    * Groq (LLM Inference)
    * OpenAI (Embeddings)
    * Tavily AI (Web Search)

---

## 🚀 Getting Started

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

This is the most important step. The app will not run without these keys.

Create a file named `.env` in the root of the `qg_app` directory. Then, add the following lines to it, replacing `...` with your actual API keys.

```ini
# --- .env file ---

# Used for generating the text embeddings
OPENAI_API_KEY=your_openai_api_key_here

# Used for fast LLM generation
GROQ_API_KEY=your_groq_api_key_here

# Used for the Pinecone vector database
PINECONE_API_KEY=your_pinecone_api_key_here
```

**Where to get them:**
* **OPENAI_API_KEY:** Get from the [OpenAI Platform](https://platform.openai.com/api-keys)
* **GROQ_API_KEY:** Get from the [Groq Console](https://console.groq.com/keys)
* **PINECONE_API_KEY:** Get from the [Pinecone Console](https://app.pinecone.io/)

> **Warning: Pinecone Index Name**
> This application is currently hard-coded to use a Pinecone index named `nlp-project`. You must have a serverless index with this exact name in your Pinecone project.
>
> If you want to use a different name, you must update it in `modules/db_manager.py` at the top (`PINECONE_INDEX_NAME = "your-index-name"`).

### 5. (Optional) Install Tesseract OCR

To enable uploading images (PNG, JPG) and extracting text from them, you must install Google's Tesseract OCR on your system.

* [Tesseract Installation Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)

After installing, make sure the `tesseract` executable is added to your system's PATH.

### 6. Run the Application

Once your `.env` file is ready, run the Flask server:
```bash
python app.py
```
The application will be available at `http://127.0.0.1:5000`.

---

## 🖥️ How to Use

1.  Start the app and open it in your browser.
2.  Upload a file using the drag-and-drop zone in the left panel.
3.  Enter a query (e.g., "Key concepts from chapter 2" or "Data poisoning in LLMs").
4.  Select your options:
    * Number of questions
    * Question Type (MCQ or Short Q&A)
    * Toggle "Use Web Search" if you want the AI to search online for more context.
5.  Click Generate! The main panel will show skeleton loaders while the AI works, and the right panel will show your generation details.
6.  Review your questions and download them as JSON if you wish.
7.  Clear the DB using the "Clear DB" button to start fresh with new documents.

---

## ⚖️ License

This project is licensed under the MIT License.
