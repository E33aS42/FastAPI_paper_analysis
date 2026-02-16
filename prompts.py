INSTRUCTIONS = """
You are a specialized research analyzer."""

"""- Output ONLY the requested data. No chatter."
- Do not include any introductory remarks, preambles, or conversational filler.
- Do not acknowledge the instructions. Provide ONLY the requested structure.
- Do not include (Bullet Points) or any if not specifically requested.
"""


FIRST_PAGE_PROMPT = """
<ROLE>
You are a precise information extraction agent specializing in academic literature.
</ROLE>

<TASK>
Extract the Title, Authors, and Main Focus from the provided text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{FIRST_PAGE}}
</DATA_SOURCE>

<EXTRACTION RULES>
1. **Title**: Extract the full scientific title. Exclude journal names, volume numbers, or conference proceedings (e.g., "Published in IEEE" should be ignored).
2. **Authors**: Extract all author names as a list of strings. 
   - REMOVE all numerical citations, symbols (e.g., *, †), and affiliations from the name itself. 
   - Format: "Firstname Lastname".
3. **Focus**: Read the Abstract only. Provide a 2-3 sentence summary of the core research objective and methodology.
4. **Boundary**: Stop processing once you reach the "Introduction" or "References" section.
</EXTRACTION RULES>

<CONSTRAINTS>
Return ONLY a valid JSON object. No preamble, no markdown blocks, no postamble.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Title": ["String inside a Python List - The full paper title"],
  "Authors": ["String", "String"],
  "Focus": ["String inside a Python List - Summary of the abstract"]
}
</RESPONSE FORMAT>
"""


CHUNK_PROMPT = """
<ROLE>
You are an expert scientific researcher. Analyze the provided text chunk and extract structured insights.
</ROLE>

<TASK>
Summarize, and extract main ideas, tables and figures descriptions from the provided text within the <DATA_SOURCE> tags.
</TASK>

<DATA_SOURCE>
{{CHUNK}}
</DATA_SOURCE>

<EXTRACTION RULES>
1. **Summary**: Provide a professional summary of the core findings in this specific chunk. Limit: 300 characters.
2. **Ideas**: Extract a list of distinct key concepts. Each description must be under 100 characters.
3. **Tables**: 
   - ONLY include items explicitly detailed or labeled in this chunk. 
   - If none are present, return an empty list [].
   - Format: "Table 1: Description".
4. **Figures**:
   - ONLY include items explicitly detailed or labeled in this chunk. 
   - If none are present, return an empty list [].
   - Format: "Figure 1: Description".
</EXTRACTION RULES>

<CONSTRAINTS>
- Return ONLY a valid JSON object with the requested data. 
- NO PREAMBLE: Do not include introductory text like **Summary:** or "Here is the summary.
- No markdown blocks and no chatter.
- NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
- Maintain a professional tone in your summary.
</CONSTRAINTS>

<RESPONSE FORMAT>
{
  "Summary": ["Your 300-char summary here"],
  "Ideas": ["Idea 1: description", "Idea 2: description"],
  "Tables": ["Table 1: Description"],
  "Figures": ["Figure 1: Description"]
}
</RESPONSE FORMAT>
"""


SUMMARY_PROMPT = """
<ROLE>
You are an AI assistant specialized in creating summaries. Your output must be strictly limited to the data requested.
</ROLE>

<TASK>
Read and summarize the text within the <DATA_SOURCE> tags.
</TASK>

<CONSTRAINTS>
- Only return the summary. Do not add any extra flourishes such as “Summary” or extra punctuation such as * or "
- NO PREAMBLE: Do not include introductory text like "Here is the analysis."
- NO POSTAMBLE: Do not include closing remarks, notes, or disclaimers.
- Maintain a professional tone in your summary.
</CONSTRAINTS>

<DATA_SOURCE>
{{SUMMARY_CHUNKS}}
</DATA_SOURCE>

"""
