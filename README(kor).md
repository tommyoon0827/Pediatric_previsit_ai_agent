# 우리아이들병원 Pediatric Pre-visit Survey & CDSS Agent  
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)  
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)  
![OpenAI](https://img.shields.io/badge/LLM-OpenAI_GPT--4o--mini-412991.svg)  
![LangChain](https://img.shields.io/badge/Framework-LangChain-1C3C3C.svg)  

**For Korean documentation, please see [README_KR.md](./README_KR.md).**

---

## Project Overview
**Smart Pediatric Pre-visit Survey & CDSS Agent** is an intelligent pediatric pre-visit survey and clinical decision-support system developed using data from the Woori Children’s Hospital. It supports both Korean and English for seamless use in diverse clinical environments.

The system provides:  
- A **dynamic age-specific survey**,  
- A **RAG-based AI parenting assistant**,  
- Automated **clinical summary reports for physicians**,  
- **Real-time warning detection**, and  
- **Downloadable PDF reports** for caregivers and clinicians.

The repository includes two localized versions:


infant_survey_app_kor/ # Korean UI & responses
infant_survey_app_eng/ # English UI & responses


---

## Key Features & Screenshots

### 1. Dynamic Survey Generation  
Automatically calculates the child's age in days and loads the correct age-appropriate survey.  
<img width="623" height="302" alt="image" src="https://github.com/user-attachments/assets/40bc6b42-b5d1-4131-91ac-dcf253b8cbe6" />


---

### 2. AI Parenting Chatbot (RAG-based)  
Provides evidence-based Q&A using vector search over pediatric medical documents.  
<img width="621" height="308" alt="image" src="https://github.com/user-attachments/assets/2653369a-adac-4292-ac0a-5290e5617fd0" />


---

### 3. Clinical CDSS Summary for Physicians  
Generates a structured medical summary and risk notes based on survey responses.  
<img width="621" height="291" alt="image" src="https://github.com/user-attachments/assets/0068bf6e-8ab8-4b32-90a9-e1d12079aab2" />



---

### 4. Real-time Risk Detection  
Instant alerts fire when guardian inputs indicate urgent or abnormal symptoms.  
<img width="1641" height="675" alt="image" src="https://github.com/user-attachments/assets/6d396062-0389-4dc3-b019-ebd766d0eed6" />



---

### 5. PDF Report Generation  
Caregivers and clinicians can download a comprehensive PDF report.  
<img width="215" height="301" alt="image" src="https://github.com/user-attachments/assets/3e4340de-5994-4f57-b4a5-f0251c167f6a" />


---

##  Directory Structure
```plaintext
root/
│── README.md
│── README_KR.md
│── images/
│── infant_survey_app_kor/
│     ├── config/
│     ├── data/
│     ├── modules/
│     ├── agents/
│     └── streamlit_app.py
│── infant_survey_app_eng/
      ├── config/
      ├── data/
      ├── modules/
      ├── agents/
      └── streamlit_app.py

🛠️ Tech Stack
Frontend: Streamlit
AI / LLM: LangChain, OpenAI GPT-4o-mini
Vector DB: ChromaDB or FAISS
Utilities: Pydantic, ReportLab
Format: Python, Jupyter Notebook (setup)

🔧 Installation & Usage
1. Clone Repository
git clone https://github.com/yourname/pediatric-previsit-cdss.git
cd pediatric-previsit-cdss

2. Install Dependencies
pip install -r requirements.txt

3. Set Environment Variables (IMPORTANT)
Create a .env file:
OPENAI_API_KEY=your_api_key_here

Never commit your API keys to GitHub.
Use .gitignore to protect secrets.

4. Run the App
Korean version
streamlit run infant_survey_app_kor/streamlit_app.py


English version
streamlit run infant_survey_app_eng/streamlit_app.py

License
MIT License © 2025 Yoon
