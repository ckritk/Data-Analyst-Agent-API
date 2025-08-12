from llm import call_grok, call_llm_with_fallback
from depend import manage_dependencies
from prompt_util import generate_prompt, extract_code_and_dependencies
from exec import execute_python_code

call_llm_classify = call_grok
call_llm_code = call_llm_with_fallback

def classify(question: str) -> str:
    prompt = generate_prompt(question,prompt_type="classify")
    class_ = call_llm_classify(prompt)
    if class_:
        return class_.strip()
    else:
        raise ValueError(f"Error classifying question: {question}")

def retry(question: str, code: str, error_msg: str, trial: int, max_trials=6) -> str:
    if trial >= max_trials:
        return f"Max retries reached. Last error: {error_msg}"
    
    prompt = generate_prompt(question, prompt_type="retry", code = code, error=error_msg)
    response = call_llm_code(prompt)
    result = extract_code_and_dependencies(response)
    #print(result)
    if not result["success"]:
        print()
        return f"Error generating retry prompt: {result['error']}"
    code, dependencies = result["code"], result["dependencies"]
    #print(code)

    manage_dependencies(dependencies)

    print(f"Retrying ({trial} attempts left)...")
    result = execute_python_code(code)
    
    if result["success"]:
        return result["output"]
    else:
        print(f"Retry failed: {result['error']}")
        return retry(question, code, result['error'], trial + 1)

def handle_execute_code_class(question: str):
    prompt = generate_prompt(question)
    response = call_llm_code(prompt)
    result = extract_code_and_dependencies(response)
    print(result)

    if not result["success"]: 
        return f"Error generating code: {result['error']}"
    
    code, dependencies = result["code"], result["dependencies"]

    manage_dependencies(dependencies)
    result = execute_python_code(code, dependencies)
    print(result)
    if not result["success"]:
        return retry(question, code, result['error_type']+result['error'],2)
    
def handle_generate_code_class(question):
    prompt = generate_prompt(question)
    response = call_llm_code(prompt)
    result = extract_code_and_dependencies(response)
    if not result["success"]:
        return f"Error generating code: {result['error']}"
    
    return result["code"]

def api_creation(question: str):
    pass

def simple_llm(question: str):
    prompt = generate_prompt(question, prompt_type="simple_llm")
    response = call_llm_code(prompt)
    return response.strip() if response else "No response from LLM"

def static_answer(question: str):
    prompt = generate_prompt(question, prompt_type="simulate")
    response = call_llm_code(prompt)
    return response.strip() if response else "No response from LLM"

def query_only(question: str):
    prompt = generate_prompt(question, prompt_type="query")
    response = call_llm_code(prompt)
    return response.strip() if response else "No response from LLM"

def other(question: str):
    prompt = generate_prompt(question)
    response = call_llm_code(prompt)
    result = extract_code_and_dependencies(response)
    print(result)

    if not result["success"]: 
        return f"Error generating code: {result['error']}"
    
    code, dependencies = result["code"], result["dependencies"]

    manage_dependencies(dependencies)
    result = execute_python_code(code, dependencies)
    print(result)
    if not result["success"]:
        return retry(question, code, result['error_type']+result['error'],2)


if __name__ == "__main__":
    from global_var import QUESTIONS
    question = QUESTIONS[0]
    
    print("\n--- handle_execute_code_class ---")
    output = handle_execute_code_class(question)
    print("Output:", output)
