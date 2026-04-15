import re
import os

def save_analysis_results(text, py_filename="replicated_model.py"):
    """
    Saves the full research analysis to a Markdown file and 
    extracts the Python code to a .py file.
    """
    # Create an 'outputs' directory if it doesn't exist
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    # 1. Save the full raw text (including reasoning, math, and code)
    md_filename = py_filename.replace(".py", "_analysis.md")
    md_path = os.path.join("outputs", md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"📄 Full analysis saved to: {md_path}")

    # 2. Extract and save only the Python code block
    py_path = os.path.join("outputs", py_filename)
    code_match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if code_match:
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(code_match.group(1))
        print(f"✅ Executable code saved to: {py_path}")
    else:
        print("⚠️ Note: No Python code block found to extract.")