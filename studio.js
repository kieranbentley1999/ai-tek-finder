var currentCode = {
    html: '<div class="card">\n  <h1>NEXUS Matrix Application</h1>\n  <p>Status: Operational</p>\n  <button onclick="pingSystem()">Ping System</button>\n</div>',
    css: 'body { background: #0d1117; color: #00ff00; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }\n.card { border: 1px solid #00ff00; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 0 15px rgba(0,255,0,0.2); }\nbutton { background: #00ff00; color: #000; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; cursor: pointer; }\nbutton:hover { opacity: 0.9; }',
    js: 'function pingSystem() {\n  alert("NEXUS System Response: 200 OK - All Nodes Online!");\n}'
};

var activeTab = 'html';

function switchTab(tab) {
    currentCode[activeTab] = document.getElementById('codeEditor').value;
    activeTab = tab;
    
    var tabs = document.querySelectorAll('.tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('codeEditor').value = currentCode[activeTab];
}

function updatePreview() {
    var frame = document.getElementById('previewFrame');
    var doc = frame.contentDocument || frame.contentWindow.document;
    doc.open();
    doc.write('<!DOCTYPE html><html><head><style>' + currentCode.css + '</style></head><body>' + currentCode.html + '<script>' + currentCode.js + '<\/script></body></html>');
    doc.close();
}

function updatePreviewFromEditor() {
    currentCode[activeTab] = document.getElementById('codeEditor').value;
    updatePreview();
}

// -------------------------------------------------------------
// LIVE BACKEND GENERATE ENGINE CALL
// -------------------------------------------------------------
async function generateApp() {
    var prompt = document.getElementById('appPrompt').value.trim();
    if (!prompt) return;

    var statusElem = document.getElementById('previewStatus');
    statusElem.innerText = "⏳ GENERATING LIVE AI APP...";
    statusElem.style.color = "#ffff00";

    try {
        var response = await fetch("https://ai-tek-finder.onrender.com/generate-app", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!response.ok) {
            throw new Error("HTTP Status " + response.status);
        }

        var data = await response.json();

        currentCode.html = data.html || "<div>Error parsing HTML</div>";
        currentCode.css = data.css || "body { background: #000; color: #00ff00; }";
        currentCode.js = data.js || "// No JS returned";

        document.getElementById('codeEditor').value = currentCode[activeTab];
        updatePreview();

        statusElem.innerText = "● LIVE";
        statusElem.style.color = "#00ff00";

    } catch (err) {
        console.error("Studio AI Generation Failed:", err);
        
        // Fallback card if offline
        currentCode.html = '<div class="app-container">\n  <h2>' + prompt.toUpperCase() + '</h2>\n  <p>Connection Error to Backend Engine</p>\n</div>';
        currentCode.css = 'body { background: #050505; color: #ff0000; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }\n.app-container { border: 1px dashed #ff0000; padding: 25px; text-align: center; }';
        currentCode.js = '// Check Render connection';

        document.getElementById('codeEditor').value = currentCode[activeTab];
        updatePreview();

        statusElem.innerText = "● OFFLINE / FALLBACK";
        statusElem.style.color = "#ff0000";
    }
}

function loadPreset(type) {
    if (type === 'pomodoro') {
        document.getElementById('appPrompt').value = "Build a 25-minute Pomodoro Timer with start and reset controls.";
    } else if (type === 'crypto') {
        document.getElementById('appPrompt').value = "Create a real-time crypto price card layout for SOL and BTC.";
    } else if (type === 'todo') {
        document.getElementById('appPrompt').value = "Build a lightweight Kanban task list with add and delete functionality.";
    }
    generateApp();
}

window.onload = function() {
    document.getElementById('codeEditor').value = currentCode.html;
    updatePreview();

    // Matrix Background Effect
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