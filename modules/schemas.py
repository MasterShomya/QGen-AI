import json
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

# --- Schemas ---

qa_schema = {
    "name": "qa_list",
    "description": "A list of question-answer pairs with short, concise answers.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Unique id for the question"},
            "question": {"type": "string", "description": "The question text"},
            "answer": {"type": "string", "description": "Short, concise answer (1-3 sentences max)"}
        },
        "required": ["id", "question", "answer"]
    }
}

mcq_schema = {
    "name": "mcq_list",
    "description": "A list of MCQ objects. Each MCQ must include exactly 4 options and one correct index (1-based).",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Unique id for the question"},
            "question": {"type": "string"},
            "options": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": {"type": "string"}
            },
            "correct_index": {"type": "integer", "minimum": 1, "maximum": 4},
            "explanation": {"type": "string", "description": "Short justification for the correct answer"}
        },
        "required": ["id", "question", "options", "correct_index"]
    }
}

# --- Parsers ---

qa_parser = JsonOutputParser(schema=qa_schema)
mcq_parser = JsonOutputParser(schema=mcq_schema)

# --- Prompt Templates ---

qa_prompt_template_str = """You are an expert question writer.
Context: {context}

Instruction:
 - Generate {num_questions} question-answer pairs strictly in JSON that conforms to the provided schema.
 - Each answer should be SHORT and CONCISE (1-3 sentences maximum).
 - Questions should be clear, specific, and directly answerable from the context.
 - IDs should be short unique strings (like QA1, QA2, ...).

JSON SCHEMA:
{schema}

Output ONLY valid JSON that matches the schema.
"""

qa_prompt_template = PromptTemplate(
    template=qa_prompt_template_str,
    input_variables=["context", "num_questions", "schema"]
)

mcq_prompt_template_str = """You are an expert defense studies question writer.
Context: {context}

Instruction:
 - Generate {num_questions} multiple-choice questions (MCQs) strictly in JSON that conforms to the provided schema.
 - Each question must have exactly 4 options.
 - Provide a short explanation for the correct option.
 - Use domain-accurate, textbook-style language (not generic).
 - Avoid using the exact words "Correct Answer" in the question text; put the correct option index in `correct_index`.
 - IDs should be short unique strings (like Q1, Q2 ...).

JSON SCHEMA:
{schema}

Output ONLY valid JSON that matches the schema.
"""

mcq_prompt_template = PromptTemplate(
    template=mcq_prompt_template_str,
    input_variables=["context", "num_questions", "schema"]
)

# --- Fallback JSON Parser ---

def safe_json_parse(raw_json_str: str, parser_type: str = "array"):
    """
    Tries to parse JSON, falling back to extracting from common LLM outputs.
    """
    try:
        if parser_type == "array":
            # Find the first '[' and last ']'
            start = raw_json_str.find("[")
            end = raw_json_str.rfind("]") + 1
            if start != -1 and end != -1:
                return json.loads(raw_json_str[start:end])
        else: # "object"
            start = raw_json_str.find("{")
            end = raw_json_str.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(raw_json_str[start:end])
        raise ValueError("No valid JSON object/array found")
    except Exception as e:
        print(f"[!] Fallback JSON parser failed: {e}")
        raise