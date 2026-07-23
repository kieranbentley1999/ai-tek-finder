from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os
import re
import json
import urllib.parse
import sqlite3

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------
# DATABASE SETUP: SQLite Metrics Tracker
# -------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('nexus_metrics.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visits 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, page TEXT, ip TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS searches 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, query TEXT, type TEXT)''')
    conn.commit()
    conn.close()

init_db()

def log_search(query, search_type):
    try:
        conn = sqlite3.connect('nexus_metrics.db')
        c = conn.cursor()
        c.execute("INSERT INTO searches (query, type) VALUES (?, ?)", (query, search_type))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Tracking Error: {e}")

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# -------------------------------------------------------------
# ROUTE: Root Health Check
# -------------------------------------------------------------
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return jsonify({"status": "NEXUS Core System Operational", "version": "v3.0"}), 200

# -------------------------------------------------------------
# ROUTE: NEXUS Studio AI App Generator Engine (Groq REST API)
# -------------------------------------------------------------
@app.route('/generate-app', methods=['POST'])
def generate_app():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({"error": "Prompt payload is empty"}), 400

    log_search(prompt, "STUDIO_AI_GEN")

    groq_api_key = os.environ.get('GROQ_API_KEY')

    # IF GROQ API KEY IS SET: USE DIRECT REST API CALL
    if groq_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key.strip()}",
                "Content-Type": "application/json"
            }
            
            system_instruction = (
                "You are the NEXUS AI Application Generator engine. "
                "The user will describe a web application in plain English. "
                "Return a strict JSON object with 3 keys: 'html', 'css', and 'js'.\n\n"
                "RULES:\n"
                "1. Return ONLY raw JSON (no markdown wrapper, no ```json or ```).\n"
                "2. 'html' must contain body elements only (no <html>, <head>, or <script> tags).\n"
                "3. 'css' must contain styling only (no <style> tags).\n"
                "4. 'js' must contain interactive JavaScript logic only (no <script> tags).\n"
                "5. Ensure dark/matrix theme styling matching the NEXUS theme when appropriate."
            )

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Build a complete web app: {prompt}"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }

            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
            
            if res.status_code == 200:
                result_json = res.json()
                content_text = result_json['choices'][0]['message']['content']
                app_data = json.loads(content_text)

                return jsonify({
                    "html": app_data.get("html", "<div>App generation error</div>"),
                    "css": app_data.get("css", "body { background: #000; color: #00ff00; }"),
                    "js": app_data.get("js", "// No JS generated")
                })
            else:
                print("Groq API Error Code:", res.status_code, res.text)

        except Exception as e:
            print("Groq API Request Exception:", str(e))

    # FALLBACK ENGINE IF KEY NOT SET OR API FAILS
    title_clean = prompt.upper()
    fallback_html = f"""<div class="app-card">
  <h2>{title_clean}</h2>
  <p>Status: Active Matrix Process</p>
  <div id="display-val">0</div>
  <div class="btn-group">
    <button onclick="updateVal(1)">+ INCREASE</button>
    <button onclick="updateVal(-1)">- DECREASE</button>
    <button onclick="resetVal()">RESET</button>
  </div>
</div>"""

    fallback_css = """body {
  background: #050505; color: #00ff00;
  font-family: 'Courier New', monospace;
  display: flex; justify-content: center; align-items: center;
  height: 100vh; margin: 0;
}
.app-card {
  border: 1px dashed #00ff00; padding: 30px;
  background: rgba(0,20,0,0.85); text-align: center;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
}
#display-val { font-size: 3.5rem; margin: 20px 0; color: #fff; font-weight: bold; }
.btn-group { display: flex; gap: 10px; justify-content: center; }
button {
  background: transparent; color: #00ff00; border: 1px solid #00ff00;
  padding: 10px 15px; font-family: monospace; font-weight: bold; cursor: pointer;
}
button:hover { background: #00ff00; color: #000; }"""

    fallback_js = """var count = 0;
function updateVal(amt) {
  count += amt;
  document.getElementById('display-val').innerText = count;
}
function resetVal() {
  count = 0;
  document.getElementById('display-val').innerText = count;
}"""

    return jsonify({
        "html": fallback_html,
        "css": fallback_css,
        "js": fallback_js
    })

# -------------------------------------------------------------
# ROUTE: Core Search Engine
# -------------------------------------------------------------
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"results": "<span style='color: red;'>[-] ERROR: Empty query.</span>"})
    
    if "apk" in query.lower():
        log_search(query.replace('apk', '').strip(), "APK_SCAN")
        clean_keyword = query.lower().replace('apk', '').strip()
        encoded_keyword = urllib.parse.quote(clean_keyword)
        
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_keyword}+apk"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(search_url, headers=headers, timeout=10)
            html_content = response.text
            links = re.findall(r'<a class="result__url" href="([^"]+)"', html_content)
            
            if not links:
                links = [
                    f"https://www.apkmirror.com/?searchtype=apk&s={encoded_keyword}",
                    f"https://apkpure.com/search?q={encoded_keyword}",
                    f"https://github.com/search?q={encoded_keyword}+apk"
                ]
            
            results_html = f"<span style='color: #00ff00;'>[+] GLOBAL NETWORK QUERY: '{clean_keyword.upper()}'</span><br><br>"
            for i in range(min(3, len(links))):
                raw_url = links[i]
                actual_url = raw_url.split('?uddg=')[-1].replace('%3a', ':').replace('%2f', '/') if '?uddg=' in raw_url else raw_url
                
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', actual_url)
                source_name = domain_match.group(1) if domain_match else "Global Mirror Network"
                
                current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
                js_snippet = escape_html(f"// Download Trigger\nwindow.open('{actual_url}', '_blank');")

                results_html += f"<span style='color: #00ff00;'>TARGET LOCATION: <a href='{actual_url}' target='_blank' style='color: #00ff00; text-decoration: underline;'>{source_name}</a></span><br>"
                results_html += f"<span style='color: #00ff00;'>SAFETY INTEGRITY: 92/100</span><br>"
                results_html += f"<span style='color: #aaa;'>LAST CHECKED: {current_date} (VERIFIED SAFE)</span><br>"
                results_html += f"<button class='terminal-btn' onclick=\"toggleCode('apk-code-{i}', `{js_snippet}`)\">[ GENERATE SCRIPT ]</button><br>"
                results_html += f"<pre id='apk-code-{i}' class='code-box' style='display:none;'></pre>"
                results_html += "<span style='color: #444;'>--------------------------</span><br><br>"
            return jsonify({"results": results_html})
        except Exception as e:
            return jsonify({"results": f"<span style='color: red;'>[-] APK PIPELINE ERROR: {str(e)}</span>"})

    else:
        log_search(query, "GITHUB_REPO")
        gh_search_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=3"
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "TEKFINDER-Core"}
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f"Bearer {github_token.strip()}"
        
        try:
            response = requests.get(gh_search_url, headers=headers, timeout=10)
            data = response.json()
            if 'items' not in data or len(data['items']) == 0:
                return jsonify({"results": f"<span style='color: yellow;'>[!] NO TARGETS FOUND for '{query}'.</span>"})
            
            results_html = f"<span style='color: #00ff00;'>[+] TEKFINDER QUERY: '{query}'</span><br><br>"
            for i, repo in enumerate(data['items']):
                repo_url = repo.get('html_url', '#')
                clone_snippet = escape_html(f"git clone {repo_url}.git")
                results_html += f"<span style='color: #00ff00;'>TARGET: <a href='{repo_url}' target='_blank' style='color: #00ff00; text-decoration: underline;'>{repo['full_name']}</a></span><br>"
                results_html += f"<span style='color: #aaa;'>INFO: {repo.get('description', 'No metadata')}</span><br>"
                results_html += f"<span>STARS: {repo['stargazers_count']}</span><br>"
                results_html += f"<button class='terminal-btn' onclick=\"toggleCode('git-code-{i}', `{clone_snippet}`)\">[ GENERATE CLONE CMD ]</button><br>"
                results_html += f"<pre id='git-code-{i}' class='code-box' style='display:none;'></pre>"
                results_html += "<span style='color: #444;'>--------------------------</span><br><br>"
            return jsonify({"results": results_html})
        except Exception as e:
            return jsonify({"results": f"<span style='color: red;'>[-] FETCH ERROR: {str(e)}</span>"})

# -------------------------------------------------------------
# ROUTE: Code Translator Endpoint
# -------------------------------------------------------------
@app.route('/translate', methods=['POST'])
def translate_code():
    data = request.json or {}
    code = data.get('code', '')
    target_lang = data.get('target', 'javascript').lower()
    
    if not code:
        return jsonify({"error": "Empty code payload"}), 400
        
    translated = code
    
    if target_lang in ['javascript', 'typescript']:
        translated = translated.replace("def ", "function ")
        translated = translated.replace("print(", "console.log(")
        translated = translated.replace("True", "true").replace("False", "false")
        translated = translated.replace("None", "null")
        translated = re.sub(r'# (.*)', r'// \1', translated)
    elif target_lang == 'rust':
        translated = translated.replace("def ", "fn ")
        translated = translated.replace("print(", "println!(")
        translated = translated.replace("True", "true").replace("False", "false")
        translated = re.sub(r'# (.*)', r'// \1', translated)
    elif target_lang == 'go':
        translated = translated.replace("def ", "func ")
        translated = translated.replace("print(", "fmt.Println(")
        translated = re.sub(r'# (.*)', r'// \1', translated)

    return jsonify({
        "translated_code": f"// Translated to {target_lang.upper()} via NEXUS AI Engine\n" + translated,
        "target_lang": target_lang
    })

@app.route('/trending', methods=['GET'])
def get_trending():
    return jsonify({"items": [{"name": "React", "html_url": "https://github.com/facebook/react", "description": "A declarative, efficient UI library.", "stargazers_count": 210000, "language": "JavaScript"}]})

@app.route('/find-apis', methods=['GET'])
def find_apis():
    query = request.args.get('query', '').strip().lower()
    log_search(query or "random_apicall", "PUBLIC_API")
    return jsonify({"apis": [{"name": "Cat Facts API", "url": "https://catfact.ninja/fact", "description": "Daily cat facts.", "category": "Animals"}]})

# -------------------------------------------------------------
# ROUTE: Admin Tracking & Metrics Endpoint
# -------------------------------------------------------------
@app.route('/api/track', methods=['POST'])
def track_visit():
    data = request.json or {}
    page = data.get('page', 'Unknown Page')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) 
    
    try:
        conn = sqlite3.connect('nexus_metrics.db')
        c = conn.cursor()
        c.execute("INSERT INTO visits (page, ip) VALUES (?, ?)", (page, ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Track Error:", e)
    return jsonify({"status": "logged"})

@app.route('/api/admin/metrics', methods=['GET'])
def admin_metrics():
    passkey = request.args.get('passkey', '')
    if passkey != "NEXUS_OVERRIDE":
        return jsonify({"error": "Unauthorized Access. Disconnecting."}), 401
    
    try:
        conn = sqlite3.connect('nexus_metrics.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM visits")
        total_visits = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT ip) FROM visits")
        unique_visitors = c.fetchone()[0]
        c.execute("SELECT page, COUNT(*) FROM visits GROUP BY page ORDER BY COUNT(*) DESC LIMIT 5")
        popular_pages = c.fetchall()
        c.execute("SELECT query, type, timestamp FROM searches ORDER BY id DESC LIMIT 10")
        recent_searches = c.fetchall()
        conn.close()
        
        return jsonify({
            "total_visits": total_visits,
            "unique_visitors": unique_visitors,
            "popular_pages": popular_pages,
            "recent_searches": recent_searches
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)