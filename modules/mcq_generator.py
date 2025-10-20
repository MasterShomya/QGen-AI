import json
from langchain.chains import LLMChain

# Import from our modules
from .schemas import mcq_prompt_template, mcq_parser, mcq_schema, safe_json_parse
# --- MODIFIED ---
# Import shared utilities
from .utils import calculate_context_similarity, search_with_tavily
# --- END MODIFIED ---

# --- MODIFIED: Function signature and logic updated ---
def generate_mcqs_from_retrieved_context(retriever, llm, query: str, embeddings, num_questions=None,
                                        similarity_threshold: float = 0.5, use_tavily: bool = False):
    """
    Generate MCQs from retrieved context based on a query.
    Optionally uses Tavily if context similarity is low.
    """
    # Get relevant docs based on the user's query
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([d.page_content for d in docs])
    
    similarity_score = calculate_context_similarity(query, context, embeddings)
    print(f"\n[*] Context similarity score: {similarity_score:.2%}")

    if not context or similarity_score < similarity_threshold:
        if not context:
            print("[!] No context found for the query.")
        else:
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
                print("[!] No results from Tavily, using original (or empty) context")
        else:
            print("[*] Tavily search is disabled. Proceeding with original context.")
    else:
        print(f"[+] Context similarity is acceptable ({similarity_score:.2%})")

    if not context:
        print("[!] No context found. Cannot generate MCQs.")
        return [], ""

    # Decide number of MCQs if not specified
    if num_questions is None:
        approx_chars = len(context)
        num_questions = min(12, max(3, approx_chars // 300))

    # Build chain
    llm_chain = LLMChain(llm=llm, prompt=mcq_prompt_template)

    print(f"\n[*] Generating {num_questions} MCQs...")
    raw = llm_chain.run({
        "context": context,
        "num_questions": num_questions,
        "schema": json.dumps(mcq_schema)
    })

    # Parse structured output
    try:
        parsed = mcq_parser.parse(raw)
    except Exception as e:
        print(f"[!] Structured parser failed: {e}. Trying fallback.")
        try:
            parsed_obj = safe_json_parse(raw, "object")
            if "mcq_list" in parsed_obj:
                 parsed = parsed_obj["mcq_list"]
            else:
                 parsed = safe_json_parse(raw, "array")
        except Exception:
             parsed = safe_json_parse(raw, "array")

    return parsed, context
# --- END MODIFIED ---