import codecs, re

file_path = r'c:\WebsiteProject\EDITABLE MENU TEMPLATE WITHOUT KIDS MENU\build_app.py'

# Reset build_app.py first if possible by undoing previous patch?
# Actually, I'll just look for what I added and fix it or replace.
with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# ─────────────────────────────────────────────
# Fix the Modern CSS (Double braces for f-string compatibility)
# ─────────────────────────────────────────────
modern_css_proper = """
/* ─── Modern Selection Highlight ─── */
.editable-text.selected {{
    border: 2px solid #f1c40f !important;
    background: rgba(241, 196, 15, 0.15) !important;
    box-shadow: 0 0 15px rgba(241, 196, 15, 0.5);
    z-index: 1000 !important;
    border-radius: 4px;
    animation: selectionPulse 1.5s infinite;
}}
@keyframes selectionPulse {{
    0% {{ box-shadow: 0 0 5px rgba(241, 196, 15, 0.4); }}
    50% {{ box-shadow: 0 0 20px rgba(241, 196, 15, 0.8); }}
    100% {{ box-shadow: 0 0 5px rgba(241, 196, 15, 0.4); }}
}}

/* ─── Selection Handles (Simulated) ─── */
.editable-text.selected::after {{
    content: '';
    position: absolute;
    bottom: -5px; right: -5px;
    width: 10px; height: 10px;
    background: #f1c40f;
    border: 2px solid #fff;
    border-radius: 50%;
}}

/* ─── Contextual Selection Bar (Bottom) ─── */
#selection-bar {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(150%);
    background: rgba(15, 15, 30, 0.9);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 30px;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 3000;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    max-width: 95vw;
}}
#selection-bar.show {{ transform: translateX(-50%) translateY(0); }}

#selection-bar .ctrl-group {{
    display: flex;
    align-items: center;
    gap: 8px;
    border-right: 1px solid rgba(255,255,255,0.1);
    padding-right: 12px;
}}
#selection-bar .ctrl-group:last-child {{ border-right: none; padding-right: 0; }}

#selection-bar select {{
    background: #111;
    color: #fff;
    border: 1px solid #444;
    border-radius: 15px;
    padding: 4px 8px;
    font-size: 11px;
    max-width: 100px;
}}

#selection-bar .val-display {{
    min-width: 24px;
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    color: #f1c40f;
}}

#selection-bar .btn-round {{
    width: 28px; height: 28px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    border: none;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 14px;
}}
#selection-bar .btn-round:active {{ background: #f1c40f; color: #000; }}

#selection-bar .btn-delete {{ background: rgba(231, 76, 60, 0.2); color: #e74c3c; }}
#selection-bar .btn-delete:active {{ background: #e74c3c; color: #fff; }}

/* ─── Global Toolbar overrides ─── */
@media (max-width: 900px) {{
    #style-panel {{ display: none !important; }}
    #toolbar {{ height: 44px; padding: 0 12px; }}
    #toolbar-brand span {{ font-size: 13px; }}
    #editor-wrapper {{ margin-top: 44px !important; margin-bottom: 0px !important; }}
}}
"""

# If the broken CSS is already there, replace it.
# The broken one had single { }
broken_css_pattern = r'/\* ─── Modern Selection Highlight ─── \*/.*?#editor-wrapper \{ margin-top: 44px !important; margin-bottom: 0px !important; \}\n\}\n'
content = re.sub(broken_css_pattern, modern_css_proper, content, flags=re.DOTALL)

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)

# Update the patch script itself so it's correct for potential re-runs
# (Already updated in this execution if I just use it correctly next time)
print("build_app.py SyntaxError fixed (CSS braces escaped).")
