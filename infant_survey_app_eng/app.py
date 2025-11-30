
import streamlit as st  # Main library for building UI
import json  # Module for reading/writing survey data
import os  # Module for file path and env vars
import io  # Module for memory buffer (PDF)
import re  # Regex module for string processing
import glob  # Module for listing files
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- [API Configuration] ---
os.environ["OPENAI_API_KEY"] = "sk-" 

# --- [Library Load Exception Handling] ---
try:
    # Modules for PDF generation (ReportLab)
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    # Modules for AI features (LangChain)
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    pass

# Custom modules
from modules.persistence import save_response
from modules.survey_schema import SurveyPack, Question

# Streamlit page settings
st.set_page_config(page_title="Our Children's Pediatrics Survey", layout="wide")

# Constants
SURVEY_PATH = "config/questionnaires/px_previsit_1.0.0.json"
RESP_DIR = "data/responses"

# --- [Functions: Stats/Feedback/AI/PDF] ---

def calculate_stats(q_id, q_type):
    """
    Shows statistics on how many others answered this question.
    """
    try:
        if not os.path.exists(RESP_DIR):
            return None

        files = glob.glob(os.path.join(RESP_DIR, "*.json"))
        if not files:
            return None

        return f"{len(files)} other guardians have answered this question."
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def get_ai_feedback_message(q_text, answer, months_old):
    """
    AI analyzes the answer and provides 'Immediate Warning/Advice'.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return None

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

        system_prompt = """
        You are a pediatric specialist AI. 
        Analyze the child's age (months), question, and guardian's answer to determine if 'Clinical Attention' is needed.

        [Analysis Rules]
        1. If the answer is within normal medical range or no urgent advice is needed, ONLY print "PASS". (No explanation)
        2. If there is a suspicion of developmental delay or pathological symptoms requiring 'Attention', write a 1-sentence advice in the format below.
           Format: "⚠️ [Key Advice]"

        [Precautions]
        - Do NOT add fluff like "It is normal". ONLY output "PASS" or "⚠️ ...".
        - Answer in English.
        """

        user_prompt = f"""
        [Data]
        - Age: {months_old} months
        - Question: {q_text}
        - Answer: {answer}

        Analysis Result:
        """

        messages = [("system", system_prompt), ("human", user_prompt)]
        response = llm.invoke(messages)
        feedback = response.content.strip()

        if feedback == "PASS":
            return None
        if not feedback.startswith("⚠️"):
            return None

        return feedback
    except:
        return None

def check_feedback(q, val, months_old):
    if not val: return None
    return get_ai_feedback_message(q.text, str(val), months_old)

def generate_clinical_summary(responses, child_info):
    """
    Generates a 'Clinical Summary Report' after survey completion.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return "API Key is not set in the code."

    try:
        context = ""
        for item in responses:
            ans = item['answer']
            # Skip negative answers for summary focus
            if ans and ans not in ["No", "Not at all", "None"]: 
                context += f"- Q: {item['text']}\n  A: {ans}\n"
        if not context: context = "No significant findings."

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        prompt = ChatPromptTemplate.from_messages([
                    ("system", """
                    You are an AI assistant (CDSS) for a pediatrician. 
                    Analyze the patient's survey data and write a report in English.
                    [Rules]
                    1. Summarize key symptoms.
                    2. List potential suspected conditions (Probability: High/Medium).
                    3. Provide recommendation points for the doctor.
                    4. End with "※ Accurate diagnosis is made by a doctor."
                    """),
                    ("human", f"""
                    [Patient Info]
                    Name: {child_info['name']}, Gender: {child_info['gender']}
                    Age: {child_info['months_old']} months ({child_info['days_old']} days old)

                    [Survey Content]
                    {context}
                    """)
                ])
        return (prompt | llm).invoke({}).content
    except Exception as e:
        return f"Error during AI analysis: {str(e)}"

def create_pdf_report(payload):
    """
    Converts result data into a PDF file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Use standard font for English
    font_name = 'Helvetica'

    # Define styles
    title_style = ParagraphStyle('KT', parent=styles['Heading1'], fontName=font_name, fontSize=18, alignment=1)
    head_style = ParagraphStyle('KH', parent=styles['Heading3'], fontName=font_name, fontSize=12, textColor='navy', spaceBefore=10)
    norm_style = ParagraphStyle('KN', parent=styles['Normal'], fontName=font_name, fontSize=10)

    story = [Paragraph("Pediatric Pre-visit Survey Results", title_style), Spacer(1, 20)]
    info = payload['child_info']
    story.append(Paragraph(f"Name: {info['name']} ({info['gender']}) | Age: {info['months_old']} months", norm_style))
    story.append(Spacer(1, 10))

    # AI Summary
    story.append(Paragraph("<b>[AI Clinical Analysis Report]</b>", head_style))
    story.append(Paragraph(payload.get('ai_summary','').replace('\n','<br/>'), norm_style))
    story.append(Spacer(1, 15))

    # Detailed Responses
    story.append(Paragraph("<b>[Survey Details]</b>", head_style))
    for r in payload['responses']:
        story.append(Paragraph(f"Q. {r['text']}<br/>A. <b>{r['answer']}</b>", norm_style))
        story.append(Spacer(1, 5))

    doc.build(story)
    buffer.seek(0)
    return buffer

def find_matching_index(days, age_labels):
    """
    Finds the correct survey age group index based on days old.
    """
    for i, label in enumerate(age_labels):
        # Find "4~6 months" pattern
        m = re.search(r"(\d+)\s*~\s*(\d+)\s*months", label.lower())
        if m: 
            if int(m.group(1)) <= (days//30) <= int(m.group(2)): return i
        # Find "14~35 days" pattern
        m2 = re.search(r"(\d+)\s*~\s*(\d+)\s*days", label.lower())
        if m2:
            if int(m2.group(1)) <= days <= int(m2.group(2)): return i
    return 0

def age_sort_key(s):
    """
    Sort key for age labels.
    """
    s = s.lower().replace(" ","")
    if "days" in s: return int(re.match(r"(\d+)", s).group(1))
    if "months" in s: return int(re.match(r"(\d+)", s).group(1)) * 30
    return 9999

# ================= MAIN APP =================

# --- Sidebar: Chatbot ---
with st.sidebar:
    st.header("💬 Pediatric AI Agent")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me anything about the survey questions. I'm here to help."}
        ]

    chat_container = st.container(height=400)
    for msg in st.session_state.messages:
        chat_container.chat_message(msg["role"]).write(msg["content"])

    if user_q := st.chat_input("Type your question..."):
        chat_container.chat_message("user").write(user_q)
        st.session_state.messages.append({"role": "user", "content": user_q})

        if "rag" not in st.session_state:
            try:
                from agents.chains import get_rag_chain
                st.session_state.rag = get_rag_chain()
            except: st.session_state.rag = None

        with chat_container.chat_message("assistant"):
            with st.spinner("Thinking..."):
                rag_answer = ""
                if st.session_state.rag:
                    try:
                        out = st.session_state.rag.invoke({"question": user_q})
                        rag_answer = out.get("answer", "")
                    except: pass

                recent_history = st.session_state.messages[-5:]
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent_history])

                prompt_template = f"""
                You are a kind and professional pediatric counseling AI.
                Answer in English.
                [History] {history_text}
                [Medical Info] {rag_answer}
                [Current Question] {user_q}
                """

                llm_agent = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.environ["OPENAI_API_KEY"])
                full_response = llm_agent.invoke(prompt_template).content

                st.write(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Main Screen: Survey ---

try:
    with open(SURVEY_PATH, "r", encoding="utf-8") as f: raw = json.load(f)
    pack = SurveyPack(**raw)
except: st.error("Failed to load data"); st.stop()

st.title("Pediatric Pre-visit Survey")
st.markdown("---")

# --- User Info Input ---
c1, c2, c3 = st.columns([1,1,2])
with c1: 
    child_name = st.text_input("Child's Name", placeholder="e.g., John Doe")
    gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
with c2:
    dob = st.date_input("Date of Birth", value=date.today(), max_value=date.today())
    days_diff = (date.today() - dob).days
    months_old = days_diff // 30
    st.caption(f"👶 **{days_diff} days old** ({months_old} months)")

with c3:
    age_list = sorted(list({q.age for q in pack.questions}), key=age_sort_key)
    matched_idx = find_matching_index(days_diff, age_list)

    if "last_dob" not in st.session_state:
        st.session_state.last_dob = dob

    if st.session_state.last_dob != dob:
        st.session_state.last_dob = dob
        if 0 <= matched_idx < len(age_list):
            st.session_state.selected_age = age_list[matched_idx]
            st.rerun()

    if "selected_age" not in st.session_state:
        if age_list:
            st.session_state.selected_age = age_list[matched_idx if matched_idx < len(age_list) else 0]

    sel_age = st.selectbox("Select Age Group", age_list, key="selected_age")

qs = [q for q in pack.questions if q.age == sel_age]

# --- Progress Bar ---
ans_cnt = 0
current_page_q_ids = [q.id for q in qs]
for k, v in st.session_state.items():
    if k.startswith("ans_") and v:
        if any(q_id in k for q_id in current_page_q_ids):
            ans_cnt += 1

st.progress(min(ans_cnt / len(qs), 1.0) if qs else 0, f"Progress (Approx) {int(min(ans_cnt/len(qs), 1.0)*100 if qs else 0)}%")

# --- Render Questions ---
if not qs: 
    st.info("No questions available.")
else:
    cats = sorted(list({q.category for q in qs}))
    tabs = st.tabs([f"{c}" for c in cats])
    final_answers = []

    for tab, cat in zip(tabs, cats):
        with tab:
            cqs = [q for q in qs if q.category == cat]

            for idx, q in enumerate(cqs):
                st.markdown(f"#### {q.text}")
                if q.help: st.caption(f"ℹ️ {q.help}")

                k = f"ans_{q.id}_{cat}_{idx}"

                val = None
                if q.qtype == "single": 
                    val = st.radio("Select", q.options or ["Yes","No"], key=k, horizontal=True, index=None)
                elif q.qtype == "multi": 
                    val = st.multiselect("Select", q.options or [], key=k)
                elif q.qtype == "scale": 
                    val = st.radio("Degree", options=q.options or ["Never","Sometimes","Often","Always"], key=k, horizontal=True, index=None)
                elif q.qtype == "number": 
                    val = st.number_input("Number", step=1, key=k, value=None)
                else: 
                    val = st.text_area("Input", key=k)

                if val is not None and val != "" and val != []:
                    stat_msg = calculate_stats(q.id, q.qtype)
                    if stat_msg: st.info(stat_msg, icon="📊")

                    feedback_msg = check_feedback(q, val, months_old)
                    if feedback_msg: st.warning(feedback_msg, icon="👨‍⚕️")

                with st.expander("💡 Detailed Info"):
                    if q.criteria: st.write(f"**Criteria**: {q.criteria}")
                    if q.actions: st.write(f"**Action**: {q.actions}")

                st.divider()
                final_answers.append({"id":q.id, "category":q.category, "text":q.text, "answer":val})

# --- Footer: Submit & Upload ---
st.markdown("### 📎 Attachments")
c_f, c_s = st.columns([2,1])
with c_f: up = st.file_uploader("Upload", type=["png","jpg","pdf"])
with c_s: 
    st.write("<br>", unsafe_allow_html=True)
    sub = st.button("Submit", type="primary", use_container_width=True)

# --- Submit Logic ---
if sub:
    if not child_name: st.warning("Child's name is required")
    else:
        c_info = {"name":child_name, "gender":gender, "dob":dob.isoformat(), "months_old":months_old, "days_old":days_diff, "age_group":sel_age}

        with st.spinner("Analyzing with AI..."):
            ai_sum = generate_clinical_summary(final_answers, c_info)

        payload = {
            "submitted_at": datetime.now().isoformat(),
            "child_info": c_info,
            "attachment": up.name if up else None,
            "ai_summary": ai_sum,
            "responses": final_answers
        }
        save_response(payload)
        st.success("Submission Complete!")

        with st.expander("📋 AI Analysis Result", expanded=True): st.info(ai_sum)

        if "messages" in st.session_state:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📝 **[Analysis Result]** has arrived.\n\n{ai_sum}\n\nFeel free to ask if you have questions."
            })

        try:
            pdf = create_pdf_report(payload)
            st.download_button("📄 Download PDF", pdf, f"Result_{child_name}.pdf", "application/pdf")
        except Exception as e:
            st.error(f"PDF Generation Failed: {e}")
