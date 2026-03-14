import json
import base64
import os
import glob

# Ensure we are in the script's directory for asset loading
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Preparing assets (external)...")
bg_url = "menu-bg-preview.jpg"  # LIGHTWEIGHT PREVIEW
bg_master = "menu-bg.png"       # HIGH-RES MASTER (EXPORT ONLY)

# Dynamically find ALL fonts in the directory
font_files = glob.glob("*.ttf") + glob.glob("*.otf")
fonts = {}
for file in font_files:
    family_name = os.path.splitext(file)[0]
    fonts[family_name] = file

print(f"Registered {len(fonts)} fonts: {list(fonts.keys())}")

with open("raw_coords.json", "r", encoding="utf-8") as f:
    data = json.load(f)

width = data["width"]
height = data["height"]
spans = data["text_data"]

print("Generating HTML...")

# Generate Font CSS (Using relative URLs for speed + font-display: swap)
font_css = ""
for name, filename in fonts.items():
    font_css += f"""
@font-face {{
    font-family: '{name}';
    src: url('{filename}') format('truetype');
    font-display: swap;
}}
"""

# Generate Font Dropdown Options
font_options = ""
for name in sorted(fonts.keys()):
    display = name.replace('-', ' ').replace('_', ' ').title()
    font_options += f"        <option value=\"{name}\">{display}</option>\n"

html = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Menu Editor Pro - UX Final</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
{font_css}

/* ─── UI Font ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {{
    margin: 0; padding: 0;
    background: #000;
    color: #fff;
    font-family: 'Inter', sans-serif;
    overflow: hidden;
    height: 100vh;
}}

/* ─── THE VIEWPORT (Centering & Bi-Directional Scrolling) ─── */
#editor-viewport {{
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: auto; /* ENABLES BOTH SCROLLBARS */
    background: radial-gradient(circle at center, #1a1a2e 0%, #010101 100%);
    scroll-behavior: smooth;
}}

#centering-wrapper {{
    display: flex;
    justify-content: center; /* Initial center */
    align-items: center;    /* Initial center */
    width: 100%;
    min-width: min-content;
    min-height: 100%;
    padding: 250px; /* SPACE TO PAN AROUND CLIPPED EDGES */
    box-sizing: border-box;
}}

/* Custom Scrollbar Styling (Vibrant & Obvious) */
#editor-viewport::-webkit-scrollbar {{ width: 14px; height: 14px; }}
#editor-viewport::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.4); }}
#editor-viewport::-webkit-scrollbar-thumb {{ 
    background: #f1c40f; 
    border-radius: 7px; 
    border: 3px solid #000;
}}
#editor-viewport::-webkit-scrollbar-thumb:hover {{ background: #ffea00; }}

#scaler-wrapper {{
    position: relative;
    transform-origin: 0 0;
    transition: none;
    flex-shrink: 0;
    margin: auto; /* THE MAGIC FIX: Centers if small, aligns to start if large */
    display: block;
}}

#menu-container {{
    position: absolute;
    width: {width}px;
    height: {height}px;
    background-color: #fff;
    transform-origin: 0 0;
    transition: none;
    box-shadow: 0 0 150px rgba(0,0,0,0.9);
    left: 0; top: 0;
}}

#menu-bg {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 1;
    pointer-events: none;
}}

/* ─── TEXT ELEMENTS ─── */
.editable-text {{
    position: absolute;
    z-index: 2;
    white-space: nowrap;
    outline: none;
    cursor: pointer;
    line-height: 1.1;
    border: 1px solid transparent;
    padding: 0 2px;
}}

body.editing .editable-text {{ cursor: move; }}

.editable-text.selected {{
    border: 2px solid #f1c40f !important;
    background: rgba(241, 196, 15, 0.2) !important;
    box-shadow: 0 0 30px rgba(241, 196, 15, 0.8);
    z-index: 1000 !important;
    border-radius: 4px;
}}

/* ─── FLOATING UI ─── */
#fab {{
    position: fixed;
    bottom: 30px; right: 30px;
    width: 68px; height: 68px;
    border-radius: 34px;
    background: linear-gradient(135deg, #f1c40f, #ff6d00);
    border: none;
    color: #000;
    font-size: 28px;
    cursor: pointer;
    z-index: 10000;
    box-shadow: 0 12px 40px rgba(255,109,0,0.4);
    display: flex; align-items: center; justify-content: center;
    transition: 0.3s;
}}
#fab.open {{ transform: rotate(45deg); background: #e74c3c; color: #fff; }}

#bottom-drawer {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(5, 5, 20, 0.99);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border-top: 1px solid rgba(255,255,255,0.1);
    border-radius: 28px 28px 0 0;
    padding: 15px 30px 40px;
    z-index: 9999;
    transform: translateY(0);
    transition: transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
    display: flex; flex-direction: column; gap: 15px;
}}
#bottom-drawer.closed {{ transform: translateY(100%); }}

.drawer-handle {{ width: 60px; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 auto 15px; cursor: pointer; }}

.btn-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}

.btn-ui {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 16px;
    border-radius: 16px;
    font-size: 15px; font-weight: 700;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 10px;
    transition: 0.2s;
}}
.btn-ui.primary {{ background: #f1c40f; color: #000; border: none; }}
.btn-ui:active {{ transform: scale(0.96); opacity: 0.8; }}

/* ─── SELECTION BAR ─── */
#selection-bar {{
    position: fixed;
    bottom: 130px;
    left: 50%;
    transform: translateX(-50%) translateY(300%);
    background: rgba(15, 15, 30, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 40px;
    padding: 12px 24px;
    display: flex; align-items:center; gap: 16px;
    z-index: 9998;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8);
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: 1px solid rgba(241,196,15,0.3);
    max-width: 95vw;
    overflow-x: auto;
}}
#selection-bar.show {{ transform: translateX(-50%) translateY(0); }}

.bar-ctrl-btn {{
    width: 40px; height: 40px;
    border-radius: 20px;
    background: rgba(255,255,255,0.1);
    border: none; color: #fff;
    font-size: 16px;
    cursor: pointer;
    display: flex; align-items:center; justify-content:center;
    flex-shrink: 0;
}}
.bar-ctrl-btn:active {{ background: #f1c40f; color: #000; }}

.color-swatch {{
    width: 30px; height: 30px;
    border-radius: 15px;
    border: 2px solid rgba(255,255,255,0.2);
    cursor: pointer;
    transition: 0.2s;
}}
.color-swatch:hover {{ transform: scale(1.3); border-color: #fff; }}

/* Custom Scrollbar for Selection Bar (Essential for Mobile Discovery) */
#selection-bar::-webkit-scrollbar {{ height: 8px; }}
#selection-bar::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.05); border-radius: 4px; }}
#selection-bar::-webkit-scrollbar-thumb {{ background: #ff6d00; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); }}

#scroll-hint {{
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    background: #ff6d00;
    color: #000;
    padding: 6px 12px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: 700;
    pointer-events: none;
    animation: bounceRight 1s infinite;
    z-index: 100;
    white-space: nowrap;
    display: none;
}}

@keyframes bounceRight {{
    0%, 100% {{ transform: translateY(-50%) translateX(0); }}
    50% {{ transform: translateY(-50%) translateX(5px); }}
}}

@media (max-width: 600px) {{
    #selection-bar {{
        bottom: 160px; /* Move up slightly to avoid reaching browser controls */
        padding: 10px 16px;
        gap: 12px;
        border-radius: 25px;
    }}
    #edit-controls {{ gap: 12px !important; }}
    .bar-ctrl-btn {{ width: 38px; height: 38px; font-size: 15px; }}
    #bar-font-family {{ max-width: 130px; padding: 6px 10px; font-size: 13px; }}
    .color-swatch {{ width: 26px; height: 26px; }}
}}

@media print {{
    #fab, #bottom-drawer, #selection-bar {{ display: none !important; }}
    #editor-viewport {{ overflow: visible; display: block; }}
    #centering-wrapper {{ padding: 0; min-width: auto; min-height: auto; }}
    #scaler-wrapper {{ transform: none !important; margin: 0; }}
}}
</style>
</head>
<body>

<div id="editor-viewport">
    <div id="centering-wrapper">
        <div id="scaler-wrapper">
            <div id="menu-container">
                <img id="menu-bg" src="{bg_url}" alt="Background" />
"""]

# Map PDF data to elements
for i, span in enumerate(spans):
    font_family = "century-gothic-regular"
    orig_f = span["font"].lower()
    if "bolditalic" in orig_f or "italicbold" in orig_f: font_family = "century-gothic-bold-italic"
    elif "bold" in orig_f: font_family = "century-gothic-bold"
    elif "bernard" in orig_f: font_family = "bernard-mt-condensed-regular"
    
    color = f"#{span['color']:06x}" if span['color'] > 0 else "#000000"
    if span['color'] == 16777215: color = "#ffffff"
    
    div = (f'            <div id="text_{i}" class="editable-text" contenteditable="false" spellcheck="false" '
           f'style="left: {span["bbox"][0]}px; top: {span["bbox"][1]}px; '
           f'font-family: \'{font_family}\'; font-size: {span["size"]}px; color: {color};"> '
           f'{span["text"]}</div>')
    html.append(div)

html.append(f"""
            </div>
        </div>
    </div>
</div>

<button id="fab" class="open">☰</button>

<div id="bottom-drawer">
    <div class="drawer-handle" id="btn-close-drawer"></div>
    <div class="btn-row">
        <button id="btn-toggle-edit" class="btn-ui primary">✏️ Edit Mode</button>
        <button id="btn-save" class="btn-ui">💾 Save Session</button>
        <button id="btn-load" class="btn-ui">📂 Load Session</button>
        <button id="btn-lock" class="btn-ui">🔓 Layout Unlocked</button>
        <button id="btn-add-text" class="btn-ui">＋ Add Text</button>
        <button id="btn-png" class="btn-ui">⬇️ Export Pro PNG</button>
        <button id="btn-reset" class="btn-ui">↺ Reset All</button>
    </div>
</div>

<div id="selection-bar">
    <div id="scroll-hint">Scroll for more ➔</div>
    <div id="edit-hint" style="color: #f1c40f; font-weight: 600; padding: 10px 20px;">
        👆 Click any text to edit it
    </div>
    <div id="edit-controls" style="display: none; align-items:center; gap:16px;">
    <div style="display:flex; align-items:center; gap:10px; border-right:1px solid rgba(255,255,255,0.1); padding-right:15px;">
        <select id="bar-font-family" style="background:#111; color:#fff; border:1px solid #444; border-radius:20px; padding:8px 12px; font-size:13px;">
{font_options}
        </select>
    </div>
    
    <div style="display:flex; align-items:center; gap:12px; border-right:1px solid rgba(255,255,255,0.1); padding-right:15px;">
        <div class="color-swatch" style="background:#ffffff;" title="White" onclick="setColor('#ffffff')"></div>
        <div class="color-swatch" style="background:#000000;" title="Black" onclick="setColor('#000000')"></div>
        <div class="color-swatch" style="background:#e74c3c;" title="Red" onclick="setColor('#e74c3c')"></div>
        <div class="color-swatch" style="background:#ff6d00;" title="Vibrant Orange" onclick="setColor('#ff6d00')"></div>
        <input type="color" id="color-custom" style="width:32px; height:32px; padding:0; border:none; background:none; cursor:pointer;" onchange="setColor(this.value)">
    </div>

    <div style="display:flex; align-items:center; gap:10px;">
        <button class="bar-ctrl-btn" id="btn-zoom-out">🔍−</button>
        <button class="bar-ctrl-btn" id="btn-zoom-in">🔍＋</button>
    </div>

    <div style="display:flex; align-items:center; gap:8px; margin: 0 4px; border-left:1px solid rgba(255,255,255,0.1); padding-left:15px;">
        <button class="bar-ctrl-btn" id="btn-size-down">−</button>
        <span id="label-size" style="color:#f1c40f; font-weight:700; font-size:16px; min-width:28px; text-align:center;">16</span>
        <button class="bar-ctrl-btn" id="btn-size-up">＋</button>
    </div>

    <div style="display:flex; align-items:center; gap:8px; border-left:1px solid rgba(255,255,255,0.1); padding-left:15px;">
        <button class="bar-ctrl-btn" id="btn-nudge-left">←</button>
        <button class="bar-ctrl-btn" id="btn-nudge-up">↑</button>
        <button class="bar-ctrl-btn" id="btn-nudge-down">↓</button>
        <button class="bar-ctrl-btn" id="btn-nudge-right">→</button>
    </div>

    <div style="display:flex; align-items:center; gap:8px; border-left:1px solid rgba(255,255,255,0.1); padding-left:15px;">
        <button class="bar-ctrl-btn" id="btn-track-down">↔−</button>
        <button class="bar-ctrl-btn" id="btn-track-up">↔＋</button>
    </div>

    <button class="bar-ctrl-btn" style="background:#e74c3c; margin-left:15px;" id="btn-delete">🗑</button>
    </div>
</div>

<script>
// ─── STATE ───
let isEditing = false;
let layoutLocked = false;
let selectedElement = null;
let zoomScale = 1;
let sessionLoaded = false; 
let isSaving = false;

const viewport = document.getElementById('editor-viewport');
const scaler = document.getElementById('scaler-wrapper');
const container = document.getElementById('menu-container');
const fab = document.getElementById('fab');
const drawer = document.getElementById('bottom-drawer');
const selBar = document.getElementById('selection-bar');

const CONFIG = {{
    name: "Menu Editor Pro",
    width: {width},
    height: {height},
    dpi: 300,
    priceColumn: 760, 
    snapGrid: 10,
    bgMaster: "{bg_master}" // High-res master for export only
}};

const originalWidth = CONFIG.width;
const originalHeight = CONFIG.height;

// ─── TRANSFORMS ───
function updateTransform() {{
    scaler.style.width = (originalWidth * zoomScale) + 'px';
    scaler.style.height = (originalHeight * zoomScale) + 'px';
    container.style.transform = `scale(${{zoomScale}})`;
    void viewport.scrollWidth; 
}}

function fitToScreen() {{
    if(sessionLoaded) return;
    const sW = window.innerWidth;
    const sH = window.innerHeight;
    const scaleW = (sW * 0.8) / originalWidth;
    const scaleH = (sH * 0.8) / originalHeight;
    zoomScale = Math.min(scaleW, scaleH);
    updateTransform();
    
    setTimeout(() => {{
        if(sessionLoaded) return;
        viewport.scrollLeft = (viewport.scrollWidth - sW) / 2;
        viewport.scrollTop = (viewport.scrollHeight - sH) / 2;
    }}, 50);
}}
window.addEventListener('resize', fitToScreen);
setTimeout(fitToScreen, 150);

function applyZoom(factor, centerX, centerY) {{
    const oldScale = zoomScale;
    zoomScale = Math.max(0.05, Math.min(10.0, zoomScale * factor));
    
    const rect = viewport.getBoundingClientRect();
    const scrollX = viewport.scrollLeft;
    const scrollY = viewport.scrollTop;
    
    const viewportX = centerX - rect.left;
    const viewportY = centerY - rect.top;
    
    const worldX = (scrollX + viewportX) / oldScale;
    const worldY = (scrollY + viewportY) / oldScale;
    
    updateTransform();
    
    viewport.scrollLeft = worldX * zoomScale - viewportX;
    viewport.scrollTop = worldY * zoomScale - viewportY;
}}

viewport.addEventListener('wheel', (e) => {{
    if(e.ctrlKey) {{
        e.preventDefault();
        applyZoom(e.deltaY > 0 ? 0.9 : 1.1, e.clientX, e.clientY);
    }}
}}, {{passive:false}});

// ─── PINCH ZOOM (MOBILE) ───
let initialPinchDistance = 0;
function getDistance(t) {{
    const dx = t[0].clientX - t[1].clientX;
    const dy = t[0].clientY - t[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
}}
function getMidpoint(t) {{
    return {{ x: (t[0].clientX + t[1].clientX)/2, y: (t[0].clientY + t[1].clientY)/2 }};
}}

viewport.addEventListener('touchstart', (e) => {{
    if (e.touches.length === 2) {{
        initialPinchDistance = getDistance(e.touches);
    }}
}}, {{passive: false}});

// ─── MANIPULATION ───
let isDragging = false;
let dragStartX, dragStartY;

function attachListeners(el) {{
    const startHandler = (e) => {{
        if(!isEditing) return;
        e.stopPropagation();
        isDragging = true;
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);
        
        const rect = el.getBoundingClientRect();
        dragStartX = clientX - rect.left;
        dragStartY = clientY - rect.top;
        
        selectElement(el);
        closeDrawer();
    }};
    el.addEventListener('mousedown', startHandler);
    el.addEventListener('touchstart', startHandler);
}}

function closeDrawer() {{ drawer.classList.add('closed'); fab.classList.remove('open'); }}
function openDrawer() {{ drawer.classList.remove('closed'); fab.classList.add('open'); }}

function selectElement(el) {{
    if(selectedElement) selectedElement.classList.remove('selected');
    selectedElement = el;
    el.classList.add('selected');
    selBar.classList.add('show');
    document.getElementById('label-size').innerText = Math.round(parseFloat(el.style.fontSize));
    
    let ff = el.style.fontFamily.replace(/['"]/g, '');
    document.getElementById('bar-font-family').value = ff;
    
    document.getElementById('edit-hint').style.display = 'none';
    document.getElementById('edit-controls').style.display = 'flex';
    
    const rect = el.getBoundingClientRect();
    const threshold = window.innerHeight - 200;
    if(rect.bottom > threshold) {{
        viewport.scrollBy({{ top: (rect.bottom - threshold) + 50, behavior: 'smooth' }});
    }}
}}

document.addEventListener('mousemove', (e) => {{
    if(!isDragging || !selectedElement || layoutLocked) return;
    const rect = container.getBoundingClientRect();
    let newX = (e.clientX - rect.left - dragStartX) / zoomScale;
    let newY = (e.clientY - rect.top - dragStartY) / zoomScale;
    
    newY = Math.round(newY / CONFIG.snapGrid) * CONFIG.snapGrid;
    
    const text = selectedElement.innerText.trim();
    const looksLikePrice = /^\\$?\\\d+(\.\\\d{{2}})?$/.test(text);
    if(looksLikePrice && !layoutLocked) {{
        if(Math.abs(newX - CONFIG.priceColumn) < 50) {{
             newX = CONFIG.priceColumn;
             selectedElement.style.textAlign = 'right';
        }}
    }}
    
    selectedElement.style.left = newX + 'px';
    selectedElement.style.top = newY + 'px';
}});

document.addEventListener('touchmove', (e) => {{
    if (e.touches.length === 2 && initialPinchDistance > 0) {{
        e.preventDefault();
        const dist = getDistance(e.touches);
        const factor = dist / initialPinchDistance;
        initialPinchDistance = dist; 
        const mid = getMidpoint(e.touches);
        applyZoom(factor, mid.x, mid.y);
        return;
    }}

    if(!isDragging || !selectedElement || layoutLocked) return;
    const rect = container.getBoundingClientRect();
    const t = e.touches[0];
    let newX = (t.clientX - rect.left - dragStartX) / zoomScale;
    let newY = (t.clientY - rect.top - dragStartY) / zoomScale;
    newY = Math.round(newY / CONFIG.snapGrid) * CONFIG.snapGrid;
    
    selectedElement.style.left = newX + 'px';
    selectedElement.style.top = newY + 'px';
    if(e.cancelable) e.preventDefault();
}}, {{passive:false}});

document.addEventListener('mouseup', () => {{ isDragging = false; }});
document.addEventListener('touchend', () => {{ isDragging = false; initialPinchDistance = 0; }});

document.querySelectorAll('.editable-text').forEach(attachListeners);

fab.onclick = () => {{ 
    if(drawer.classList.contains('closed')) openDrawer();
    else closeDrawer();
}};
document.getElementById('btn-close-drawer').onclick = closeDrawer;

function setEditMode(state) {{
    isEditing = state;
    document.body.classList.toggle('editing', isEditing);
    document.getElementById('btn-toggle-edit').innerText = isEditing ? '✅ Finish Editing' : '✏️ Edit Mode';
    document.querySelectorAll('.editable-text').forEach(el => el.contentEditable = isEditing);
    if(isEditing) {{
        selBar.classList.add('show');
    }} else {{
        if(selectedElement) selectedElement.classList.remove('selected');
        selectedElement = null; 
        selBar.classList.remove('show');
    }}
}}

document.getElementById('btn-toggle-edit').onclick = () => {{
    setEditMode(!isEditing);
    if(isEditing && !selectedElement) {{
        document.getElementById('edit-hint').style.display = 'block';
        document.getElementById('edit-controls').style.display = 'none';
    }}
    closeDrawer();
}};

document.getElementById('btn-zoom-in').onclick = () => applyZoom(1.2, window.innerWidth/2, window.innerHeight/2);
document.getElementById('btn-zoom-out').onclick = () => applyZoom(0.8, window.innerWidth/2, window.innerHeight/2);

document.getElementById('btn-size-up').onclick = () => {{
    if(!selectedElement) return;
    let s = parseFloat(selectedElement.style.fontSize) + 1;
    selectedElement.style.fontSize = s + 'px';
    document.getElementById('label-size').innerText = Math.round(s);
}};
document.getElementById('btn-size-down').onclick = () => {{
    if(!selectedElement) return;
    let s = Math.max(1, parseFloat(selectedElement.style.fontSize) - 1);
    selectedElement.style.fontSize = s + 'px';
    document.getElementById('label-size').innerText = Math.round(s);
}};

function setColor(c) {{ if(selectedElement) selectedElement.style.color = c; }}

document.getElementById('btn-nudge-up').onclick = () => {{ if(selectedElement) selectedElement.style.top = (parseFloat(selectedElement.style.top)-1)+'px'; }};
document.getElementById('btn-nudge-down').onclick = () => {{ if(selectedElement) selectedElement.style.top = (parseFloat(selectedElement.style.top)+1)+'px'; }};
document.getElementById('btn-nudge-left').onclick = () => {{ if(selectedElement) selectedElement.style.left = (parseFloat(selectedElement.style.left)-1)+'px'; }};
document.getElementById('btn-nudge-right').onclick = () => {{ if(selectedElement) selectedElement.style.left = (parseFloat(selectedElement.style.left)+1)+'px'; }};

document.getElementById('btn-track-up').onclick = () => {{ if(selectedElement) {{ let ls = parseFloat(selectedElement.style.letterSpacing) || 0; selectedElement.style.letterSpacing = (ls + 0.5) + 'px'; }} }};
document.getElementById('btn-track-down').onclick = () => {{ if(selectedElement) {{ let ls = parseFloat(selectedElement.style.letterSpacing) || 0; selectedElement.style.letterSpacing = (ls - 0.5) + 'px'; }} }};

document.getElementById('bar-font-family').onchange = (e) => {{ if(selectedElement) selectedElement.style.fontFamily = e.target.value; }};
document.getElementById('btn-delete').onclick = () => {{ if(selectedElement) {{ selectedElement.remove(); selectedElement = null; selBar.classList.remove('show'); }} }};

document.getElementById('btn-save').onclick = async () => {{
    if(isSaving) return;
    isSaving = true;
    const btn = document.getElementById('btn-save');
    const originalText = btn.innerText;
    btn.innerText = '⏳ Saving...';

    const data = {{
        zoom: zoomScale,
        scroll: {{ x: viewport.scrollLeft, y: viewport.scrollTop }},
        elements: []
    }};
    
    document.querySelectorAll('.editable-text').forEach(el => {{
        data.elements.push({{ 
            id: el.id, 
            t: el.innerText, 
            l: el.style.left, 
            tp: el.style.top, 
            fs: el.style.fontSize, 
            ff: el.style.fontFamily, 
            ls: el.style.letterSpacing, 
            c: el.style.color 
        }});
    }});

    localStorage.setItem('menu_pro_draft_v1', JSON.stringify(data));

    try {{
        const response = await fetch('/api/menu', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }});
        
        if (!response.ok) throw new Error('Server save failed');
        
        const result = await response.json();
        console.log('Saved to server:', result);
        btn.innerText = '✅ Saved';
        setTimeout(() => btn.innerText = originalText, 2000);
    }} catch (err) {{
        console.error(err);
        btn.innerText = '❌ Save Error';
        alert('Failed to save to server. A local draft was saved to this browser.');
        setTimeout(() => btn.innerText = originalText, 3000);
    }} finally {{
        isSaving = false;
    }}
}};

function changeDpi(blob) {{
    return new Promise((resolve) => {{
        const reader = new FileReader();
        reader.onload = (e) => {{
            const arr = new Uint8Array(e.target.result);
            const chunks = [];
            let pos = 8; 
            while (pos < arr.length) {{
                const length = (arr[pos] << 24) | (arr[pos + 1] << 16) | (arr[pos + 2] << 8) | arr[pos + 3];
                const type = String.fromCharCode(arr[pos + 4], arr[pos + 5], arr[pos + 6], arr[pos + 7]);
                const chunk = arr.slice(pos, pos + length + 12);
                if (type !== 'IEND') chunks.push(chunk);
                else chunks.push(chunk);
                pos += length + 12;
            }}

            const dpiBuffer = new ArrayBuffer(21);
            const view = new DataView(dpiBuffer);
            view.setUint32(0, 9); 
            view.setUint8(4, 112); view.setUint8(5, 72); view.setUint8(6, 89); view.setUint8(7, 115); 
            view.setUint32(8, 11811); 
            view.setUint32(12, 11811); 
            view.setUint8(16, 1); 

            const crcTable = new Uint32Array(256);
            for (let n = 0; n < 256; n++) {{
                let c = n;
                for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
                crcTable[n] = c;
            }}
            function crc32(buf) {{
                let c = 0xFFFFFFFF;
                for (let i = 0; i < buf.length; i++) {{
                    c = crcTable[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
                }}
                return (c ^ 0xFFFFFFFF) >>> 0;
            }}
            view.setUint32(17, crc32(new Uint8Array(dpiBuffer, 4, 13)));

            const newChunks = [arr.slice(0, 8), chunks[0], new Uint8Array(dpiBuffer)];
            for (let i = 1; i < chunks.length; i++) newChunks.push(chunks[i]);
            resolve(new Blob(newChunks, {{ type: 'image/png' }}));
        }};
        reader.readAsArrayBuffer(blob);
    }});
}}

document.getElementById('btn-lock').onclick = () => {{
    layoutLocked = !layoutLocked;
    const btn = document.getElementById('btn-lock');
    btn.innerText = layoutLocked ? '🔒 Layout Locked' : '🔓 Layout Unlocked';
    btn.classList.toggle('primary', layoutLocked);
    closeDrawer();
}};

async function renderHighRes() {{
    const FINAL_SCALE = 4.1687; 
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(originalWidth * FINAL_SCALE);
    canvas.height = Math.round(originalHeight * FINAL_SCALE);
    const ctx = canvas.getContext('2d');
    
    const bgImg = new Image();
    console.log('Loading High-Res Master Asset...');
    bgImg.src = CONFIG.bgMaster; // Use the 7MB master for export
    await new Promise(r => bgImg.onload = r);
    ctx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
    
    await document.fonts.ready; 
    
    const elements = document.querySelectorAll('.editable-text');
    for(const el of elements) {{
        ctx.save();
        const left = parseFloat(el.style.left) * FINAL_SCALE;
        const top = parseFloat(el.style.top) * FINAL_SCALE;
        const size = parseFloat(el.style.fontSize) * FINAL_SCALE;
        const family = el.style.fontFamily.replace(/['"]/g, '');
        const color = el.style.color || '#000000';
        const text = el.innerText;
        const letterSpacing = (parseFloat(el.style.letterSpacing) || 0) * FINAL_SCALE;
        const align = el.style.textAlign || 'left';
        
        ctx.font = `${{size}}px "${{family}}"`;
        ctx.fillStyle = color;
        ctx.textBaseline = 'top';
        ctx.textAlign = align;
        
        let drawX = left;
        if(letterSpacing === 0) {{
            ctx.fillText(text, drawX, top);
        }} else {{
            let currentX = drawX;
            for(let char of text) {{
                ctx.fillText(char, currentX, top);
                currentX += ctx.measureText(char).width + letterSpacing;
            }}
        }}
        ctx.restore();
    }}
    
    return new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
}}

document.getElementById('btn-png').onclick = async () => {{
    closeDrawer();
    selBar.classList.remove('show');
    const wasEditing = isEditing;
    if(wasEditing) document.body.classList.remove('editing');
    if(selectedElement) selectedElement.classList.remove('selected');
    
    const blob = await renderHighRes();
    const dpiBlob = await changeDpi(blob);
    
    const link = document.createElement('a');
    link.download = 'menu-300dpi-pro.png';
    link.href = URL.createObjectURL(dpiBlob);
    link.click();
    
    if(wasEditing) document.body.classList.add('editing');
}};

document.getElementById('btn-add-text').onclick = () => {{
    const id = 'txt_' + Date.now();
    const el = document.createElement('div');
    el.id = id; el.className = 'editable-text'; el.innerText = 'New Text'; el.contentEditable = 'true';
    el.style.left = '450px'; el.style.top = '900px'; el.style.fontSize = '26px'; el.style.fontFamily = 'century-gothic-bold'; el.style.color = '#000000';
    container.appendChild(el); attachListeners(el); 
    setEditMode(true); 
    selectElement(el); 
    closeDrawer();
}};

document.getElementById('btn-reset').onclick = () => {{ if(confirm('Reset all changes?')) location.reload(); }};

async function loadSession(isAuto = false) {{
    try {{
        const response = await fetch('/api/menu');
        if(!response.ok) throw new Error('Fetch failed');
        const saved = await response.json();
        
        // --- Persistence Warning ---
        if (saved.status && !saved.status.is_persistent) {{
            console.warn('⚠️ EPHEMERAL STORAGE DETECTED. Data will be LOST after redeploy.');
            if (!isAuto) {{
                alert('Warning: No Railway Volume detected at ' + saved.status.storage_base + '. Your changes will be wiped on the next deployment.');
            }}
        }}

        if (!saved.elements || saved.elements.length === 0) {{
            const localData = localStorage.getItem('menu_pro_draft_v1');
            if (localData && confirm('No data on server. Load local draft?')) {{
                applyData(JSON.parse(localData));
            }}
            return;
        }}

        applyData(saved);
        if(!isAuto) alert('Session Loaded from Server.');
    }} catch (err) {{
        console.error('Load failed:', err);
        const localData = localStorage.getItem('menu_pro_draft_v1');
        if (localData) applyData(JSON.parse(localData));
    }}
}}

function applyData(saved) {{
    saved.elements.forEach(item => {{
        let el = document.getElementById(item.id);
        if(!el) {{
            el = document.createElement('div');
            el.id = item.id;
            el.className = 'editable-text';
            el.contentEditable = isEditing.toString();
            container.appendChild(el);
            attachListeners(el);
        }}
        el.innerText = item.t; 
        el.style.left = item.l; el.style.top = item.tp; 
        el.style.fontSize = item.fs; el.style.fontFamily = item.ff; 
        if(item.ls) el.style.letterSpacing = item.ls; 
        if(item.c) el.style.color = item.c;
    }});
    
    if(saved.zoom) {{
        sessionLoaded = true; 
        zoomScale = saved.zoom;
        updateTransform();
        setTimeout(() => {{
            const oldBehavior = viewport.style.scrollBehavior;
            viewport.style.scrollBehavior = 'auto';
            viewport.scrollLeft = saved.scroll.x;
            viewport.scrollTop = saved.scroll.y;
            viewport.style.scrollBehavior = oldBehavior;
        }}, 100);
    }}
}}

document.getElementById('btn-load').onclick = () => loadSession(false);

window.addEventListener('DOMContentLoaded', () => {{
    setTimeout(() => loadSession(true), 500); 
}});
</script>
</body>
</html>
""")

with open("index.html", "w", encoding="utf-8") as f:
    f.write("".join(html))
print("Generated index.html successfully.")
