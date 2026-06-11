import html
from base64 import b64encode
from pathlib import Path

import streamlit as st


def inject_global_styles():
    hero_image = Path(__file__).with_name("mundial_2026.jpg")
    hero_background = ""
    if hero_image.exists():
        encoded_image = b64encode(hero_image.read_bytes()).decode("ascii")
        hero_background = f', url("data:image/jpeg;base64,{encoded_image}")'

    css = """
        <style>
        :root {
            --pitch: #0f5f4b;
            --pitch-dark: #08392f;
            --line: rgba(255, 255, 255, 0.18);
            --gold: #f8c14a;
            --coral: #ef6f4f;
            --ink: #11231f;
            --muted: #66736f;
            --surface: #ffffff;
            --surface-soft: #f5f8f6;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(248, 193, 74, 0.18), transparent 34rem),
                linear-gradient(180deg, #f8faf8 0%, #eef4f0 48%, #f8faf8 100%);
            color: var(--ink);
        }

        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--pitch-dark) 0%, var(--pitch) 100%);
            color: #ffffff;
        }

        [data-testid="stSidebar"] * {
            color: #ffffff;
        }

        [data-testid="stSidebar"] img {
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.22);
            box-shadow: 0 18px 34px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stSidebar"] [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 8px;
            padding: 0.8rem 0.9rem;
        }

        [data-testid="stSidebar"] [data-testid="stMetricValue"] {
            font-size: clamp(1.25rem, 1.9vw, 1.65rem);
            line-height: 1.1;
            white-space: normal;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.3rem 0.45rem;
            transition: background 160ms ease, border-color 160ms ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(248, 193, 74, 0.45);
        }

        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, var(--gold), #ffdc75) !important;
            color: var(--pitch-dark) !important;
            border: 1px solid rgba(255, 255, 255, 0.34) !important;
            box-shadow: 0 12px 26px rgba(0, 0, 0, 0.18);
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, #ffe08a, var(--gold)) !important;
            border-color: rgba(255, 255, 255, 0.55) !important;
        }

        [data-testid="stSidebar"] .stButton > button p {
            color: var(--pitch-dark) !important;
            font-weight: 900;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        .hero-panel {
            position: relative;
            overflow: hidden;
            min-height: 210px;
            border-radius: 8px;
            padding: 2rem;
            margin: 0 0 1.25rem;
            background:
                linear-gradient(110deg, rgba(8, 57, 47, 0.94) 0%, rgba(15, 95, 75, 0.9) 54%, rgba(239, 111, 79, 0.78) 100%)__HERO_BACKGROUND__;
            background-size: cover;
            background-position: center;
            box-shadow: 0 20px 55px rgba(7, 41, 34, 0.18);
            color: #ffffff;
        }

        .hero-panel::after {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px);
            background-size: 52px 52px;
            opacity: 0.24;
        }

        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 760px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.9rem;
            padding: 0.28rem 0.62rem;
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            color: #fff6d8;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .hero-panel h1 {
            margin: 0;
            color: #ffffff;
            font-size: clamp(2rem, 4vw, 3.5rem);
            line-height: 1.02;
        }

        .hero-panel p {
            margin: 0.85rem 0 0;
            color: rgba(255, 255, 255, 0.86);
            font-size: 1rem;
            max-width: 620px;
        }

        .section-title {
            margin: 1.3rem 0 0.75rem;
        }

        .section-title h2 {
            margin: 0;
            font-size: 1.55rem;
        }

        .section-title p {
            margin: 0.25rem 0 0;
            color: var(--muted);
        }

        div[data-testid="stExpander"] {
            border: 1px solid #dfe8e3 !important;
            border-radius: 8px !important;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 12px 28px rgba(16, 48, 40, 0.06);
        }

        div[data-testid="stExpander"] details summary {
            background: linear-gradient(135deg, #ffffff, #edf6f1) !important;
            color: var(--pitch-dark) !important;
            min-height: 2.6rem;
            font-weight: 900;
        }

        div[data-testid="stExpander"] details summary p,
        div[data-testid="stExpander"] details summary span,
        div[data-testid="stExpander"] details summary svg {
            color: var(--pitch-dark) !important;
            fill: var(--pitch-dark) !important;
        }

        .match-card {
            border: 1px solid #dfe8e3;
            border-radius: 8px;
            padding: 1rem 1rem 0.85rem;
            margin-bottom: 0.85rem;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbf9 100%);
            box-shadow: 0 12px 28px rgba(16, 48, 40, 0.08);
        }

        .match-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.8rem;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .match-pill {
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            color: var(--pitch-dark);
            background: rgba(248, 193, 74, 0.22);
        }

        .match-teams {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 0.8rem;
            text-align: center;
        }

        .team-name {
            min-width: 0;
            font-weight: 800;
            font-size: 1.05rem;
            overflow-wrap: anywhere;
        }

        .versus {
            width: 38px;
            height: 38px;
            display: inline-grid;
            place-items: center;
            border-radius: 999px;
            background: var(--pitch);
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 900;
            box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.16);
        }

        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #dfe8e3 !important;
            border-radius: 8px !important;
            box-shadow: 0 12px 28px rgba(16, 48, 40, 0.06);
        }

        .stTextInput label, .stNumberInput label, .stSelectbox label {
            color: var(--ink) !important;
            font-weight: 700;
        }

        .stTextInput input, .stNumberInput input {
            background: #ffffff !important;
            color: var(--ink) !important;
            border: 1px solid #cfddd6 !important;
            border-radius: 8px !important;
            caret-color: var(--pitch);
        }

        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: var(--pitch) !important;
            box-shadow: 0 0 0 2px rgba(15, 95, 75, 0.14) !important;
        }

        .stTabs [role="tab"] {
            color: var(--muted);
            font-weight: 800;
        }

        .stTabs [aria-selected="true"] {
            color: var(--pitch-dark);
        }

        .stButton > button, [data-testid="stFormSubmitButton"] button,
        [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {
            border-radius: 8px;
            border: 0;
            font-weight: 800;
            min-height: 2.6rem;
            box-shadow: 0 10px 22px rgba(15, 95, 75, 0.16);
        }

        .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"],
        [data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primary"],
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, var(--pitch), #138f6e) !important;
            background-color: var(--pitch) !important;
            color: #ffffff !important;
        }

        div[data-testid="stFormSubmitButton"] button p {
            color: #ffffff !important;
        }

        [data-testid="stBaseButton-secondary"] {
            background: rgba(255, 255, 255, 0.92) !important;
            color: var(--pitch-dark) !important;
            border: 1px solid #dfe8e3 !important;
        }

        .rank-card {
            border-radius: 8px;
            padding: 1rem;
            background: var(--surface);
            border: 1px solid #dfe8e3;
            box-shadow: 0 12px 28px rgba(16, 48, 40, 0.08);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #dfe8e3;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 12px 28px rgba(16, 48, 40, 0.06);
            background: #ffffff;
        }

        @media (max-width: 768px) {
            [data-testid="stAppViewContainer"] > .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-panel {
                padding: 1.4rem;
                min-height: 230px;
            }
        }
        </style>
        """.replace("__HERO_BACKGROUND__", hero_background)

    st.markdown(
        css,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle, eyebrow="Polla Mundial 2026"):
    st.markdown(
        f"""
        <section class="hero-panel">
            <div class="hero-content">
                <div class="eyebrow">{html.escape(eyebrow)}</div>
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_title(title, subtitle=None):
    subtitle_html = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{html.escape(title)}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def match_card(equipo_a, equipo_b, meta="Fase de grupos", status="Pendiente"):
    st.markdown(
        f"""
        <div class="match-card">
            <div class="match-meta">
                <span>{html.escape(meta)}</span>
                <span class="match-pill">{html.escape(status)}</span>
            </div>
            <div class="match-teams">
                <div class="team-name">{html.escape(equipo_a)}</div>
                <div class="versus">VS</div>
                <div class="team-name">{html.escape(equipo_b)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
