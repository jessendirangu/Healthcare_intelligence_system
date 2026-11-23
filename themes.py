"""Colour themes the user can switch between in the sidebar."""

THEMES = {
    "Light (clinic green)": {
        "bg": "#F5F7F6", "surface": "#FFFFFF", "surface2": "#E9EFED",
        "text": "#1F2D2B", "muted": "#5B6B68", "border": "#DCE5E2", "accent": "#2F7D6D",
    },
    "Dark": {
        "bg": "#0F1720", "surface": "#17212B", "surface2": "#1F2B37",
        "text": "#E6EDF3", "muted": "#9AA7B4", "border": "#2C3A47", "accent": "#3FB59E",
    },
    "Ocean blue": {
        "bg": "#F2F7FC", "surface": "#FFFFFF", "surface2": "#E3EEF8",
        "text": "#12263A", "muted": "#4F6377", "border": "#CFE0F0", "accent": "#1F6FB2",
    },
    "Sunset": {
        "bg": "#FDF6F0", "surface": "#FFFFFF", "surface2": "#F7E8DC",
        "text": "#3A2418", "muted": "#7A5C4C", "border": "#EED8C7", "accent": "#C8553D",
    },
    "Lavender": {
        "bg": "#F7F5FC", "surface": "#FFFFFF", "surface2": "#ECE7F7",
        "text": "#2B2340", "muted": "#64597E", "border": "#DDD5EE", "accent": "#6B4FBB",
    },
    "Midnight blue": {
        "bg": "#0B1426", "surface": "#13203A", "surface2": "#1B2C4D",
        "text": "#E4ECFA", "muted": "#93A4C3", "border": "#263A60", "accent": "#5B9CF5",
    },
}


def theme_css(t):
    return f"""
<style>
.stApp, header[data-testid="stHeader"] {{ background: {t['bg']}; }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"] {{ color: {t['text']}; }}
[data-testid="stCaptionContainer"], .stApp small {{ color: {t['muted']} !important; }}

section[data-testid="stSidebar"] {{
    background: {t['surface2']};
    border-right: 1px solid {t['border']};
}}

/* Text boxes, number boxes and dropdowns */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb="input"], div[data-baseweb="base-input"],
div[data-baseweb="select"] > div {{
    background: {t['surface']} !important;
    color: {t['text']} !important;
    border-color: {t['border']} !important;
}}
div[data-baseweb="popover"] ul, ul[role="listbox"] {{ background: {t['surface']} !important; }}
ul[role="listbox"] li {{ color: {t['text']} !important; }}

/* Buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
    background: {t['accent']}; color: #FFFFFF; border: none; border-radius: 8px; font-weight: 600;
}}
/* Keep button text white (the general text colour rule would otherwise darken it) */
.stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p {{
    color: #FFFFFF !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {{ filter: brightness(1.1); color: #FFFFFF; }}

/* Cards */
.banner {{
    padding: 28px 32px; border-radius: 12px; margin-bottom: 20px;
    background: {t['surface']}; border: 1px solid {t['border']};
    border-left: 6px solid {t['accent']};
}}
.banner h1 {{ color: {t['text']} !important; font-size: 32px; margin: 0 0 6px 0; }}
.banner p  {{ color: {t['muted']} !important; font-size: 15px; margin: 0; }}

div[data-testid="stMetric"], div[data-testid="stForm"], div[data-testid="stExpander"] {{
    background: {t['surface']}; border: 1px solid {t['border']}; border-radius: 10px;
}}
div[data-testid="stMetric"] {{ padding: 16px; }}
div[data-testid="stMetricValue"] {{ color: {t['accent']} !important; }}

/* Charts and tables sit on a light card so they stay readable in dark themes */
div[data-testid="stVegaLiteChart"], div[data-testid="stArrowVegaLiteChart"],
div[data-testid="stDataFrame"] {{
    background: #FFFFFF; border-radius: 10px; padding: 8px;
}}

/* Tabs */
button[data-baseweb="tab"] p {{ color: {t['muted']}; }}
button[data-baseweb="tab"][aria-selected="true"] p {{ color: {t['accent']}; }}

hr {{ border-color: {t['border']}; }}
</style>
"""