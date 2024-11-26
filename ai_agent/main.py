from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from prompts import agent_context, code_parser_template
from code_reader import code_reader
from dotenv import load_dotenv
import ast
import os
# need to get API for llama parser
load_dotenv()

llm = Ollama(model="mistral", request_timeout=300.0)

# setting up parser
parser = LlamaParse(result_type="markdown")

file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# passing the documents to the embed model
embed_model = resolve_embed_model("local:BAAI/bge-m3") #using local model instead chatgpt
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

#wrapping in query engine to be used
query_engine = vector_index.as_query_engine(llm=llm)

tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="This tool gives documentation about the API. Use this for reading docs for the API."
        )
    ),
    code_reader
]

# code generation llm
code_llm = Ollama(model="codellama")
agent = ReActAgent.from_tools(tools, llm=code_llm,  verbose=True, context=agent_context)

# creating code output llm which will analyze the code llm output

class CodeOuput(BaseModel):
    code: str
    description: str
    filename: str


parser = PydanticOutputParser(CodeOuput)
json_prompt_str = parser.format(code_parser_template)

json_prompt_template = PromptTemplate(json_prompt_str)
output_pipeline = QueryPipeline(chain=[json_prompt_template, llm])

while (prompt := input("Enter a prompt (q to quit): ")) != "q":

    retries = 0
    while retries < 3:
        try:

            result = agent.query(prompt)
            next_result = output_pipeline.run(response=result)
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))
            print(cleaned_json)
            break
        except Exception as e:
            retries +=1
            print(f"Error occured, rety number {retries}")

    if retries >=3:
        print('Unable: try again')
        continue

    print("Code generated")

    print(cleaned_json["code"])
    print("\n\nDescription: ", cleaned_json["description"])

    filename = cleaned_json["filename"]

    try:
        with open(os.path.join("output", filename), "w") as f:
            f.write(cleaned_json["code"])
        print('Saved file', filename)
    except:
        print("Error saving the file")