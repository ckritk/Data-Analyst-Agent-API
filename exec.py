import subprocess
import sys
import tempfile
import os
from typing import Dict, Any, Optional
import json


def execute_python_code(code: str, timeout: int = 50, capture_stderr: bool = True, 
                       working_directory: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Python code as a subprocess and return results or errors in a specific format.
    
    Args:
        code: Python code string to execute
        timeout: Maximum execution time in seconds (default: 30)
        capture_stderr: Whether to capture stderr separately (default: True)
        working_directory: Working directory for the subprocess (default: None)
    
    Returns:
        Dict containing:
        - success: bool (True if execution successful, False if error)
        - output: str (stdout output from the code)
        - error: str (error message if any)
        - error_type: str (type of error: 'execution', 'timeout', 'system')
        - return_code: int (subprocess return code)
        - execution_time: float (approximate execution time)
    """
    import time
    
    # Initialize result structure
    result = {
        "success": False,
        "output": "",
        "error": "",
        "error_type": None,
        "return_code": None,
        "execution_time": 0.0
    }
    
    # Validate input
    if not isinstance(code, str) or not code.strip():
        result["error"] = "Invalid or empty code provided"
        result["error_type"] = "input_validation"
        return result
    
    temp_file = None
    start_time = time.time()
    
    try:
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            temp_file = f.name
            f.write(code)
        
        # Prepare subprocess command
        cmd = [sys.executable, temp_file]
        
        # Execute the code
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_directory,
            encoding='utf-8',
            errors='replace'
        )
        
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 3)
        result["return_code"] = process.returncode
        
        # Process results
        if process.returncode == 0:
            # Successful execution
            result["success"] = True
            result["output"] = process.stdout if process.stdout else ""
            
            # Include stderr in output if it contains warnings (not errors)
            if process.stderr and capture_stderr:
                stderr_content = process.stderr.strip()
                if stderr_content:
                    # If there's stderr content but return code is 0, treat as warnings
                    if result["output"]:
                        result["output"] += f"\n[WARNINGS]\n{stderr_content}"
                    else:
                        result["output"] = f"[WARNINGS]\n{stderr_content}"
        else:
            # Execution failed
            result["success"] = False
            result["error_type"] = "execution"
            result["output"] = process.stdout if process.stdout else ""
            
            # Format error message
            error_msg = process.stderr if process.stderr else "Unknown execution error"
            result["error"] = f"Execution failed (return code: {process.returncode})\n{error_msg.strip()}"
    
    except subprocess.TimeoutExpired:
        # Timeout error
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 3)
        result["success"] = False
        result["error_type"] = "timeout"
        result["error"] = f"Code execution timed out after {timeout} seconds"
        result["return_code"] = -1
    
    except PermissionError as e:
        # Permission error
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 3)
        result["success"] = False
        result["error_type"] = "system"
        result["error"] = f"Permission error: {str(e)}"
        result["return_code"] = -1
    
    except Exception as e:
        # Other system errors
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 3)
        result["success"] = False
        result["error_type"] = "system"
        result["error"] = f"System error: {str(e)}"
        result["return_code"] = -1
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                # If cleanup fails, add note to result
                if result["error"]:
                    result["error"] += f"\n[Cleanup warning: Could not delete temp file: {e}]"
                else:
                    result["error"] = f"Cleanup warning: Could not delete temp file: {e}"
    
    return result


def execute_python_code_simple(code: str, timeout: int = 30) -> str:
    """
    Simplified version that returns just the output string or error message.
    
    Args:
        code: Python code string to execute
        timeout: Maximum execution time in seconds
    
    Returns:
        String containing output or error message
    """
    result = execute_python_code(code, timeout)
    
    if result["success"]:
        return result["output"] if result["output"] else "[No output]"
    else:
        return f"ERROR ({result['error_type']}): {result['error']}"


def execute_python_file(file_path: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a Python file and return results in the same format.
    
    Args:
        file_path: Path to Python file to execute
        timeout: Maximum execution time in seconds
    
    Returns:
        Same format as execute_python_code()
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        return execute_python_code(code, timeout)
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Could not read file {file_path}: {str(e)}",
            "error_type": "file_read",
            "return_code": -1,
            "execution_time": 0.0
        }

# Example usage and testing
if __name__ == "__main__":
    print("=== Python Code Executor Test ===\n")
    
    # Test 1: Successful execution
    print("Test 1: Successful execution")
    code1 = """
print("Hello, World!")
print("This is a test")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
    result1 = execute_python_code(code1)
    print("Result:", json.dumps(result1, indent=2))
    print()
    
    # Test 2: Code with error
    print("Test 2: Code with syntax error")
    code2 = """
print("This will work")
print("But this will fail"
# Missing closing parenthesis
"""
    result2 = execute_python_code(code2)
    print("Result:", json.dumps(result2, indent=2))
    print()
    
    # Test 3: Runtime error
    print("Test 3: Runtime error")
    code3 = """
print("Starting execution")
x = 1 / 0  # Division by zero
print("This won't print")
"""
    result3 = execute_python_code(code3)
    print("Result:", json.dumps(result3, indent=2))
    print()
    
    # Test 4: Code that takes time (but within timeout)
    print("Test 4: Code with delay")
    code4 = """
import time
print("Starting...")
time.sleep(1)
print("Finished after 1 second")
"""
    result4 = execute_python_code(code4, timeout=5)
    print("Result:", json.dumps(result4, indent=2))
    print()
    
    # Test 5: Using simplified function
    print("Test 5: Using simplified function")
    code5 = """
for i in range(3):
    print(f"Count: {i}")
"""
    simple_result = execute_python_code_simple(code5)
    print("Simple result:", repr(simple_result))
    print()
    
    # Test 6: Code with warnings
    print("Test 6: Code with warnings")
    code6 = """
import warnings
warnings.warn("This is a warning", UserWarning)
print("Code executed successfully despite warning")
"""
    result6 = execute_python_code(code6)

    print("Result:", json.dumps(result6, indent=2))

