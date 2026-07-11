from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os  # Standard library to securely read environment variables
from google import genai

app = FastAPI()

# Securely pull the key from the system environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_and_analyze(query: str):
    # 1. Pull the top 5 raw results from GitHub to give the AI good choices
    github_url = f"https://api.github.com/search/repositories?q={query}&per_page=5"
    
    try:
        github_response = requests.get(github_url).json()
        items = github_response.get('items', [])
        
        if not items:
            return {"results": "[-] NO TEK FOUND IN THE MATRIX DATABASE."}
        
        # 2. Package the GitHub data for the AI
        raw_data_for_ai = ""
        for repo in items:
            raw_data_for_ai += f"Name: {repo['name']}\nDescription: {repo['description']}\nURL: {repo['html_url']}\nStars: {repo['stargazers_count']}\n\n"
        
        # 3. Upgraded Prompt forcing a Top 3 Ranking System with Scores
        ai_prompt = f"""
        You are a Cyber AI Terminal Agent inside the Matrix. 
        A user is looking for code/technology related to: "{query}".
        
        Here is the raw data scraped from GitHub:
        {raw_data_for_ai}
        
        Your task:
        1. Evaluate the data and choose the top 3 best matching repositories.
        2. Rank them as RANK #1, RANK #2, and RANK #3.
        3. Assign each a compatibility score out of 100 based on how well it answers the user's query and its popularity (stars).
        4. Write a brief, sharp, hacker-style reason explaining why it earned that spot.
        5. Provide a direct, clean hyperlink to the code repo using this HTML format: <a href="URL" target="_blank" style="color: #00FF33; font-weight: bold;">[ACCESS SOURCE CODE]</a>
        
        Structure your entire response cleanly using HTML line breaks (<br>) so it reads perfectly inside a terminal box. 
        Start immediately with your evaluation.
        """
        
        # 4. Run it through the Gemini Brain
        ai_response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=ai_prompt,
        )
        
        return {"results": ai_response.text}
        
    except Exception as e:
        return {"results": f"[-] CRITICAL ENGINE ERROR: {str(e)}"}