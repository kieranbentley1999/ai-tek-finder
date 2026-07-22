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

function generateApp() {
    var prompt = document.getElementById('appPrompt').value.trim();
    if (!prompt) return;

    document.getElementById('previewStatus').innerText = "⏳ GENERATING APP...";
    document.getElementById('previewStatus').style.color = "#ffff00";

    setTimeout(function() {
        currentCode.html = '<div class="app-container">\n  <h2>' + prompt.toUpperCase() + '</h2>\n  <div id="counter">0</div>\n  <button onclick="increment()">Increment Counter</button>\n</div>';
        currentCode.css = 'body { background: #050505; color: #00ff00; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }\n.app-container { border: 1px dashed #00ff00; padding: 25px; text-align: center; background: rgba(0,20,0,0.8); }\n#counter { font-size: 3rem; margin: 15px 0; color: #fff; }\nbutton { background: transparent; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px; font-weight: bold; cursor: pointer; }\nbutton:hover { background: #00ff00; color: #000; }';
        currentCode.js = 'var count = 0;\nfunction increment() {\n  count++;\n  document.getElementById("counter").innerText = count;\n}';

        document.getElementById('codeEditor').value = currentCode[activeTab];
        updatePreview();

        document.getElementById('previewStatus').innerText = "● LIVE";
        document.getElementById('previewStatus').style.color = "#00ff00";
    }, 800);
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