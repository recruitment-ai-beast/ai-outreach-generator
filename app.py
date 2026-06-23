"""
AI Candidate Outreach Generator
Production-grade Streamlit application.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from utils.validators import validate_inputs, validate_api_key
from utils.outreach_generator import generate_outreach, generate_variations
from utils.scoring import calculate_personalization_score, detect_spam_risk
from utils.export_utils import export_as_txt, export_bulk_csv, export_bulk_txt
from utils.bulk_processor import validate_csv, process_bulk

load_dotenv()
logging.basicConfig(level=logging.ERROR)

# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="AI Outreach Generator",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Session State
# --------------------------------------------------

def init_session_state():
    defaults = {
        "generated_content": None,
        "variations": {},
        "history": [],
        "candidate_name": "",
        "current_role": "",
        "current_company": "",
        "skills": "",
        "target_job": "",
        "tone": "Professional",
        "platform": "LinkedIn",
        "generate_variations": False,
        "theme_mode": "Dark",
        "bulk_results": []
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# Process pending actions BEFORE widgets render
if st.session_state.get("_do_reset", False):
    st.session_state.tone = "Professional"
    st.session_state.platform = "LinkedIn"
    st.session_state.generate_variations = False
    st.session_state["_do_reset"] = False

if "_pending_reuse" in st.session_state:
    st.session_state.generated_content = st.session_state.pop("_pending_reuse")
    for key in ["conn_note_edit", "outreach_edit", "followup_edit"]:
        if key in st.session_state:
            del st.session_state[key]

# --------------------------------------------------
# API Key
# --------------------------------------------------

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #050816; color: #E6F1FF; }

    section[data-testid="stSidebar"] {
        background-color: #0B1220;
        border-right: 1px solid #1E293B;
    }

    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00D4FF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1.5rem 0 0.3rem;
    }

    .main-tagline {
        text-align: center;
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00D4FF, #3B82F6) !important;
        color: #050816 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100% !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #0B1220 !important;
        border: 1px solid #1E293B !important;
        color: #E6F1FF !important;
        border-radius: 8px !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
    }

    label[data-testid="stWidgetLabel"] p {
        color: #E6F1FF !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: #0B1220;
        color: #94A3B8;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [aria-selected="true"] {
        background: #00D4FF !important;
        color: #050816 !important;
        font-weight: 600 !important;
    }

    .metric-card {
        background: #0B1220;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }

    .metric-value { font-size: 1.8rem; font-weight: 700; color: #00D4FF; }
    .metric-label { color: #94A3B8; font-size: 0.8rem; }

    .char-counter { color: #94A3B8; font-size: 0.75rem; text-align: right; }

    .output-section {
        background: #0B1220;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .section-header {
        color: #00D4FF;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .risk-low { color: #22C55E; font-weight: 600; }
    .risk-medium { color: #F59E0B; font-weight: 600; }
    .risk-high { color: #EF4444; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Light mode override
if st.session_state.theme_mode == "Light":
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
        section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }
        label[data-testid="stWidgetLabel"] p { color: #0F172A !important; }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-color: #CBD5E1 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown('<div class="main-title">✉️ AI Candidate Outreach Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="main-tagline">Create personalized outreach messages that candidates actually reply to.</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    theme_mode = st.radio("Theme", ["Dark", "Light"], horizontal=True,
                          index=0 if st.session_state.theme_mode == "Dark" else 1)
    st.session_state.theme_mode = theme_mode
    st.markdown("---")

    st.markdown("### ⚙️ Configuration")

    if st.button("🔄 Reset All Settings", use_container_width=True):
        st.session_state["_do_reset"] = True
        st.rerun()

    st.markdown("---")

    tone = st.selectbox(
        "Tone",
        ["Professional", "Casual", "LinkedIn-native"],
        index=["Professional", "Casual", "LinkedIn-native"].index(st.session_state.tone)
    )
    st.session_state.tone = tone

    platform = st.selectbox(
        "Platform",
        ["LinkedIn", "Email", "WhatsApp"],
        index=["LinkedIn", "Email", "WhatsApp"].index(st.session_state.platform)
    )
    st.session_state.platform = platform

    generate_vars = st.toggle("Generate A/B Variations", value=st.session_state.generate_variations)
    st.session_state.generate_variations = generate_vars

    st.markdown("---")
    st.markdown("### 📊 Session Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.history)}</div>
            <div class="metric-label">Generated</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.bulk_results)}</div>
            <div class="metric-label">Bulk</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#94A3B8; font-size:0.75rem; text-align:center;">
        Built by <strong style="color:#00D4FF;">BEAST</strong><br>
        Vertical AI Engineer<br>
        Recruitment Automation
    </div>""", unsafe_allow_html=True)

# --------------------------------------------------
# Main Tabs
# --------------------------------------------------

main_tab, bulk_tab = st.tabs(["👤 Single Candidate", "📋 Bulk Mode"])

# ==================================================
# SINGLE CANDIDATE TAB
# ==================================================

with main_tab:
    input_col, output_col = st.columns([1, 1.3], gap="large")

    # --------------------------------------------------
    # Input Form
    # --------------------------------------------------

    with input_col:
        st.markdown('<div class="section-header">📋 Candidate Details</div>', unsafe_allow_html=True)

        candidate_name = st.text_input(
            "Candidate Name *",
            value=st.session_state.candidate_name,
            placeholder="e.g. Sarah Johnson"
        )
        st.session_state.candidate_name = candidate_name

        current_role = st.text_input(
            "Current Role *",
            value=st.session_state.current_role,
            placeholder="e.g. Senior Backend Engineer"
        )
        st.session_state.current_role = current_role

        current_company = st.text_input(
            "Current Company *",
            value=st.session_state.current_company,
            placeholder="e.g. Stripe"
        )
        st.session_state.current_company = current_company

        skills = st.text_area(
            "Candidate Skills *",
            value=st.session_state.skills,
            placeholder="Python, AWS, Kubernetes, Distributed Systems",
            height=80
        )
        st.session_state.skills = skills
        st.markdown(f'<div class="char-counter">{len(skills)} chars</div>', unsafe_allow_html=True)

        target_job = st.text_input(
            "Role You're Recruiting For *",
            value=st.session_state.target_job,
            placeholder="e.g. Staff Platform Engineer"
        )
        st.session_state.target_job = target_job

        st.markdown("---")

        # Tone preview
        with st.expander("👁️ Tone Preview"):
            st.markdown(f"""
            **Professional:** Formal, polished — for senior roles
            
            **Casual:** Conversational, warm — like a smart colleague
            
            **LinkedIn-native:** Short, punchy — feels native to LinkedIn
            
            *Currently selected: **{tone}***
            """)

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("✉️ Generate Outreach Package", use_container_width=True)

    # --------------------------------------------------
    # Generation Logic
    # --------------------------------------------------

    if generate_btn:
        key_valid, key_error = validate_api_key(GROQ_API_KEY or "")
        if not key_valid:
            st.error(key_error)
            st.stop()

        inputs_valid, input_error = validate_inputs(
            candidate_name, current_role, current_company,
            skills, target_job, tone, platform
        )
        if not inputs_valid:
            st.error(input_error)
            st.stop()

        # Clear stale content
        st.session_state.generated_content = None
        for key in ["conn_note_edit", "outreach_edit", "followup_edit"]:
            if key in st.session_state:
                del st.session_state[key]

        with st.spinner("Crafting personalized outreach..."):
            content = generate_outreach(
                api_key=GROQ_API_KEY,
                candidate_name=candidate_name,
                current_role=current_role,
                current_company=current_company,
                skills=skills,
                target_job=target_job,
                tone=tone,
                platform=platform
            )

        if content:
            st.session_state.generated_content = content
            st.session_state.history.append({
                "candidate": candidate_name,
                "role": current_role,
                "company": current_company,
                "target": target_job,
                "tone": tone,
                "platform": platform,
                "timestamp": datetime.now().strftime("%H:%M · %d %b"),
                "content": content
            })

            if st.session_state.generate_variations:
                with st.spinner("Generating A/B variations..."):
                    st.session_state.variations = generate_variations(
                        api_key=GROQ_API_KEY,
                        candidate_name=candidate_name,
                        current_role=current_role,
                        current_company=current_company,
                        skills=skills,
                        target_job=target_job,
                        tone=tone,
                        platform=platform
                    )

            st.rerun()
        else:
            st.error(
                "We're having trouble generating outreach messages right now. "
                "Please try again in a moment."
            )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    with output_col:
        if st.session_state.generated_content:
            content = st.session_state.generated_content

            # Scoring
            p_score, p_reason = calculate_personalization_score(
                content,
                st.session_state.candidate_name,
                st.session_state.current_company,
                st.session_state.skills
            )
            risk_level, risk_color, risk_flags = detect_spam_risk(content)

            # Score display
            col_score, col_risk = st.columns(2)
            with col_score:
                st.markdown("**Personalization Score**")
                st.progress(p_score / 100)
                st.markdown(f'<span style="color:#00D4FF; font-weight:600;">{p_score}/100</span> — {p_reason}', unsafe_allow_html=True)

            with col_risk:
                st.markdown("**Spam Risk**")
                risk_class = f"risk-{risk_color}"
                st.markdown(f'<span class="{risk_class}">● {risk_level}</span>', unsafe_allow_html=True)
                if risk_flags:
                    st.caption(f"Flags: {', '.join(risk_flags[:3])}")

            st.markdown("---")

            # Tabs
            tabs_list = ["📄 Messages"]
            if st.session_state.variations:
                tabs_list += ["🅰️ Version A", "🅱️ Version B"]
            tabs_list.append("🕘 History")

            tab_objects = st.tabs(tabs_list)

            # --------------------------------------------------
            # Messages Tab
            # --------------------------------------------------

            with tab_objects[0]:
                # Parse sections from generated content
                sections = {}
                current_section = None
                current_lines = []

                for line in content.split("\n"):
                    if line.startswith("## "):
                        if current_section:
                            sections[current_section] = "\n".join(current_lines).strip()
                        current_section = line.replace("## ", "").strip()
                        current_lines = []
                    else:
                        current_lines.append(line)

                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()

                # Connection Note
                conn_note = sections.get("Connection Note", "")
                st.markdown('<div class="section-header">🔗 Connection Request Note</div>', unsafe_allow_html=True)
                conn_edit = st.text_area(
                    "Edit:", value=conn_note, height=100, key="conn_note_edit",
                    label_visibility="collapsed"
                )
                char_count = len(conn_edit)
                char_color = "#EF4444" if char_count > 300 else "#22C55E"
                st.markdown(
                    f'<div class="char-counter" style="color:{char_color};">{char_count}/300</div>',
                    unsafe_allow_html=True
                )
                if st.button("📋 Copy Connection Note"):
                    components.html(f"<script>navigator.clipboard.writeText({conn_edit!r});</script>", height=0)
                    st.success("Copied!")

                st.markdown("---")

                # Outreach Message
                outreach_msg = sections.get("Outreach Message", "")
                st.markdown('<div class="section-header">✉️ Full Outreach Message</div>', unsafe_allow_html=True)
                outreach_edit = st.text_area(
                    "Edit:", value=outreach_msg, height=200, key="outreach_edit",
                    label_visibility="collapsed"
                )
                st.markdown(f'<div class="char-counter">{len(outreach_edit.split())} words</div>', unsafe_allow_html=True)
                if st.button("📋 Copy Outreach Message"):
                    components.html(f"<script>navigator.clipboard.writeText({outreach_edit!r});</script>", height=0)
                    st.success("Copied!")

                st.markdown("---")

                # Follow-Up
                followup_msg = sections.get("Follow-Up Message", "")
                st.markdown('<div class="section-header">🔄 Follow-Up Message (Day 4)</div>', unsafe_allow_html=True)
                followup_edit = st.text_area(
                    "Edit:", value=followup_msg, height=120, key="followup_edit",
                    label_visibility="collapsed"
                )
                st.markdown(f'<div class="char-counter">{len(followup_edit)} chars</div>', unsafe_allow_html=True)
                if st.button("📋 Copy Follow-Up"):
                    components.html(f"<script>navigator.clipboard.writeText({followup_edit!r});</script>", height=0)
                    st.success("Copied!")

                # Subject Lines (Email only)
                if st.session_state.platform == "Email":
                    subject_lines = sections.get("Subject Lines", "")
                    if subject_lines:
                        st.markdown("---")
                        st.markdown('<div class="section-header">📧 Subject Lines</div>', unsafe_allow_html=True)
                        st.text_area(
                            "Options:", value=subject_lines, height=120,
                            label_visibility="collapsed"
                        )

                st.markdown("---")

                # Export
                st.markdown("**Export:**")
                full_package = f"{conn_edit}\n\n---\n\n{outreach_edit}\n\n---\n\n{followup_edit}"
                txt_data = export_as_txt(full_package, st.session_state.candidate_name)
                st.download_button(
                    "📄 Export TXT",
                    data=txt_data,
                    file_name=f"outreach_{st.session_state.candidate_name.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            # --------------------------------------------------
            # Variation Tabs
            # --------------------------------------------------

            if st.session_state.variations:
                for i, (label, var_content) in enumerate(st.session_state.variations.items()):
                    with tab_objects[i + 1]:
                        st.markdown(f"**{label} — Different psychological angle**")
                        st.text_area(
                            "Content:", value=var_content, height=400,
                            key=f"var_{label}", label_visibility="collapsed"
                        )
                        if st.button(f"📋 Copy {label}", key=f"copy_var_{label}"):
                            components.html(f"<script>navigator.clipboard.writeText({var_content!r});</script>", height=0)
                            st.success(f"{label} copied!")

            # --------------------------------------------------
            # History Tab
            # --------------------------------------------------

            with tab_objects[-1]:
                if not st.session_state.history:
                    st.info("No history yet. Generate your first outreach above.")
                else:
                    st.markdown(f"**{len(st.session_state.history)} outreach package(s) this session**")

                    for i, item in enumerate(reversed(st.session_state.history)):
                        with st.expander(
                            f"✉️ {item['candidate']} · {item['target']} · {item['platform']} · {item['timestamp']}"
                        ):
                            st.text_area(
                                "Content:", value=item["content"], height=250, key=f"hist_{i}",
                                label_visibility="collapsed"
                            )
                            if st.button("♻️ Reuse", key=f"reuse_{i}"):
                                st.session_state["_pending_reuse"] = item["content"]
                                st.rerun()

                    if st.button("🗑️ Clear History", use_container_width=True):
                        st.session_state.history = []
                        st.rerun()

        else:
            st.markdown("""
            <div style="
                text-align:center; padding:4rem 2rem;
                background:#0B1220; border:1px dashed #1E293B;
                border-radius:12px; color:#94A3B8;
            ">
                <div style="font-size:3rem; margin-bottom:1rem;">✉️</div>
                <div style="font-size:1.1rem; font-weight:600; color:#E6F1FF; margin-bottom:0.5rem;">
                    Ready to generate
                </div>
                <div style="font-size:0.9rem;">
                    Fill in candidate details on the left<br>and click Generate.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================================================
# BULK MODE TAB
# ==================================================

with bulk_tab:
    st.markdown("### 📋 Bulk Candidate Outreach")
    st.markdown("Upload a CSV file to generate outreach for multiple candidates at once.")

    # CSV template download
    sample_data = {
        "candidate_name": ["Sarah Johnson", "Alex Chen"],
        "current_role": ["Senior Backend Engineer", "ML Engineer"],
        "current_company": ["Stripe", "Google"],
        "skills": ["Python, AWS, Kubernetes", "Python, PyTorch, LLMs"],
        "target_job": ["Staff Platform Engineer", "Senior AI Engineer"]
    }
    sample_df = pd.DataFrame(sample_data)
    st.download_button(
        "📥 Download CSV Template",
        data=sample_df.to_csv(index=False).encode("utf-8"),
        file_name="outreach_template.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.lower()

            valid, err = validate_csv(df)
            if not valid:
                st.error(f"CSV Error: {err}")
            else:
                st.success(f"✅ {len(df)} candidates loaded")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("🚀 Generate All Outreach", use_container_width=True):
                    key_valid, key_error = validate_api_key(GROQ_API_KEY or "")
                    if not key_valid:
                        st.error(key_error)
                        st.stop()

                    with st.spinner(f"Generating outreach for {len(df)} candidates..."):
                        results, success_count, failure_count = process_bulk(
                            df=df,
                            api_key=GROQ_API_KEY,
                            tone=st.session_state.tone,
                            platform=st.session_state.platform,
                            generate_fn=generate_outreach
                        )

                    st.session_state.bulk_results = results

                    col_s, col_f = st.columns(2)
                    with col_s:
                        st.success(f"✅ {success_count} generated successfully")
                    with col_f:
                        if failure_count:
                            st.error(f"❌ {failure_count} failed")

                    # Export
                    csv_data = export_bulk_csv(results)
                    txt_data = export_bulk_txt(results)

                    exp1, exp2 = st.columns(2)
                    with exp1:
                        if csv_data:
                            st.download_button(
                                "📊 Export CSV",
                                data=csv_data,
                                file_name="bulk_outreach.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    with exp2:
                        st.download_button(
                            "📄 Export TXT",
                            data=txt_data,
                            file_name="bulk_outreach.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

        except Exception:
            st.error("We couldn't process that file. Please check the format and try again.")
