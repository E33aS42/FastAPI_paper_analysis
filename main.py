
# to run the API from command line:
# > uvicorn main:app --reload

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import ollama
import fitz  # PyMuPDF
from prompts import INSTRUCTIONS, FIRST_PAGE_PROMPT, CHUNK_PROMPT, SUMMARY_PROMPT
import os
import re
from dotenv import load_dotenv
from ollama import Client
import json
import ast

# Use the Koyeb  environment variable
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = Client(host=OLLAMA_URL, timeout=300.0)

load_dotenv() # load value from our environment variable file

API_KEY_CREDITS = {os.getenv("API_KEY"): 5} # the value are credits that are subtracted from everytime someone uses the API_KEY (not implemented)
print(API_KEY_CREDITS)
# MODEL = 'llama3.2'
MODEL = 'Mistral-nemo'

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


def analyze_1st_page(text):
    system_instructions = (INSTRUCTIONS)
    PROMPT = FIRST_PAGE_PROMPT.replace("{{FIRST_PAGE}}", text)

    response = client.chat(
        model=MODEL, 
        messages=[
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': PROMPT},
        ],
        options={"num_ctx": 2048} # 2k tokens context window
    )

    return response['message']['content']


def parse_1stpage_analysis(text):
    with open("title_authors.txt", "w", encoding="utf-8") as file:
        file.write(text)
    pattern = r'[^a-zA-Z"-:.\[\]{}, ]'
    cleaned_text = re.sub(pattern, '', text)
    print("cleaned_text 1 :", cleaned_text)
    if not cleaned_text.endswith('}'):
        cleaned_text += '}'
        # print("cleaned_text 2 :", cleaned_text)
    cleaned_text = cleaned_text.replace("'", '"')
    parsing_dict = ast.literal_eval(cleaned_text)
    parsing_dict["Title"] = " ".join(parsing_dict["Title"])
    return parsing_dict


def analyze_chunk(text):
    system_instructions = (INSTRUCTIONS)
    PROMPT = CHUNK_PROMPT.replace("{{CHUNK}}", text)

    response = client.chat(
        model=MODEL, 
        messages=[
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': PROMPT},
        ],
        options={"num_ctx": 4096} # 4k tokens context window
    )

    return response['message']['content']


def compile_summary(text):
    system_instructions = (INSTRUCTIONS)
    PROMPT = SUMMARY_PROMPT.replace("{{SUMMARY_CHUNKS}}", text)

    response = client.chat(
        model=MODEL, 
        messages=[
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': PROMPT},
        ],
        options={"num_ctx": 2048} # 2k tokens context window
    )

    return response['message']['content']


def parse_chunk(text):
    parsing_dict = ast.literal_eval(text)
    if not parsing_dict.endswith('}'):
        cleaned_text += '}'
    print(parsing_dict)
    return parsing_dict


def renumber_items(item_list, label):
    new_list = []
    # Remove any item with 'None' that indicates there is no figure or table
    item_list = [item for item in item_list if "None" not in item]
    item_list = [item for item in item_list if "not" not in item]
    item_list = [item for item in item_list if "Not" not in item]
    for i, item in enumerate(item_list, 1):
        print(f"i={i}, item={item}")
        # looks for "label X:" 
        # and replaces it with the current index "label i:"
        dynamic_pattern = rf"{label} \d+:"
        new = f"{label} {i}:"

        # If the pattern exists in item, replace existing label with new label; otherwise, just keep the item
        new_item = re.sub(dynamic_pattern, new, item)
        print("new_item : ", new_item)
        new_list.append(new_item)
    return new_list


def extract_data(analysed_chunks):
    raw_summary = "\n".join(analysed_chunks['Summary'])
    summary = compile_summary(raw_summary)
    ideas = "\u2022 " + "\n\u2022 ".join(analysed_chunks['Main Ideas'])
    nb_tbl = len(analysed_chunks['Tables'])
    nb_fig = len(analysed_chunks['Figures'])
    if nb_tbl > 1:
        tables = f"{nb_tbl} tables were found :\n" + "\u2022 " + "\n\u2022 ".join(analysed_chunks['Tables']) + "\n"
    elif nb_tbl == 1:
        tables = f"{nb_tbl} table was found :\n" + "\u2022 " + "\n\u2022 ".join(analysed_chunks['Tables']) + "\n"
    else:
        tables = "No table were found\n"
    if nb_fig > 1:
        figures = f"{nb_fig} figures were found :\n" + "\u2022 " + "\n\u2022 ".join(analysed_chunks['Figures']) + "\n"
    elif nb_fig == 1:
        figures = f"{nb_fig} figure was found :\n" + "\u2022 " + "\n\u2022 ".join(analysed_chunks['Figures']) + "\n"
    else:
        figures = "No figure were found\n"

    return summary, ideas, tables + "\n" + figures


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("results.html", "r") as f:
        return f.read()

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # Check file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    # Check MIME Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid MIME type.")
    
    # Extract text from PDF
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    print(f"Type of file: {type(doc)}, number of pages: {len(doc)}")
    nb_pages = len(doc)

    # Analyze the first page to extract the title, authors, and main focus of the paper.
    page_0 = doc[0].get_text()
    first_page = analyze_1st_page(page_0)
    parse_1stpage = parse_1stpage_analysis(first_page)
    title, authors, focus = parse_1stpage["Title"], parse_1stpage["Authors"], parse_1stpage["Focus"]
    authors = ", ".join(authors)
    authors = re.sub(r'\d+', '', authors) # remove extra numbers
    authors = re.sub(r',\s*,', ', ', authors) # remove extra commas
    authors = authors.strip(' ,') # remove extra commas on the edges

    # Analyze paper in chunks, then regroup the findings
    group_pages = 3
    analysed_chunks = {"Summary" : [],  "Main Ideas" : [], "Tables" : [], "Figures" : []}
    for i in range(0, nb_pages, group_pages):
        chunk_text = ""
        for page_num in range(i, min(i + group_pages, nb_pages)):
            chunk_text += doc[page_num].get_text()
        chunk = analyze_chunk(chunk_text)
        if not chunk.endswith('}'):
            chunk += '}'
        print("chunk: \n", chunk)
        keys_list = list(analysed_chunks.keys())
        chunk = ast.literal_eval(chunk)
        analysed_chunks = {key: analysed_chunks[key] + chunk[key] for key in chunk}
    # print("analysed_chunks 1: ", analysed_chunks)
    keys_list = list(analysed_chunks.keys())
    if 'Tables' not in keys_list:
        analysed_chunks['Tables'] = []
    else:
        analysed_chunks['Tables'] = renumber_items(analysed_chunks['Tables'], "Table")
    if 'Figures' not in keys_list:
        analysed_chunks['Figures'] = []
    else:
        analysed_chunks['Figures'] = renumber_items(analysed_chunks['Figures'], "Figure")
    print("analysed_chunks 2: ", analysed_chunks)

    summary, ideas, tables_figures = extract_data(analysed_chunks)

    print(f"\nsummary\n\nideas:\n{ideas}\n\ntables & figures: \n{tables_figures}\n")
    return {
        "title": title,
        "authors": authors,
        "summary": summary,
        "primary_focus": focus,
        "ideas": ideas,
        "tables_figures": tables_figures,
    }
