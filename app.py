import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from our custom modules
from modules.db_manager import (
    upsert_documents, 
    clear_vectordb,
    load_document, 
    get_vectordb, 
    get_embeddings, 
    get_mmr_retriever
)
from modules.qa_generator import generate_qa_from_context
from modules.mcq_generator import generate_mcqs_from_retrieved_context
from modules.llm_provider import get_qa_llm, get_mcq_llm

# --- App Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('chroma_persist', exist_ok=True)

# --- Static Routes ---
@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')

@app.route('/static/js/<path:filename>')
def static_js(filename):
    """Serve the main.js file."""
    return send_from_directory('static/js', filename)

# --- API Endpoints ---

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads to the vector database."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
            docs = load_document(file_path)
            if not docs:
                 return jsonify({"error": "File type not supported or file is empty"}), 400
                 
            upsert_documents(docs)
            
            # --- MODIFIED: Friendlier message for toast ---
            return jsonify({"message": f"File processed: {filename}"}), 200
            # --- END MODIFIED ---
        
        except Exception as e:
            print(f"[!] Upload Error: {e}")
            return jsonify({"error": str(e)}), 500
        
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

# --- MODIFIED: Handle new return signature from clear_vectordb ---
@app.route('/clear-db', methods=['POST'])
def clear_db():
    """Clear the entire Chroma vector database."""
    try:
        success, message, msg_type = clear_vectordb()
        if success:
            return jsonify({"message": message, "type": msg_type}), 200
        else:
            # msg_type is 'error' here
            return jsonify({"error": message, "type": msg_type}), 500
    except Exception as e:
        print(f"[!] Clear DB Error: {e}")
        return jsonify({"error": str(e), "type": "error"}), 500
# --- END MODIFIED ---


@app.route('/generate', methods=['POST'])
def generate():
    """Generate MCQs or Q&A based on user query."""
    data = request.get_json()
    query = data.get('query')
    num_questions = int(data.get('numQuestions', 5))
    gen_type = data.get('type', 'mcq') # 'mcq' or 'qa'
    use_tavily = bool(data.get('useTavily', False))
    
    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        vectordb = get_vectordb()
        retriever = get_mmr_retriever(vectordb)
        # --- MODIFIED: Get embeddings for both types ---
        embeddings = get_embeddings()
        
        if gen_type == 'mcq':
            llm = get_mcq_llm()
            # Pass new args to the mcq generator
            result, _ = generate_mcqs_from_retrieved_context(
                retriever, 
                llm, 
                query, 
                embeddings, 
                num_questions,
                similarity_threshold=0.5, # default
                use_tavily=use_tavily
            )
        # --- END MODIFIED ---
        else: # 'qa'
            llm = get_qa_llm()
            result, _, _ = generate_qa_from_context(
                retriever, 
                llm, 
                query, 
                embeddings, 
                num_questions, 
                similarity_threshold=0.5,
                use_tavily=use_tavily
            )
        
        if not result:
             return jsonify({"error": "No results generated. The context might be empty or irrelevant."}), 404

        return jsonify({"data": result}), 200
        
    except Exception as e:
        print(f"[!] Generation Error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# --- Run Application ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)