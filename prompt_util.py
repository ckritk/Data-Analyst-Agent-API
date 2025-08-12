import re
from typing import Dict, List, Tuple, Optional

def load_prompt_template(file_path: str) -> str:
    """
    Load prompt template from a text file.
    
    Args:
        file_path: Path to the template file
    
    Returns:
        Template content as string
    
    Raises:
        FileNotFoundError: If template file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt template file not found: {file_path}")
    except Exception as e:
        raise IOError(f"Error reading template file {file_path}: {str(e)}")

def generate_prompt(question: str, prompt_type: str = "code", code: str = "", error: str = "", 
                   code_template_path: str = "prompts/code.txt", retry_template_path: str = "prompts/retry.txt", simple_llm_path = "prompts/simple.txt",
                   simulate_template_path = "prompts/simulate.txt", query_template_path = "prompts/query.txt", classify_template_path = "prompts/classify.txt") -> str:
    """
    Generate appropriate prompt based on type (code or retry) using external template files.
    
    Args:
        question: The coding question/task to solve
        prompt_type: Either "code" for initial code generation or "retry" for debugging
        code: Python code (required for retry prompt)
        error: Error message (required for retry prompt)
        code_template_path: Path to code generation template file (default: "code.txt")
        retry_template_path: Path to retry/debugging template file (default: "retry.txt")
    
    Returns:
        Formatted prompt string
    
    Raises:
        ValueError: If invalid prompt_type or missing required parameters
        FileNotFoundError: If template files don't exist
        IOError: If template files cannot be read
    """
    
    # Validate required parameters
    if not question or not question.strip():
        raise ValueError("question cannot be empty")
    
    if prompt_type == "code":
        # Load and format code generation template
        template = load_prompt_template(code_template_path)
        return template.format(question=question.strip())
    
    elif prompt_type == "retry":
        if not code or not code.strip():
            raise ValueError("code parameter is required for retry prompt")
        if not error or not error.strip():
            raise ValueError("error parameter is required for retry prompt")
        
        # Load and format retry template
        template = load_prompt_template(retry_template_path)
        return template.format(
            question=question.strip(),
            code=code.strip(),
            error=error.strip()
        )

    elif prompt_type == "simple_llm":
        # Load and format simple LLM template
        template = load_prompt_template(simple_llm_path)
        return template.format(question=question.strip())
    
    elif prompt_type == "simulate":
        # Load and format simulate template
        template = load_prompt_template(simulate_template_path)
        return template.format(question=question.strip())
    
    elif prompt_type == "query":
        # Load and format query template
        template = load_prompt_template(query_template_path)
        return template.format(question=question.strip())
    
    elif prompt_type == "classify":
        template = load_prompt_template(classify_template_path)
        return template.format(question=question.strip())
    
def extract_code_and_dependencies(llm_response: str) -> dict:
    try:
        code_match = re.search(r"```code\s*(.*?)```", llm_response, re.DOTALL)
        deps_match = re.findall(r"```dependencies\s*(.*?)```", llm_response, re.DOTALL)

        if not code_match:
            return {"success": False, "code": "", "dependencies": [], "error": "Code block not found"}

        code = code_match.group(1).strip()
        dependencies = []
        for dep_block in deps_match:
            dependencies.extend([line.strip() for line in dep_block.splitlines() if line.strip()])

        return {
            "success": True,
            "code": code,
            "dependencies": dependencies,
            "error": ""
        }

    except Exception as e:
        return {"success": False, "code": "", "dependencies": [], "error": str(e)}


# Example usage and testing
if __name__ == "__main__":
    print("=== LLM Prompt Generator and Parser Test ===\n")
    
    # Test 1: Generate code prompt (requires code.txt)
    print("Test 1: Generate initial code prompt")
    question1 = "Calculate the average of numbers in a CSV file"
    try:
        prompt1 = generate_prompt(question1, "code")
        print("Generated prompt preview:")
        print(prompt1[:200] + "..." if len(prompt1) > 200 else prompt1)
    except (FileNotFoundError, IOError) as e:
        print(f"Could not load template: {e}")
    print()
    
    # Test 2: Generate retry prompt (requires retry.txt)
    print("Test 2: Generate retry prompt")
    code_with_error = """
import pandas as pd
df = pd.read_csv('data.csv')
print(df.mean())
"""
    error_msg = "FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'"
    
    try:
        prompt2 = generate_prompt(question1, "retry", code_with_error, error_msg)
        print("Generated retry prompt preview:")
        print(prompt2[:300] + "..." if len(prompt2) > 300 else prompt2)
    except (FileNotFoundError, IOError) as e:
        print(f"Could not load template: {e}")
    print()
    
    # Test 3: Parse response with code and dependencies
    print("Test 3: Parse LLM response")
    sample_response = """
Here's the solution:

===CODE===
import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('data.csv')

# Calculate and print the average
average = df.select_dtypes(include=[np.number]).mean().mean()
print(average)

===DEPENDENCIES===
pandas
numpy
"""
    
    parsed = extract_code_and_dependencies(sample_response)
    print("Parsing result:")
    print(f"Success: {parsed['success']}")
    print(f"Code length: {len(parsed['code'])} characters")
    print(f"Dependencies: {parsed['dependencies']}")
    if parsed['error']:
        print(f"Error: {parsed['error']}")
    print()
    
    # Test 4: Parse response with alternative format
    print("Test 4: Parse response with code blocks")
    alt_response = """
I'll solve this step by step:

```python
import requests
import json

def fetch_data():
    response = requests.get('https://api.example.com/data')
    data = response.json()
    return data

result = fetch_data()
print(len(result))
```

===DEPENDENCIES===
- requests
- beautifulsoup4
"""
    
    parsed2 = extract_code_and_dependencies(alt_response)
    print("Alternative parsing result:")
    print(f"Success: {parsed2['success']}")
    print(f"Code preview: {parsed2['code'][:100]}...")
    print(f"Dependencies: {parsed2['dependencies']}")
    print()
    
    # Test 5: Error handling
    print("Test 5: Error handling")
    try:
        bad_prompt = generate_prompt("", "invalid_type")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    empty_parse = extract_code_and_dependencies("")
    print(f"Empty response parse - Success: {empty_parse['success']}, Error: {empty_parse['error']}")