from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import ollama
import fitz  # PyMuPDF
from prompts import AGENT_PROMPT
import os
import re
from dotenv import load_dotenv
from ollama import Client

# Use the environment variable we will set in the next step
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = Client(host=OLLAMA_URL, timeout=300.0)


load_dotenv() # load value from our environment variable file

API_KEY_CREDITS = {os.getenv("API_KEY"): 5} # the value are credits that are subtracted from everytime someone uses the API_KEY (not implemented)
print(API_KEY_CREDITS)
# MODEL = 'llama3.2'
# MODEL = 'mistral'
# MODEL = 'gemma3:1b'
MODEL = 'tinyllama'
MODEL = 'llama3.2:1b'

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/config")
async def get_config():
    # This sends the key from your .env to the browser
    return {
        "api_key": os.getenv("API_KEY"),
        "model_name": MODEL
        }

def verify_api_key(x_api_key: str = Header(None)):
    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return x_api_key

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return f.read()

# @app.post("/analyze")
# async def analyze_document(file: UploadFile = File(...)):
#     # 1. Extract text from PDF
#     content = await file.read()
#     doc = fitz.open(stream=content, filetype="pdf")
#     text = " ".join([page.get_text() for page in doc])
    
#     # 2. Define your PROMPT
#     PROMPT = AGENT_PROMPT.replace("{{RESEARCH_PAPER}}", text)

#     # 3. Call local Llama via Ollama
#     response = ollama.generate(model='llama3.2', prompt=PROMPT)
#     return {"analysis": response['response']}

def analyze_document(text):
    # This sets the strict rules
    system_instruction = (
        "You are a specialized research analyzer. "
        "Output ONLY the requested data. No chatter."
        "Your output must start IMMEDIATELY with the '**Summary**' section. "
        "Do not include any introductory remarks, preambles, or conversational filler. "
        "Do not acknowledge the instructions. Provide ONLY the requested structure."
        "Do not include (Bullet Points) or any (approx. 80 chars) or (approx. 180 wordss)"
        "Do not include any additional double stars ** other than around the 5 main listed section titles, Summary, Primary Focus, Authors, Main Ideas, Tables & Figures"
    )

    # This is your actual request
    user_prompt = f"""Analyze the following research paper:
    
    <research_paper>f
    {text}
    </research_paper>

    REQUIRED STRUCTURE:
    **Summary** : [Max 400 words]
    **Primary Focus** : [Max 100 chars]
    **Authors** : [List authors/titles]
    **Main Ideas** : [List ideas]
    **Tables & Figures** : [State counts and subjects]
    The 5 main listed section titles above should be surrounded by two stars **. For instance Summary should be **Summary**.
    Do not include any additional double stars ** other than around the 5 main listed section titles above
    """

    response = client.chat(model=MODEL, messages=[
        {'role': 'system', 'content': system_instruction},
        {'role': 'user', 'content': user_prompt},
    ])

    raw_text = response['message']['content']
    _, marker, clean_text = raw_text.partition("**Summary**")

    if marker:
        # print(marker + clean_text)
        return marker + clean_text
    
    return response['message']['content']


def parse_analysis(text):
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(text)
    print(text)
        # Regex breakdown:
    # \*\*(.*?)\*\*     -> Capture the title
    # (?:\s*\(.*?\))?   -> Ignore optional (parentheses)
    # [:\s]*            -> CONSUME any colons or whitespace (newlines/spaces) 
    #                      that immediately follow the title.
    # pattern = r'\*\*(.*?)\*\*(?:\s*\(.*?\))?[:\s]*'
    # pattern = r'(?:\*\*(.*?)\*\*|^([^:\n]+):)[:\s]*'
    pattern = r'(?:\*\*(.*?)\*\*|^([A-Z][^:\n\*\*]+):)[:\s]*'

    raw_parts = re.split(pattern, text, flags=re.MULTILINE)
    parsing_list  = [p.strip() for p in raw_parts if p and p.strip()]
    
    # re.split cuts the text into groups following the pattern and includes them in the list
    # strip() filter out empty strings and strip whitespace from each element using strip()
    # parsing_list = [part.strip() for part in re.split(pattern, text) if part.strip()]
    # folds that flat list into pairs to create a dictionary.
    parsing_dict = {parsing_list[i]: parsing_list[i+1] for i in range(0, len(parsing_list), 2)}
    
    return parsing_dict


# @app.post("/analyze")
# async def analyze_file(file: UploadFile = File(...)):
#     # Extract text from PDF
#     content = await file.read()
#     doc = fitz.open(stream=content, filetype="pdf")
#     text = " ".join([page.get_text() for page in doc])
    
#     analysis_text = analyze_document(text)
#     parsing_dict = {'Summary':'Summary', 
#                     'Primary Focus':'Primary Focus', 
#                     'Authors': 'Authors', 
#                     'Main Ideas': 'Main Ideas', 
#                     'Tables & Figures':'Tables & Figures'
#                     }
#     parsing_dict = parse_analysis(analysis_text)
#     titles = ['Summary', 'Primary Focus', 'Authors', 'Main Ideas', 'Tables & Figures']
    
#     return {
#             "analysis": analysis_text,
#             "summary": parsing_dict[titles[0]],
#             "primary_focus": parsing_dict[titles[1]],
#             "authors": parsing_dict[titles[2]],
#             "ideas": parsing_dict[titles[3]],
#             "tables_figures": parsing_dict[titles[4]],
#             }

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # Extract text from PDF
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    text = " ".join([page.get_text() for page in doc])
    
    analysis_text = analyze_document(text)
    return {
            "analysis": analysis_text,
            }