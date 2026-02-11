FIRST_PAGE_PROMPT = """You are an AI assistant specialized in finding the title, authors nd paper main subject focus on the first page of a scientific paper. Your output must be strictly limited to the data requested.

### INSTRUCTIONS:
1. Find and Read title and authors within the <first_page> tags. Both title and Authors are located before the Abstract. You should stop trying to find title and authors when the Abstract starts. The title should not contained any reference to a journal or proceeding or similar words. The title is about a scientific subject. 
2. Read the abstract and find the paper main study focus. The abstract starts just after the authors have been listed and before the paper introduction. Do not read the introduction.
3. OUTPUT FORMAT: You must follow the structure below exactly. 
4. NO PREAMBLE: Do not include introductory text like "Here is the analysis."
5. NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.

<first_page>
{{FIRST_PAGE}}
</first_page>

6. You will return a python dictionary whose values will be the title and authors found.


### REQUIRED OUTPUT STRUCTURE:
{
	'Title': [Insert page title here as a list. The title should not contained any reference to a journal or proceeding or similar words. The title can present more than one line and the title should end just before Authors are found.],
	'Authors': [Insert here the list of authors found of the paper along with their respective job titles, if available. Authors' names should only contain letters. Names should NOT contain any NUMBERS or extra punctuation such as comma.],
	'Focus': [Insert here a summary of the abstract.]
} 

"""


INSTRUCTIONS = "You are a specialized research analyzer. "
"Output ONLY the requested data. No chatter."
"Do not include any introductory remarks, preambles, or conversational filler."
"Do not acknowledge the instructions. Provide ONLY the requested structure."
"Do not include (Bullet Points) or any if not specifically requested"


CHUNK_PROMPT = """You are an AI assistant specialized in analyzing research papers. Your output must be strictly limited to the data requested. 

### INSTRUCTIONS:
1. Read and analyze the text within the <chunk> tags.
2. OUTPUT FORMAT: You will return a Python dictionary. It will NOT be a JSON. You must follow the structure below exactly and fill the values of the dictionary as requested below. 
3. Do not add any extra flourishes or extra punctuation such as * or "
4. NO PREAMBLE: Do not include introductory text like "Here is the analysis."
5. NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
6. Maintain a professional tone in your summary.

<chunk>
{{CHUNK}}
</chunk>

### REQUIRED OUTPUT STRUCTURE:
{
"Summary" : [ Insert here as a Python list: a text summary as a single element list - max 300 chars ],

"Main Ideas" : [ Insert here as a Python list: List of main ideas discussed in the text with brief description - max 100 chars per idea ],

"Tables" : [ Insert here as a Python list: : List and number using the Table label any tables found in the text, with descriptions - max 100 chars per line.  If a table is mentionned in the study but not found in the current analyzed text, do not mentionned it. ],

"Figures" : [Insert here as a Python list: List any figures found in the text, with descriptions. Each Figure description should be preceded with the 'Figure' label and numbered as such: 'Figure 1 : description' - max 100 chars per line. If a figure is mentionned in the study but not found in the current analyzed text, do not mentionned it.],

}
"""

SUMMARY_PROMPT = """You are an AI assistant specialized in creating summaries. Your output must be strictly limited to the data requested. 

### INSTRUCTIONS:
1. Read and summarize the text within the <chunks> tags.
2. Only return the summary. Do not add any extra flourishes such as “Summary” or extra punctuation such as * or "
3. NO PREAMBLE: Do not include introductory text like "Here is the analysis."
4. NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
5. Maintain a professional tone in your summary.

<chunks>
{{SUMMARY_CHUNKS}}
</chunks>

"""
