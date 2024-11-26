from llama_index.core.tools import FunctionTool
import os

def codeReaderFunction(file_name):
    path = os.path.join("data", file_name)
    try:
        with open(path, "r") as f:
            content = f.read()
            return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}
    
code_reader = FunctionTool.from_defaults(
    fn=codeReaderFunction,
    name="code_reader",
    description="""this tool can read the contents of code files and return their retuls.
      Use this when you need the content of a file."""
)