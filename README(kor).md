# 우리아이들병원 Pediatric Pre-visit Survey & CDSS Agent  
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)  
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)  
![OpenAI](https://img.shields.io/badge/LLM-OpenAI_GPT--4o--mini-412991.svg)  
![LangChain](https://img.shields.io/badge/Framework-LangChain-1C3C3C.svg)  

---

## 프로젝트 소개
**Smart Pediatric Pre-visit Survey & CDSS Agent**는 우리아이들 소아병원 데이터로 개발된, 한국어와 영어를 모두 지원하는 소아과용 지능형 사전 문진 및 임상 의사결정 지원 시스템입니다.

본 시스템은 다음 기능을 제공합니다:  
- **연령 맞춤형 동적 문진 시스템**,  
- **RAG 기반 AI 육아 상담 챗봇**,  
- 의료진을 위한 **임상 요약 보고서 자동 생성**,  
- **실시간 위험 징후 감지**,  
- 보호자와 의료진을 위한 **PDF 리포트 다운로드 기능**.

다음과 같이 두 가지 언어 버전으로 구성됩니다:

```
infant_survey_app_kor/   # 한국어 UI 및 응답
infant_survey_app_eng/   # 영어 UI 및 응답
````

---

## 주요 기능 및 스크린샷

### 1. 자동 문진 생성 (Dynamic Survey Generation)  
아이의 생후 일수를 자동 계산하여 월령에 맞는 문진을 불러옵니다.  
<img width="623" height="302" alt="image" src="https://github.com/user-attachments/assets/40bc6b42-b5d1-4131-91ac-dcf253b8cbe6" />

---

### 2. AI 육아 상담 챗봇 (RAG 기반)  
벡터 검색을 통해 소아과 관련 문서들을 참조하며 근거 기반 Q&A를 제공합니다.  
<img width="621" height="308" alt="image" src="https://github.com/user-attachments/assets/2653369a-adac-4292-ac0a-5290e5617fd0" />

---

### 3. 의료진용 CDSS 임상 요약  
문진 응답을 기반으로 구조화된 임상 요약과 위험 요소를 생성합니다.  
<img width="621" height="291" alt="image" src="https://github.com/user-attachments/assets/0068bf6e-8ab8-4b32-90a9-e1d12079aab2" />

---

### 4. 실시간 위험 감지  
보호자의 입력 내용 중 긴급 또는 이상 증상이 감지되면 즉시 경고 메시지를 제공합니다.  
<img width="1641" height="675" alt="image" src="https://github.com/user-attachments/assets/6d396062-0389-4dc3-b019-ebd766d0eed6" />

---

### 5. PDF 리포트 생성  
보호자 및 의료진이 활용할 수 있는 상세 PDF 리포트를 다운로드할 수 있습니다.  
<img width="215" height="301" alt="image" src="https://github.com/user-attachments/assets/3e4340de-5994-4f57-b4a5-f0251c167f6a" />

---

## 디렉토리 구조
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
````

---

## 🛠️ 기술 스택

* Frontend: Streamlit
* AI / LLM: LangChain, OpenAI GPT-4o-mini
* Vector DB: ChromaDB 또는 FAISS
* Utilities: Pydantic, ReportLab
* Format: Python, Jupyter Notebook (setup)

---

## 🔧 설치 및 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/yourname/pediatric-previsit-cdss.git
cd pediatric-previsit-cdss
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (중요)

`.env` 파일 생성:

```env
OPENAI_API_KEY=your_api_key_here
```

⚠️ **API Key는 절대 GitHub에 업로드하지 마세요.**
`.gitignore`를 사용하여 비밀정보를 반드시 보호하세요.

---

### 4. 애플리케이션 실행

#### 한국어 버전 실행

```bash
streamlit run infant_survey_app_kor/streamlit_app.py
```

#### 영어 버전 실행

```bash
streamlit run infant_survey_app_eng/streamlit_app.py
```

---

## 라이선스

MIT License © 2025 Yoon

```
