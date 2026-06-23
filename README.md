# AI Candidate Outreach Generator

> Create personalized outreach messages that candidates actually reply to.

---

## What It Does

Input candidate details → get a complete outreach package instantly.

Built for recruiters spending hours writing personalized messages manually.

---

## Generated Output

```
✅ Connection request note (300 char limit enforced)
✅ Full outreach message (150-200 words)
✅ Follow-up message (Day 4, no response)
✅ Subject lines (email platform)
✅ Personalization score
✅ Spam risk analysis
✅ A/B variations
✅ Bulk CSV mode
```

---

## Stack

```
Python · Streamlit · LangChain · Groq API
```

---

## Run Locally

```bash
git clone https://github.com/recruitment-ai-beast/ai-outreach-generator
cd ai-outreach-generator
pip install -r requirements.txt
cp .env.example .env
# Add GROQ_API_KEY to .env
streamlit run app.py
```

---

## Deploy on Streamlit Cloud

```
1. Push to GitHub
2. share.streamlit.io → Connect repo
3. Main file: app.py
4. Secrets: GROQ_API_KEY = "your_key"
5. Deploy
```

---

## Part of

**BEAST — Vertical AI Engineer**
Recruitment Automation Suite.
[LinkedIn](https://www.linkedin.com/in/beast-builds-ai) ·
[Resume Screener](https://ai-for-resume-screening.streamlit.app/) ·
[JD Generator](https://ai-jd-generator.streamlit.app/)