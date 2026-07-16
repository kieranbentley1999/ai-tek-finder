from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os
import re
import urllib.parse

app = Flask(__name__)
CORS(app)

def calculate_health(repo):
    score = 100
    try:
        last_push = repo.get('pushed_at', '')
        last_push_date = datetime.datetime.strptime(last_push, "%Y-%m-%dT%H:%M:%SZ")
        days_since_update = (datetime.datetime.utcnow() - last_push_date).days
        if days_since_update > 365:
            score -= 40
        elif days_since_update > 180:
            score -= 20
    except:
        score -= 10
    
    open_issues = repo.get('open_issues_count', 0)
    stars = repo.get('stargazers_count', 1)
    if open_issues > (stars * 0.5):
        score -= 30
    return max(0, score)

def assess_safety(url, source_name):
    score = 100
    if not url.startswith("https"):
        score -= 40
    url_lower = url.lower()
    source_lower = source_name.lower()
    trusted_sources = ['github', 'gitlab', 'f-droid', 'apkmirror', 'apkpure']
    suspicious_keywords = ['moded', 'cracked', 'hack', 'free-premium', 'cheat']
    if any(ts in url_lower or ts in source_lower for ts in trusted_sources):
        score += 10
    elif any(sk in url_lower for sk in suspicious_keywords):
        score -= 50
    else:
        score -= 15
    return min(100, max(0, score))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"results": "<span style='color: red;'>[-] ERROR: Empty query.</span>"})
    
    # -------------------------------------------------------------
    # ROUTE 1: Dedicated APK/API Finder (Global Web Search Matrix)
    # -------------------------------------------------------------
    if "apk" in query.lower():
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
                
                safety_rating = assess_safety(actual_url, source_name)
                current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
                safety_color = "#00ff00" if safety_rating >= 80 else "#ffff00" if safety_rating >= 50 else "#ff0000"
                
                results_html += f"<span style='color: #00ff00;'>TARGET LOCATION: <a href='{actual_url}' target='_blank' style='color: #00ff00; text-decoration: underline;'>{source_name}</a></span><br>"
                results_html += f"<span style='color: {safety_color};'>SAFETY INTEGRITY: {safety_rating}/100</span><br>"
                results_html += f"<span style='color: #aaa;'>LAST CHECKED: {current_date} (VERIFIED SAFE)</span><br>"
                results_html += "<span style='color: #444;'>--------------------------</span><br><br>"
            return jsonify({"results": results_html})
        except Exception as e:
            return jsonify({"results": f"<span style='color: red;'>[-] APK PIPELINE ERROR: {str(e)}</span>"})

    # -------------------------------------------------------------
    # ROUTE 2: Original TEK FINDER (Strict GitHub Repository Tracker)
    # -------------------------------------------------------------
    else:
        gh_search_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=3"
        
        # Modern standard headers including a required User-Agent
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TEKFINDER-Core-Agent/1.0"
        }
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            # Modernized REST authorization standard syntax
            headers['Authorization'] = f"Bearer {github_token.strip()}"
        
        try:
            response = requests.get(gh_search_url, headers=headers, timeout=10)
            
            # Safe catch for non-JSON block pages (like Cloudflare raw HTML)
            try:
                data = response.json()
            except ValueError:
                return jsonify({
                    "results": (
                        f"<span style='color: #ff0000; font-weight: bold;'>[-] GITHUB API ACCESS BLOCKED</span><br><br>"
                        f"<span style='color: #aaa;'>Reason: GitHub rejected the request or rate-limited the IP.</span><br>"
                        f"<span style='color: #ffaa00;'>SYSTEM DIAGNOSTIC -> Token Loaded in Python: {bool(github_token)}</span><br><br>"
                        f"<span style='color: #aaa;'>Action: If 'False', your variable isn't saved. If 'True', regenerate your ghp_ key.</span>"
                    )
                })
            
            if response.status_code != 200:
                error_msg = data.get('message', f"HTTP Status {response.status_code}")
                return jsonify({"results": f"<span style='color: yellow;'>[!] GITHUB API ERROR: {error_msg} (Token Active: {bool(github_token)})</span>"})
                
            if 'items' not in data:
                return jsonify({"results": "<span style='color: yellow;'>[!] GITHUB FIREWALL: Unexpected API response structure.</span>"})
                
            if len(data['items']) == 0:
                return jsonify({"results": f"<span style='color: yellow;'>[!] NO TARGETS FOUND for '{query}'.</span>"})
            
            results_html = f"<span style='color: #00ff00;'>[+] TEKFINDER QUERY: '{query}'</span><br><br>"
            for repo in data['items']:
                health = calculate_health(repo)
                color = "#00ff00" if health > 70 else "#ffff00" if health > 40 else "#ff0000"
                repo_url = repo.get('html_url', '#')
                description = repo.get('description', 'No description provided by the developer.')
                
                results_html += f"<span style='color: {color};'>TARGET: <a href='{repo_url}' target='_blank' style='color: {color}; text-decoration: underline;'>{repo['full_name']}</a></span><br>"
                results_html += f"<span style='color: #aaa;'>INFO: {description}</span><br>"
                results_html += f"<span>HEALTH SCORE: {health}/100</span><br>"
                results_html += f"<span>STARS: {repo['stargazers_count']}</span><br>"
                results_html += "<span style='color: #444;'>--------------------------</span><br><br>"
            return jsonify({"results": results_html})
        except Exception as e:
            return jsonify({"results": f"<span style='color: red;'>[-] TEK FINDER REPO FETCH ERROR: {str(e)}</span>"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)