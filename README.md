# 🎓 AI Scholarship Assistant

A conversational AI-powered web app to help Indian students discover scholarships — no forms, just chat!

## Tech Stack
- **Backend**: Python Flask
- **Database**: SQLite (15 real scholarships pre-loaded)
- **Frontend**: HTML, CSS, JavaScript
- **NLP**: Rule-based keyword extraction (no ML required)

## Setup & Run

```bash
# 1. Install dependency
pip install flask

# 2. Start the app
python run.py

# 3. Open browser
http://localhost:5000
```

## Features
- 💬 ChatGPT-style chat interface (dark/light mode)
- 🤖 Step-by-step conversational data collection (7 steps)
- 📊 Smart eligibility matching engine
- 🎯 15 real Indian scholarships in database
- 📱 Mobile responsive
- 🔄 Restart & update answers mid-conversation
- ❓ FAQ: documents, how to apply, eligibility
- 📈 Progress bar showing current step

## Project Structure
```
scholarship_app/
├── app.py              # Flask backend + chat logic
├── database.py         # SQLite setup + scholarship matching
├── nlp_engine.py       # Rule-based NLP (intent + extraction)
├── run.py              # Startup script
├── scholarships.db     # SQLite database (auto-created)
├── templates/
│   └── index.html      # Main chat UI
└── static/
    ├── css/style.css   # Full styling
    └── js/chat.js      # Chat frontend logic
```

## Scholarships Included
1. Central Sector Scheme (Ministry of Education)
2. Post Matric Scholarship for SC Students
3. Begum Hazrat Mahal National Scholarship (Girls)
4. AICTE Pragati Scholarship (Girls, B.Tech)
5. National Fellowship for ST Students
6. PM Scholarship Scheme (Ex-Servicemen wards)
7. INSPIRE Scholarship (Science)
8. Vidyasaarathi Scholarship
9. Post Matric Scholarship for OBC
10. Ishan Uday (North East students)
11. Reliance Foundation UG Scholarships
12. HDFC Bank Parivartan ECS Scholarship
13. Tata Capital Pankh Scholarship
14. Maulana Azad National Fellowship
15. Kishori Shakti Yojana (Telangana, Girls)
