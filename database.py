import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'scholarships.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT NOT NULL,
        min_gpa REAL DEFAULT 0,
        max_income REAL DEFAULT 99999999,
        category TEXT DEFAULT 'All',
        gender TEXT DEFAULT 'All',
        state TEXT DEFAULT 'All',
        deadline TEXT,
        amount TEXT,
        link TEXT,
        description TEXT,
        documents_required TEXT,
        course TEXT DEFAULT 'All',
        min_year INTEGER DEFAULT 1,
        max_year INTEGER DEFAULT 5
    )''')

    c.execute("SELECT COUNT(*) FROM scholarships")
    count = c.fetchone()[0]

    if count == 0:
        scholarships = [
            (
                "Central Sector Scheme of Scholarships",
                "Ministry of Education, Government of India",
                8.0, 800000, "All", "All", "All",
                "31 October 2025",
                "₹12,000/year (Fresher) - ₹20,000/year (PG)",
                "https://scholarships.gov.in",
                "For college & university students who scored above 80th percentile in Class XII. Covers first degree courses up to 3 years, B.Tech/BE up to 4 years.",
                "12th Marksheet, Income Certificate, Aadhaar, Bank Passbook, College Enrollment Letter",
                "All", 1, 4
            ),
            (
                "Post Matric Scholarship for SC Students",
                "Ministry of Social Justice & Empowerment",
                0.0, 250000, "SC", "All", "All",
                "15 November 2025",
                "₹570 - ₹1,200/month + maintenance allowance",
                "https://scholarships.gov.in",
                "Scholarship for Scheduled Caste students pursuing post-matriculation or post-secondary courses. Covers tuition fees and maintenance allowance.",
                "Caste Certificate, Income Certificate, Mark Sheets, Aadhaar, Bank Passbook",
                "All", 1, 5
            ),
            (
                "Begum Hazrat Mahal National Scholarship",
                "Maulana Azad Education Foundation",
                5.0, 200000, "All", "Female", "All",
                "30 September 2025",
                "₹5,000 - ₹6,000/year",
                "https://maef.net.in",
                "For meritorious girls from minority communities (Muslim, Christian, Sikh, Buddhist, Zoroastrian, Jain) studying in Class IX to XII and beyond.",
                "Minority Community Certificate, Income Certificate, Mark Sheets, Aadhaar, Bank Account",
                "All", 1, 4
            ),
            (
                "AICTE Pragati Scholarship for Girls",
                "All India Council for Technical Education (AICTE)",
                0.0, 800000, "All", "Female", "All",
                "31 October 2025",
                "₹50,000/year",
                "https://www.aicte-india.org/bureaus/bs/pragati",
                "For girl students pursuing technical education (degree/diploma). One scholarship per family. Covers tuition fee and incidentals.",
                "Aadhaar, Income Certificate, Fee Receipt, Bank Passbook, Enrollment Proof",
                "B.Tech", 1, 4
            ),
            (
                "National Fellowship and Scholarship for Higher Education of ST Students",
                "Ministry of Tribal Affairs",
                0.0, 600000, "ST", "All", "All",
                "31 December 2025",
                "₹3,000 - ₹10,000/month",
                "https://tribal.nic.in",
                "Scholarship for Scheduled Tribe students who have passed class XII and seeking admission in graduation/post-graduation in recognized institutions.",
                "ST Certificate, Income Certificate, Aadhaar, Class XII Marksheet, Bank Passbook",
                "All", 1, 5
            ),
            (
                "Prime Minister's Scholarship Scheme (PMSS)",
                "Ministry of Home Affairs",
                6.0, 999999, "All", "All", "All",
                "31 October 2025",
                "₹2,500 - ₹3,000/month",
                "https://ksb.gov.in/pmss.htm",
                "For wards and widows of Ex-Servicemen/Ex-Coast Guard personnel. Applicable for professional degree courses like B.Tech, MBBS, BDS, BCA, MBA.",
                "Ex-Serviceman Certificate, Mark Sheets, Income Certificate, Bank Passbook, Aadhaar",
                "All", 1, 5
            ),
            (
                "Inspire Scholarship (SHE)",
                "Department of Science & Technology (DST)",
                8.5, 999999, "All", "All", "All",
                "30 November 2025",
                "₹80,000/year + ₹20,000 mentorship grant",
                "https://online-inspire.gov.in",
                "Scholarship for Excellence in Science & Technology. For students who scored top 1% in Class XII and pursuing Natural/Basic Sciences at B.Sc/B.S/Integrated M.Sc level.",
                "Class XII Marksheet, Merit Certificate, Aadhaar, Bank Passbook",
                "B.Sc", 1, 3
            ),
            (
                "Vidyasaarathi Scholarship",
                "National Securities Depository Limited (NSDL)",
                7.0, 600000, "All", "All", "All",
                "Rolling Deadline",
                "₹10,000 - ₹50,000/year",
                "https://www.vidyasaarathi.co.in",
                "Multiple scholarships for students from economically weaker sections pursuing professional courses. Several corporate-sponsored schemes available.",
                "Income Certificate, Mark Sheets, Aadhaar, Bank Passbook, Enrollment Letter",
                "All", 1, 4
            ),
            (
                "Post Matric Scholarship for OBC Students",
                "Ministry of Social Justice & Empowerment",
                0.0, 100000, "OBC", "All", "All",
                "31 October 2025",
                "₹350 - ₹1,000/month + tuition fee",
                "https://scholarships.gov.in",
                "Financial assistance to OBC students for pursuing post-matriculation or post-secondary education. State-wise implementation.",
                "OBC Certificate, Income Certificate, Mark Sheets, Aadhaar, Bank Passbook",
                "All", 1, 5
            ),
            (
                "Ishan Uday Special Scholarship for North East",
                "University Grants Commission (UGC)",
                7.5, 450000, "All", "All", "North East",
                "30 September 2025",
                "₹5,400 - ₹7,800/month",
                "https://ishan.ugc.ac.in",
                "For students domiciled in North Eastern states pursuing general degree courses, technical and professional courses from recognized institutions.",
                "Domicile Certificate of NE State, Income Certificate, Mark Sheets, Aadhaar",
                "All", 1, 4
            ),
            (
                "Reliance Foundation Undergraduate Scholarships",
                "Reliance Foundation",
                7.5, 250000, "All", "All", "All",
                "30 November 2025",
                "₹2,00,000 over 4 years",
                "https://rf.foundation/scholarships",
                "For students from low-income families pursuing UG courses in STEM or Arts/Humanities. Includes academic excellence and leadership modules.",
                "Income Certificate, Mark Sheets, Aadhaar, Enrollment Letter, Bank Account",
                "All", 1, 1
            ),
            (
                "HDFC Bank Parivartan's ECS Scholarship",
                "HDFC Bank",
                5.5, 250000, "All", "All", "All",
                "31 August 2025",
                "₹75,000/year",
                "https://www.hdfcbank.com/personal/resources/learning-centre/pay/hdfc-bank-parivartan",
                "For meritorious students from economically disadvantaged families. Covers education costs including tuition, hostel, and other fees.",
                "Income Certificate, Mark Sheets, Aadhaar, Fee Structure, Bank Account",
                "All", 1, 4
            ),
            (
                "Tata Capital Pankh Scholarship",
                "Tata Capital",
                6.0, 250000, "All", "All", "All",
                "15 October 2025",
                "Up to ₹50,000/year",
                "https://www.tatacapital.com/about-us/csr/pankh-scholarship-programme.html",
                "Supporting meritorious students from financially weaker sections to pursue professional courses. Available for both UG and diploma students.",
                "Income Certificate, Mark Sheets, Aadhaar, College ID, Bank Passbook",
                "All", 1, 4
            ),
            (
                "Maulana Azad National Fellowship",
                "Ministry of Minority Affairs",
                0.0, 600000, "All", "All", "All",
                "31 December 2025",
                "₹25,000 - ₹28,000/month (PhD) + contingency grant",
                "https://maef.net.in",
                "For minority community students (Muslim, Christian, Buddhist, Sikh, Zoroastrian, Jain) pursuing M.Phil and PhD in Indian universities.",
                "Minority Certificate, Aadhaar, NET/JRF Score, Bank Account, Enrollment Letter",
                "PhD", 1, 5
            ),
            (
                "Kishori Shakti Yojana Scholarship (Telangana)",
                "Government of Telangana",
                5.0, 200000, "All", "Female", "Telangana",
                "31 October 2025",
                "₹10,000/year",
                "https://telanganaepass.cgg.gov.in",
                "State scholarship for girl students from Telangana pursuing higher education. Encourages female education and reduces dropout rates.",
                "Domicile Certificate, Income Certificate, Mark Sheets, Aadhaar, Bank Account",
                "All", 1, 4
            ),
        ]

        c.executemany('''INSERT INTO scholarships 
            (name, provider, min_gpa, max_income, category, gender, state, deadline, amount, link, description, documents_required, course, min_year, max_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', scholarships)

    conn.commit()
    conn.close()

def get_all_scholarships_summary():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, provider, amount, category, gender, state FROM scholarships")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def match_scholarships(user_profile):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM scholarships")
    all_scholarships = c.fetchall()
    conn.close()

    matches = []
    gpa = user_profile.get('gpa', 0)
    income = user_profile.get('income', 999999)
    category = user_profile.get('category', 'General')
    gender = user_profile.get('gender', 'Male')
    state = user_profile.get('state', '')
    course = user_profile.get('course', '')
    year = user_profile.get('year', 1)

    for s in all_scholarships:
        reasons = []
        eligible = True

        if gpa < s['min_gpa']:
            eligible = False
        else:
            if s['min_gpa'] > 0:
                reasons.append(f"✅ GPA {gpa}/10 meets minimum {s['min_gpa']}/10")

        if income > s['max_income']:
            eligible = False
        else:
            if s['max_income'] < 99999999:
                inc_lakh = round(s['max_income'] / 100000, 1)
                reasons.append(f"✅ Income within ₹{inc_lakh}L limit")

        sch_category = s['category']
        if sch_category != 'All':
            if sch_category != category:
                eligible = False
            else:
                reasons.append(f"✅ {category} category eligible")

        sch_gender = s['gender']
        if sch_gender != 'All':
            if sch_gender != gender:
                eligible = False
            else:
                reasons.append(f"✅ Open for {gender} students")

        sch_state = s['state']
        if sch_state not in ('All', 'North East'):
            if state.lower() != sch_state.lower():
                eligible = False
            else:
                reasons.append(f"✅ Available in {state}")
        elif sch_state == 'North East':
            ne_states = ['Assam', 'Meghalaya', 'Manipur', 'Nagaland', 'Mizoram', 'Tripura', 'Arunachal Pradesh', 'Sikkim']
            if state not in ne_states:
                eligible = False
            else:
                reasons.append(f"✅ NE state domicile qualifies")

        sch_course = s['course']
        if sch_course != 'All' and course:
            if sch_course.lower() not in course.lower() and course.lower() not in sch_course.lower():
                eligible = False
            else:
                reasons.append(f"✅ Available for {course} students")

        if not (s['min_year'] <= year <= s['max_year']):
            eligible = False

        if eligible:
            matches.append({
                'id': s['id'],
                'name': s['name'],
                'provider': s['provider'],
                'amount': s['amount'],
                'deadline': s['deadline'],
                'link': s['link'],
                'description': s['description'],
                'documents_required': s['documents_required'],
                'reasons': reasons
            })

    return matches
