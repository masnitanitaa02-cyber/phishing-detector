"""
styles.py
Custom CSS untuk tema "Fresh & Vibrant" — tema terang dengan aksen warna hidup
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ====== ROOT VARIABLES ====== */
:root {
    --bg-primary: #f0f4ff;
    --bg-secondary: #ffffff;
    --bg-card: #ffffff;
    --bg-gradient-start: #e8edff;
    --bg-gradient-end: #f5f0ff;
    --border-subtle: #dce3f0;
    --text-primary: #1a2332;
    --text-secondary: #4a5a7a;
    --text-muted: #7a8aa5;
    --accent-blue: #4f7cff;
    --accent-blue-light: #e8edff;
    --accent-green: #00c9a7;
    --accent-green-light: #e0f7f2;
    --accent-orange: #ff9f4a;
    --accent-orange-light: #fff0e0;
    --accent-pink: #ff6b8a;
    --accent-pink-light: #ffe8ee;
    --accent-purple: #8b5cf6;
    --accent-purple-light: #ede7fe;
    --shadow-card: 0 8px 30px rgba(79, 124, 255, 0.10);
    --shadow-hover: 0 12px 40px rgba(79, 124, 255, 0.18);
}

/* ====== GLOBAL ====== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
}

/* ====== SIDEBAR ====== */
[data-testid="stSidebar"] {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-subtle);
    box-shadow: 4px 0 20px rgba(79, 124, 255, 0.06);
    padding: 1.5rem 0;
}

[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: var(--text-secondary);
    padding: 8px 12px;
    border-radius: 10px;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--accent-blue-light);
    color: var(--accent-blue);
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 4px;
}

/* ====== HERO SECTION ====== */
.hero-wrap {
    padding: 32px 36px;
    border-radius: 20px;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-card);
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

.hero-wrap::before {
    content: "🛡️";
    position: absolute;
    top: -30px;
    right: -20px;
    font-size: 140px;
    opacity: 0.06;
    transform: rotate(15deg);
}

.hero-wrap::after {
    content: "";
    position: absolute;
    top: -80px;
    right: -80px;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(79, 124, 255, 0.06) 0%, transparent 70%);
}

.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-blue);
    font-weight: 600;
    margin-bottom: 10px;
    background: var(--accent-blue-light);
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
}

.hero-title {
    font-size: 34px;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.2;
    margin: 0 0 12px 0;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 15px;
    color: var(--text-secondary);
    max-width: 720px;
    line-height: 1.7;
}

.hero-sub b {
    color: var(--accent-blue);
}

/* ====== CARDS ====== */
.cyber-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: var(--shadow-card);
    transition: all 0.3s ease;
}

.cyber-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

/* ====== RESULT CARDS ====== */
.result-safe {
    background: linear-gradient(135deg, var(--accent-green-light), #ffffff);
    border: 2px solid var(--accent-green);
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(0, 201, 167, 0.15);
    transition: all 0.3s ease;
}

.result-safe:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 201, 167, 0.25);
}

.result-safe .result-icon { font-size: 52px; }

.result-safe .result-label {
    font-size: 26px;
    font-weight: 800;
    color: var(--accent-green);
    margin: 12px 0 4px 0;
    letter-spacing: -0.02em;
}

.result-danger {
    background: linear-gradient(135deg, var(--accent-pink-light), #ffffff);
    border: 2px solid var(--accent-pink);
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(255, 107, 138, 0.15);
    animation: pulse-danger 2s ease-in-out infinite;
    transition: all 0.3s ease;
}

.result-danger:hover {
    transform: translateY(-4px);
}

.result-danger .result-icon { font-size: 52px; }

.result-danger .result-label {
    font-size: 26px;
    font-weight: 800;
    color: var(--accent-pink);
    margin: 12px 0 4px 0;
    letter-spacing: -0.02em;
}

@keyframes pulse-danger {
    0%, 100% { box-shadow: 0 8px 30px rgba(255, 107, 138, 0.15); }
    50% { box-shadow: 0 8px 50px rgba(255, 107, 138, 0.30); }
}

.result-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 8px;
    word-break: break-all;
    background: rgba(0,0,0,0.03);
    padding: 8px 12px;
    border-radius: 8px;
}

/* ====== CONFIDENCE BAR ====== */
.conf-track {
    width: 100%;
    height: 12px;
    background: #eef2f8;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 20px;
    border: 1px solid var(--border-subtle);
}

.conf-fill-safe {
    height: 100%;
    background: linear-gradient(90deg, #00c9a7, #00e5c7);
    border-radius: 10px;
    transition: width 0.8s ease;
}

.conf-fill-danger {
    height: 100%;
    background: linear-gradient(90deg, #ff6b8a, #ff4d6d);
    border-radius: 10px;
    transition: width 0.8s ease;
}

.conf-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
    font-weight: 500;
}

.conf-label span:last-child {
    color: var(--text-primary);
    font-weight: 700;
}

/* ====== SECTION LABEL ====== */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-blue);
    font-weight: 600;
    margin-bottom: 12px;
    display: block;
}

.section-label::before {
    content: "✦ ";
    color: var(--accent-orange);
}

/* ====== METRICS ====== */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: var(--shadow-card);
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 28px !important;
}

/* ====== BUTTONS ====== */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), #6d8fff);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.7rem 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(79, 124, 255, 0.25);
    font-family: 'Inter', sans-serif;
}

.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(79, 124, 255, 0.40);
    transform: translateY(-2px) scale(1.02);
}

.stButton > button:active {
    transform: scale(0.98);
}

/* ====== DOWNLOAD BUTTON ====== */
.stDownloadButton > button {
    background: var(--bg-secondary);
    color: var(--accent-blue);
    border: 2px solid var(--accent-blue);
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stDownloadButton > button:hover {
    background: var(--accent-blue);
    color: white;
    box-shadow: 0 4px 20px rgba(79, 124, 255, 0.30);
    transform: translateY(-2px);
}

/* ====== TEXT INPUT ====== */
.stTextInput input {
    background: var(--bg-secondary) !important;
    border: 2px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 4px rgba(79, 124, 255, 0.10) !important;
}

/* ====== FILE UPLOAD ====== */
[data-testid="stFileUploaderDropzone"] {
    background: var(--bg-secondary) !important;
    border: 2px dashed var(--border-subtle) !important;
    border-radius: 14px !important;
    transition: all 0.3s ease;
    padding: 30px !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--accent-blue) !important;
    background: var(--accent-blue-light) !important;
}

/* ====== DATAFRAME ====== */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

[data-testid="stDataFrame"] table {
    font-family: 'Inter', sans-serif;
}

/* ====== SELECTBOX ====== */
.stSelectbox [data-baseweb="select"] {
    border-radius: 12px !important;
}

.stSelectbox [data-baseweb="select"] > div {
    border: 2px solid var(--border-subtle) !important;
    border-radius: 12px !important;
}

/* ====== RADIO BUTTONS (Sidebar) ====== */
[data-testid="stRadio"] [role="radiogroup"] {
    gap: 6px;
}

[data-testid="stRadio"] label {
    font-weight: 500;
    padding: 10px 14px;
    border-radius: 10px;
    transition: all 0.2s ease;
}

[data-testid="stRadio"] label:hover {
    background: var(--accent-blue-light);
}

[data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
    font-weight: 500;
}

/* ====== FOOTER ====== */
.cyber-footer {
    text-align: center;
    color: var(--text-muted);
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    padding: 28px 0 12px 0;
    border-top: 1px solid var(--border-subtle);
    margin-top: 40px;
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: 24px;
    box-shadow: var(--shadow-card);
}

.cyber-footer br {
    display: none;
}

.cyber-footer span {
    color: var(--accent-blue);
    font-weight: 600;
}

/* ====== RESPONSIVE ====== */
@media (max-width: 768px) {
    .hero-title {
        font-size: 24px;
    }
    .hero-wrap {
        padding: 20px;
    }
    .result-safe .result-label,
    .result-danger .result-label {
        font-size: 20px;
    }
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
    }
}

/* ====== MISC ====== */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-subtle);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-blue);
}

/* Success/Error/Warning messages */
.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid var(--accent-blue) !important;
}

.stAlert [data-testid="stMarkdownContainer"] {
    font-weight: 500;
}

/* Spinner */
[data-testid="stSpinner"] {
    color: var(--accent-blue) !important;
}

/* Tabs (if any) */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--accent-blue-light);
    color: var(--accent-blue);
}

.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: white !important;
}

/* Chart styling */
[data-testid="stChart"] {
    background: var(--bg-secondary);
    border-radius: 14px;
    padding: 16px;
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-card);
}
</style>
"""