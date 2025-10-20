from langchain_groq import ChatGroq

def get_qa_llm():
    """
    Initialize and return the LLM for Short Q&A.
    (Using the model from your short_qa.ipynb)
    """
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)
    return llm

def get_mcq_llm():
    """
    Initialize and return the LLM for MCQs. 
    (Using the model from your mcq.ipynb)
    """
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)
    return llm