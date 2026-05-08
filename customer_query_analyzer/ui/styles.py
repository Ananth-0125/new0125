CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

:root {
    --primary:      #0058A3;
    --primary-dark: #004080;
    --primary-dim:  rgba(0,88,163,0.10);
    --accent:       #FFDA1A;
    --accent-dark:  #E5C500;
    --accent-dim:   rgba(255,218,26,0.15);
    --bg:           #F5F5F5;
    --surface:      #FFFFFF;
    --surface2:     #EEF3FA;
    --surface3:     #E4EDF7;
    --border:       #C0CDD8;
    --border-dim:   #D8E3EC;
    --text:         #333333;
    --text-dim:     #666677;
    --text-mute:    #99A0AA;
    --danger:       #CC2200;
    --success:      #1A7A2A;
    --warn:         #A06000;
}

html, body, [class*="css"] { font-family: 'Oswald', 'Roboto', sans-serif !important; color: var(--text) !important; }
.stApp { background: var(--bg) !important; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 100% !important; }
@media (min-width: 768px) { .block-container { padding: 1.4rem 2rem 2rem 2rem !important; } }

[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem !important; }
[data-testid="stSidebarCollapseButton"] { background: var(--primary) !important; border-radius: 0 6px 6px 0 !important; }
[data-testid="stSidebarCollapseButton"]:hover { background: var(--primary-dark) !important; }
[data-testid="stSidebarCollapseButton"] svg { fill: #ffffff !important; }
[data-testid="collapsedControl"] { background: var(--primary) !important; border-radius: 0 6px 6px 0 !important; }
[data-testid="collapsedControl"]:hover { background: var(--primary-dark) !important; }
[data-testid="collapsedControl"] svg { fill: #ffffff !important; }

.page-header {
    background: linear-gradient(135deg, #E8F0FA 0%, #FFFFFF 60%, #FFFBF0 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--primary);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '▶';
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    color: rgba(0,88,163,0.06);
    pointer-events: none;
    line-height: 1;
}
.page-header h1 { font-size: 1.6rem; font-weight: 700; margin: 0 0 5px 0; color: var(--text); letter-spacing: -0.3px; font-family: 'Oswald', sans-serif !important; }
.page-header p { margin: 0; font-size: 0.78rem; color: var(--text-dim); font-family: 'Roboto Mono', monospace !important; font-weight: 400; }
.header-tags { margin-bottom: 10px; }
.htag { display: inline-block; background: var(--accent-dim); border: 1px solid rgba(255,218,26,0.5); color: #7A5800; padding: 2px 10px; border-radius: 2px; font-size: 0.62rem; font-family: 'Roboto Mono', monospace !important; margin-right: 5px; text-transform: uppercase; letter-spacing: 1px; }
@media (min-width: 768px) { .page-header { padding: 24px 30px; } .page-header h1 { font-size: 1.7rem; } }

.section-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: var(--text-mute); margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--border-dim); font-family: 'Roboto Mono', monospace !important; }
.sb-sec { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-mute); margin: 14px 0 6px 0; font-family: 'Roboto Mono', monospace !important; }

.chat-window { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; height: 400px; overflow-y: auto; margin-bottom: 8px; }
.bubble-user, .bubble-bot, .bubble-security { max-width: 85%; padding: 9px 14px; font-size: 0.86rem; line-height: 1.5; margin-bottom: 8px; clear: both; font-family: 'Roboto Mono', monospace !important; font-weight: 400; }
.bubble-user { background: var(--primary); color: #ffffff; border-radius: 14px 14px 3px 14px; float: right; }
.bubble-bot { background: var(--surface2); border: 1px solid var(--border); color: var(--text); border-radius: 14px 14px 14px 3px; float: left; }
.bubble-security { background: #FFF0EE; border: 1px solid #FFBBAA; color: #8B1500; border-radius: 14px 14px 14px 3px; float: left; }
.msg-meta { font-size: 0.63rem; color: var(--text-mute); margin-bottom: 6px; font-family: 'Roboto Mono', monospace !important; display: flex; gap: 5px; flex-wrap: wrap; align-items: center; clear: both; }
@media (min-width: 768px) { .bubble-user, .bubble-bot, .bubble-security { max-width: 70%; } }

.tag { display: inline-block; padding: 1px 7px; border-radius: 2px; font-size: 0.62rem; font-weight: 500; font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; letter-spacing: 0.5px; }
.t-intent { background: var(--primary-dim); color: var(--primary); border: 1px solid rgba(0,88,163,0.3); }
.t-neg    { background: #FEE8E8; color: #CC2200; border: 1px solid #FFBBAA; }
.t-neu    { background: var(--surface3); color: var(--text-dim); border: 1px solid var(--border); }
.t-pos    { background: #E8FEEE; color: #1A7A2A; border: 1px solid #AAFFBB; }
.t-sec    { background: #CC2200; color: #ffffff; border: 1px solid #AA1800; font-weight: 700; }
.t-low    { background: #FFF8E0; color: #A06000; border: 1px solid #FFD080; }
.t-good   { background: #E8FEEE; color: #1A7A2A; border: 1px solid #AAFFBB; }
.t-bad    { background: #FEE8E8; color: #CC2200; border: 1px solid #FFBBAA; }

.bar-track { background: var(--surface3); border-radius: 2px; height: 5px; margin: 3px 0 9px 0; overflow: hidden; }
.bar-blue  { background: var(--primary); height: 5px; border-radius: 2px; }
.bar-red   { background: #CC2200; height: 5px; border-radius: 2px; }

.metric-tile { background: var(--surface); border: 1px solid var(--border); border-top: 2px solid var(--primary); border-radius: 6px; padding: 12px 10px; text-align: center; }
.metric-tile .val { font-size: 1.3rem; font-weight: 700; color: var(--text); font-family: 'Oswald', sans-serif !important; line-height: 1.1; }
.metric-tile .lbl { font-size: 0.6rem; color: var(--text-mute); margin-top: 4px; text-transform: uppercase; letter-spacing: 1.5px; font-family: 'Roboto Mono', monospace !important; }

.empty-state { text-align: center; color: var(--text-mute); padding: 80px 20px; }
.empty-state .text { font-size: 0.87rem; color: var(--text-dim); }
.empty-state .hint { font-size: 0.75rem; color: var(--text-mute); margin-top: 5px; }

.stButton > button, .stDownloadButton > button { background: var(--surface2) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; font-weight: 500 !important; font-family: 'Roboto Mono', monospace !important; font-size: 0.8rem !important; padding: 6px 16px !important; transition: all 0.15s ease !important; box-shadow: none !important; text-transform: uppercase; letter-spacing: 0.5px; }
.stButton > button:hover, .stDownloadButton > button:hover { background: var(--primary) !important; color: #ffffff !important; border-color: var(--primary) !important; }
.stFormSubmitButton > button { background: var(--accent) !important; color: #333333 !important; border: none !important; border-radius: 4px !important; font-size: 1.2rem !important; font-weight: 700 !important; padding: 0 !important; width: 100% !important; min-height: 38px !important; line-height: 38px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
.stFormSubmitButton > button:hover { background: var(--accent-dark) !important; }
section[data-testid="stSidebar"] .stButton > button { background: var(--primary) !important; color: #ffffff !important; border: none !important; width: 100% !important; }
section[data-testid="stSidebar"] .stButton > button:hover { background: var(--primary-dark) !important; }
section[data-testid="stSidebar"] .stDownloadButton > button { background: var(--surface2) !important; color: var(--text) !important; border: 1px solid var(--border) !important; width: 100% !important; }
section[data-testid="stSidebar"] .stDownloadButton > button:hover { background: var(--primary) !important; color: #ffffff !important; }

div[data-baseweb="input"] input, .stTextInput input { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; color: var(--text) !important; font-family: 'Roboto Mono', monospace !important; font-size: 0.88rem !important; }
div[data-baseweb="input"] input::placeholder { color: var(--text-mute) !important; }
div[data-baseweb="input"] input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 2px rgba(0,88,163,0.15) !important; }

[data-testid="stDataFrameResizable"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.main .block-container { max-width: 100% !important; }
section.main { max-width: 100% !important; }

.stSpinner > div { border-top-color: var(--primary) !important; }
.stSuccess { background: #E8FEEE !important; color: #1A7A2A !important; border: 1px solid #AAFFBB !important; }
.stWarning { background: #FFF8E0 !important; color: #A06000 !important; border: 1px solid #FFD080 !important; }
.stError   { background: #FEE8E8 !important; color: #CC2200 !important; border: 1px solid #FFBBAA !important; }
</style>
"""
