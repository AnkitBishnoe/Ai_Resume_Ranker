import streamlit as st
import plotly.graph_objects as go
from resume_parser import extract_text_from_pdf
from scoring_engine import calculate_similarity_score, get_keyword_gap
from jobs_db import suggest_jobs
from storage import save_screening, load_history, clear_history

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14;
    color: #e8e9ed;
}
.stApp { background: #0d0f14; }

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1a1d27 0%, #0f1118 100%);
    border: 1px solid #2a2d3a;
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,179,237,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 6px 0;
           background: linear-gradient(90deg, #63b3ed, #b794f4); -webkit-background-clip: text;
           -webkit-text-fill-color: transparent; }
.hero p { color: #8892a4; font-size: 1.05rem; margin: 0; font-weight: 300; }

.card {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}

.pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 3px;
}
.pill-green  { background: #1a3a2a; color: #68d391; border: 1px solid #276749; }
.pill-red    { background: #3a1a1f; color: #fc8181; border: 1px solid #742a2a; }
.pill-blue   { background: #1a2a3a; color: #63b3ed; border: 1px solid #2a4a6a; }
.pill-purple { background: #2a1a3a; color: #b794f4; border: 1px solid #553c9a; }

.cat-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 10px 0 4px 0;
}

.job-card {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}
.job-card:hover { border-color: #63b3ed; }
.job-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
             color: #63b3ed; margin-bottom: 4px; }
.job-meta  { font-size: 0.82rem; color: #6b7280; margin-bottom: 8px; }
.job-desc  { font-size: 0.9rem; color: #9ca3af; line-height: 1.5; }
.job-badge { background: #1a1d27; color: #8892a4; border: 1px solid #2a2d3a;
              border-radius: 999px; font-size: 0.75rem; padding: 2px 10px; margin-left: 8px; }

.stButton > button {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 12px 24px;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.stTabs [data-baseweb="tab-list"] { background: #13161f; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #1e2130; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #8892a4; border-radius: 8px; border: none; font-family: 'Syne', sans-serif; font-weight: 700; }
.stTabs [aria-selected="true"] { background: #1e2436 !important; color: #63b3ed !important; }

.improvement-bar {
    background: #1a1d27;
    border-radius: 4px;
    height: 8px;
    width: 100%;
    margin: 8px 0;
}
.improvement-fill {
    background: linear-gradient(90deg, #f6ad55, #fc8181);
    height: 100%;
    border-radius: 4px;
}

.stFileUploader { background: #13161f; border: 1px dashed #2a2d3a; border-radius: 10px; }
textarea { background: #13161f !important; color: #e8e9ed !important; border: 1px solid #2a2d3a !important; border-radius: 10px !important; }
.stSpinner { color: #63b3ed; }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚡ ResumeIQ</h1>
    <p>Semantic AI-powered resume analysis · Real job matching · Keyword gap insights</p>
</div>
""", unsafe_allow_html=True)

# ── Helper: render categorized keyword pills ─────────────────────────────────
def render_categorized_keywords(categorized: dict, pill_class: str):
    """Render keyword pills grouped by real-world category."""
    if not categorized:
        return
    for cat_label, kws in categorized.items():
        st.markdown(f'<div class="cat-label">{cat_label}</div>', unsafe_allow_html=True)
        pills = "".join(f'<span class="pill {pill_class}">{k}</span>' for k in kws)
        st.markdown(pills, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎯 ATS Score", "💼 Job Matches", "📜 History"])

# ═══════════════════════════════════════════════════════════
# TAB 1 — ATS Score
# ═══════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 📄 Upload Resume")
        resume_file = st.file_uploader("PDF only", type="pdf", key="tab1_resume", label_visibility="collapsed")
        if resume_file:
            st.success(f"✅ {resume_file.name}")

    with col2:
        st.markdown("#### 📋 Job Description")
        job_desc = st.text_area("Paste JD here", height=160, placeholder="We are looking for a Python engineer with...", label_visibility="collapsed")

    analyze_btn = st.button("Analyze Match ⚡", use_container_width=True, key="analyze")

    if analyze_btn:
        if not resume_file:
            st.error("⚠️ Please upload your resume.")
        elif not job_desc.strip():
            st.error("⚠️ Please paste a job description.")
        else:
            with st.spinner("Running semantic analysis..."):
                resume_text = extract_text_from_pdf(resume_file)

            if not resume_text:
                st.error("Could not extract text. Make sure the PDF is not scanned/image-only.")
            else:
                with st.spinner("Calculating score & keyword gap..."):
                    score = calculate_similarity_score(resume_text, job_desc)
                    gap = get_keyword_gap(resume_text, job_desc)

                    save_screening({
                        "resume_name": resume_file.name,
                        "score": score,
                        "matched": gap["matched"],
                        "missing": gap["missing"]
                    })

                st.divider()

                # ── Score Display ──
                r1, r2, r3 = st.columns([1, 1, 1])

                if score >= 70:
                    color, label, emoji = "#68d391", "Strong Match", "🟢"
                elif score >= 33:
                    color, label, emoji = "#f6ad55", "Moderate Match", "🟡"
                else:
                    color, label, emoji = "#fc8181", "Low Match", "🔴"

                with r1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        number={"suffix": "%", "font": {"size": 36, "color": color, "family": "Syne"}},
                        gauge={
                            "axis": {"range": [0, 100], "tickcolor": "#444"},
                            "bar": {"color": color},
                            "bgcolor": "#1a1d27",
                            "bordercolor": "#2a2d3a",
                            "steps": [
                                {"range": [0, 33],  "color": "#1f1218"},
                                {"range": [33, 70], "color": "#1a1810"},
                                {"range": [70, 100], "color": "#0f1a14"},
                            ],
                        },
                        title={"text": f"{emoji} {label}", "font": {"size": 16, "color": "#e8e9ed", "family": "Syne"}},
                    ))
                    fig.update_layout(
                        paper_bgcolor="#13161f", plot_bgcolor="#13161f",
                        margin=dict(t=40, b=0, l=20, r=20), height=220
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with r2:
                    st.markdown("**✅ Matched Keywords**")
                    if gap.get("categorized_matched"):
                        render_categorized_keywords(gap["categorized_matched"], "pill-green")
                    elif gap["matched"]:
                        pills = "".join(f'<span class="pill pill-green">{k}</span>' for k in gap["matched"])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color:#6b7280">None found</span>', unsafe_allow_html=True)

                with r3:
                    st.markdown("**❌ Missing Keywords**")
                    if gap.get("categorized_missing"):
                        render_categorized_keywords(gap["categorized_missing"], "pill-red")
                    elif gap["missing"]:
                        pills = "".join(f'<span class="pill pill-red">{k}</span>' for k in gap["missing"])
                        st.markdown(pills, unsafe_allow_html=True)
                        st.markdown('<br><small style="color:#6b7280">💡 Add these to boost your ATS score</small>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color:#68d391">Great — no major gaps!</span>', unsafe_allow_html=True)

    # ── Multiple Resume Comparison ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 👥 Compare Multiple Resumes")
    st.markdown("<p style='color: #8892a4;'>Upload multiple resumes to see which one best matches the Job Description.</p>", unsafe_allow_html=True)

    multi_col1, multi_col2 = st.columns([1, 1], gap="large")
    with multi_col1:
        st.markdown("#### 📄 Upload Resumes")
        multi_resumes = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True, key="multi_resumes", label_visibility="collapsed")

    with multi_col2:
        st.markdown("#### 📋 Job Description")
        multi_jd = st.text_area("Paste JD for Comparison", height=120, placeholder="We are looking for...", key="multi_jd", label_visibility="collapsed")

    compare_btn = st.button("Compare Resumes ⚡", use_container_width=True, key="compare_btn")

    if compare_btn:
        if not multi_resumes or len(multi_resumes) < 2:
            st.error("⚠️ Please upload at least two resumes to compare.")
        elif not multi_jd.strip():
            st.error("⚠️ Please paste a job description.")
        else:
            with st.spinner("Comparing resumes..."):
                results = []
                for r_file in multi_resumes:
                    r_text = extract_text_from_pdf(r_file)
                    if r_text:
                        r_score = calculate_similarity_score(r_text, multi_jd)
                        r_gap = get_keyword_gap(r_text, multi_jd)
                        results.append({
                            "name": r_file.name,
                            "score": r_score,
                            "matched": len(r_gap["matched"]),
                            "missing": len(r_gap["missing"])
                        })

                if results:
                    results = sorted(results, key=lambda x: x["score"], reverse=True)
                    st.success(f"🏆 Top Match: **{results[0]['name']}** ({results[0]['score']}%)")

                    st.markdown("#### Comparison Results")
                    for i, res in enumerate(results):
                        color = "#68d391" if i == 0 else "#f6ad55" if res['score'] >= 33 else "#fc8181"
                        st.markdown(f'''
                        <div class="card" style="border-left: 4px solid {color}; padding: 12px 16px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 1.1em;">{res['name']}</strong>
                                <span style="font-family: 'Syne', sans-serif; font-weight: 700; color: {color}; font-size: 1.2em;">{res['score']}%</span>
                            </div>
                            <div style="color: #8892a4; font-size: 0.9em; margin-top: 4px;">
                                Matched Keywords: {res['matched']} | Missing Keywords: {res['missing']}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 2 — Live Job Suggestions
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 📄 Upload Resume for Job Matching")
    resume_file2 = st.file_uploader("PDF only", type="pdf", key="tab2_resume", label_visibility="collapsed")
    if resume_file2:
        st.success(f"✅ {resume_file2.name}")

    suggest_btn = st.button("Find My Best Roles 🔍", use_container_width=True, key="suggest")

    if suggest_btn:
        if not resume_file2:
            st.error("⚠️ Please upload your resume.")
        else:
            with st.spinner("Analyzing resume for matches…"):
                resume_text2 = extract_text_from_pdf(resume_file2)

            if not resume_text2:
                st.error("Could not extract text from this PDF.")
            else:
                with st.spinner("Ranking matches..."):
                    jobs = suggest_jobs(resume_text2, top_n=5)

                if not jobs:
                    st.warning("No matches found for your profile. Try refining your resume summary.")
                else:
                    st.markdown(f"### Top {len(jobs)} Matches")
                    for job in jobs:
                        badge = '<span class="job-badge">MATCHED</span>'
                        company = f' · {job["company"]}' if job.get("company") else ""
                        tags_html = ""
                        if job.get("tags"):
                            tags_html = f'<div style="margin-top:6px">{" ".join(f"<span class=\"pill pill-blue\">{t.strip()}</span>" for t in job["tags"].split(",") if t.strip())}</div>'
                        url_btn = f'<a href="{job["url"]}" target="_blank" style="color:#63b3ed;font-size:0.85rem;text-decoration:none;">🔗 View Job →</a>' if job.get("url") else ""

                        st.markdown(f"""
                        <div class="job-card">
                            <div class="job-title">{job['title']}{badge}</div>
                            <div class="job-meta">{company} Match: <strong style="color:#68d391">{job['match_score']}%</strong> {url_btn}</div>
                            <div class="job-desc">{job['description'][:280]}{'…' if len(job['description']) > 280 else ''}</div>
                            {tags_html}
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='margin-top: 12px;'><strong>🚀 Skills to Improve for this role:</strong></div>", unsafe_allow_html=True)
                        match_details = get_keyword_gap(resume_text2, job.get('description', '') + " " + job.get('tags', ''))

                        if match_details.get("categorized_missing"):
                            render_categorized_keywords(match_details["categorized_missing"], "pill-red")
                        elif match_details["missing"]:
                            pills = "".join(f'<span class="pill pill-red">{k}</span>' for k in match_details["missing"][:8])
                            st.markdown(pills, unsafe_allow_html=True)

                        if match_details["missing"]:
                            gap_percent = max(0, 100 - int(job['match_score']))
                            st.markdown(f"""
                            <div style="margin-top:10px; font-size:0.85rem; color:#8892a4;">Improvement needed: {gap_percent}%</div>
                            <div class="improvement-bar">
                                <div class="improvement-fill" style="width: {gap_percent}%;"></div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.success("You're a great fit for this role's specific skills!")

# ═══════════════════════════════════════════════════════════
# TAB 3 — History
# ═══════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("#### 📜 Recent Screenings")
    with c2:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_history()
            st.rerun()

    history = load_history()

    if not history:
        st.info("No screenings yet. Go to the ATS Score tab to start!")
    else:
        for entry in reversed(history):
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{entry['resume_name']}**")
                    st.caption(f"📅 {entry['timestamp']}")
                with c2:
                    st.markdown(f"### {entry['score']}%")

                if entry['matched']:
                    p = "".join(f'<span class="pill pill-green" style="font-size:0.7rem;">{k}</span>' for k in entry['matched'][:5])
                    st.markdown(p, unsafe_allow_html=True)

                st.divider()
