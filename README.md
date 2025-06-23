# 🧠 Multi-Agent Based Smart Resume Career Advisor

Smart Resume Career Advisor is an AI-powered web application built with **Streamlit** and the **Agno framework**. It helps users analyze their resumes, extract key skills, suggest suitable job roles, search for job opportunities, and estimate salaries — all in one intuitive interface.

![Smart Resume Advisor Screenshot](https://via.placeholder.com/900x400.png?text=Smart+Resume+Career+Advisor+UI+Mockup)

---

## 🚀 Features

- **📄 Resume Text Extraction:** Upload your PDF resume and extract structured data like skills, education, and experience.
- **🎯 AI-Powered Role Matching:** Suggests 3–5 job roles based on your resume and optional preferences.
- **💼 Job Listing Search:** Uses RapidAPI’s JSearch to find live job openings matching your profile.
- **💰 Salary Estimation:** Estimates salary ranges for each recommended job title.
- **📊 Visual Insights:** Displays extracted skills, matching job roles, and job listings with interactive UI components.

---

## 🧠 Powered By

- [Streamlit](https://streamlit.io/) — Fast and interactive data web app framework.
- [Agno Framework](https://github.com/agnos-ai/agno) — Multi-agent orchestration with tool and LLM integration.
- [Groq LLaMA 3.1](https://groq.com) — High-performance large language models.
- [RapidAPI - JSearch & Salary API](https://rapidapi.com/) — Job listings and salary estimate endpoints.
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) — For extracting text from PDF resumes.
- [dotenv](https://pypi.org/project/python-dotenv/) — For managing environment variables securely.

---

## 🧪 How It Works

1. **Upload your resume (PDF only).**
2. **AI agents** extract relevant information and skills from the text.
3. **Job role suggestions** are generated based on your experience and skills.
4. **Live job searches** are performed via RapidAPI.
5. **Salary estimates** are provided per role and location.

---

## 🛠️ Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Muntasir-Ayan/Career-Advisor.git
cd smart-resume-career-advisor
```
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
3. **Set up .env file:**Create a .env file in the root directory with the following variables:
```bash
        GROQ_API_KEY=your_groq_api_key
        RAPIDAPI_KEY=your_rapidapi_key
```
4. **Run the app:**
```bash
streamlit run app.py
``