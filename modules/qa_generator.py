import os
import json
from langchain.chains import LLMChain

# Import from our modules
from .schemas import qa_prompt_template, qa_parser, qa_schema, safe_json_parse
# --- MODIFIED ---
# Import shared utilities
from .utils import calculate_context_similarity, search_with_tavily
# --- END MODIFIED ---

def generate_qa_from_context(retriever, llm, query: str, embeddings, num_questions: int, 
                             similarity_threshold: float = 0.5, use_tavily: bool = False):
    """
    Generate question-answer pairs from retrieved context.
    Checks similarity and optionally uses Tavily search.
    """
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([d.page_content for d in docs])
    
    similarity_score = calculate_context_similarity(query, context, embeddings)
    print(f"\n[*] Context similarity score: {similarity_score:.2%}")
    
    if similarity_score < similarity_threshold:
        print(f"[!] Similarity ({similarity_score:.2%}) is below threshold ({similarity_threshold:.2%})")
        
        if use_tavily:
            print("[*] Tavily search is enabled. Searching web...")
            tavily_content = search_with_tavily(f"Information regarding: {query}")
            
            if tavily_content:
                print("[+] Using Tavily search results as context")
                context = tavily_content
                similarity_score = calculate_context_similarity(query, context, embeddings)
                print(f"[*] New context similarity score: {similarity_score:.2%}")
            else:
                print("[!] No results from Tavily, using original context")
        else:
            print("[*] Tavily search is disabled. Proceeding with original context.")
    else:
        print(f"[+] Context similarity is acceptable ({similarity_score:.2%})")

    # Build chain
    llm_chain = LLMChain(llm=llm, prompt=qa_prompt_template)

    print(f"\n[*] Generating {num_questions} Q&A pairs...")
    raw = llm_chain.run({
        "context": context,
        "num_questions": num_questions,
        "schema": json.dumps(qa_schema)
    })

    # Parse JSON output
    try:
        parsed = qa_parser.parse(raw)
    except Exception as e:
        print(f"[!] Structured parser failed: {e}. Trying fallback.")
        parsed = safe_json_parse(raw, "array")

    return parsed, context, similarity_score