var currentCode = {
    html: '<div class="card">\n  <h1>NEXUS Matrix Application</h1>\n  <p>Status: Operational</p>\n  <button onclick="pingSystem()">Ping System</button>\n</div>',
    css: 'body { background: #0d1117; color: #00ff00; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }\n.card { border: 1px solid #00ff00; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 0 15px rgba(0,255,0,0.2); }\nbutton { background: #00ff00; color: #000; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; cursor: pointer; }\nbutton:hover { opacity: 0.9; }',
    js: 'function pingSystem() {\n  alert("NEXUS System Response: 200 OK - All Nodes Online!");\n}'
};

var activeTab = 'html';

function switchTab(tab) {
    var editorElem = document.getElementById('codeEditor');
    if (editorElem) {
        currentCode[activeTab] = editorElem.value;
    }
    activeTab = tab;
    
    var tabs = document.querySelectorAll('.tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    var activeTabElem = document.getElementById('tab-' + tab);
    if (activeTabElem) {
        activeTabElem.classList.add('active');
    }
    if (editorElem) {
        editorElem.value = currentCode[activeTab];
    }
}

function updatePreview() {
    var frame = document.getElementById('previewFrame');
    if (!frame) return;
    var doc = frame.contentDocument || frame.contentWindow.document;
    doc.open();
    doc.write('<!DOCTYPE html><html><head><style>' + currentCode.css + '</style></head><body>' + currentCode.html + '<script>' + currentCode.js + '<\/script></body></html>');
    doc.close();
}

function updatePreviewFromEditor() {
    var editorElem = document.getElementById('codeEditor');
    if (editorElem) {
        currentCode[activeTab] = editorElem.value;
    }
    updatePreview();
}

// -------------------------------------------------------------
// LIVE BACKEND GENERATE ENGINE CALL (WITH ITERATIVE MODIFICATION)
// -------------------------------------------------------------
async function generateApp() {
    var promptInput = document.getElementById('appPrompt');
    if (!promptInput) return;
    var prompt = promptInput.value.trim();
    if (!prompt) return;

    var editorElem = document.getElementById('codeEditor');
    if (editorElem) {
        currentCode[activeTab] = editorElem.value;
    }

    var statusElem = document.getElementById('previewStatus');
    if (statusElem) {
        statusElem.innerText = "⏳ MODIFYING/BUILDING AI APP...";
        statusElem.style.color = "#ffff00";
    }

    try {
        var response = await fetch("https://ai-tek-finder.onrender.com/generate-app", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                prompt: prompt,
                current_html: currentCode.html,
                current_css: currentCode.css,
                current_js: currentCode.js
            })
        });

        if (!response.ok) {
            throw new Error("HTTP Status " + response.status);
        }

        var data = await response.json();

        currentCode.html = data.html || currentCode.html;
        currentCode.css = data.css || currentCode.css;
        currentCode.js = data.js || currentCode.js;

        if (editorElem) {
            editorElem.value = currentCode[activeTab];
        }
        updatePreview();

        if (statusElem) {
            statusElem.innerText = "● LIVE";
            statusElem.style.color = "#00ff00";
        }

    } catch (err) {
        console.error("Studio AI Generation Failed:", err);
        
        currentCode.html = '<div class="app-container">\n  <h2>' + prompt.toUpperCase() + '</h2>\n  <p>Connection Error to Backend Engine</p>\n</div>';
        currentCode.css = 'body { background: #050505; color: #ff0000; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }\n.app-container { border: 1px dashed #ff0000; padding: 25px; text-align: center; }';
        currentCode.js = '// Check Render connection';

        if (editorElem) {
            editorElem.value = currentCode[activeTab];
        }
        updatePreview();

        if (statusElem) {
            statusElem.innerText = "● OFFLINE / FALLBACK";
            statusElem.style.color = "#ff0000";
        }
    }
}

function loadPreset(type) {
    var promptInput = document.getElementById('appPrompt');
    if (!promptInput) return;

    if (type === 'pomodoro') {
        promptInput.value = "Build a 25-minute Pomodoro Timer with start and reset controls.";
    } else if (type === 'crypto') {
        promptInput.value = "Create a real-time crypto price card layout for SOL and BTC.";
    } else if (type === 'todo') {
        promptInput.value = "Build a lightweight Kanban task list with add and delete functionality.";
    }
    generateApp();
}

window.onload = function() {
    var editorElem = document.getElementById('codeEditor');
    if (editorElem) {
        editorElem.value = currentCode.html;
    }
    updatePreview();

    var canvas = document.getElementById('matrixCanvas'); 
    if (canvas) {
        var ctx = canvas.getContext('2d');
        canvas.height = window.innerHeight; 
        canvas.width = window.innerWidth;
        var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('');
        var drops = [];
        for (var i = 0; i < Math.floor(canvas.width / 16); i++) {
            drops[i] = 1;
        }

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ff00'; 
            ctx.font = 'bold 16px Courier New';
            for (var i = 0; i < drops.length; i++) {
                var char = letters[Math.floor(Math.random() * letters.length)];
                ctx.fillText(char, i * 16, drops[i] * 16);
                if (drops[i] * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0; 
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 35);
    }
};