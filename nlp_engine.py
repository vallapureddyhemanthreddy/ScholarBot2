"""
nlp_engine.py  —  Advanced offline NLP for ScholarBot
Zero external dependencies. Pure Python pattern matching with
context awareness, Hinglish support, and multi-field extraction.
"""
import re

# ══════════════════════════════════════════════════════
#  INTENT DETECTION
# ══════════════════════════════════════════════════════

INTENT_PATTERNS = {
    "greeting": [
        r"\b(hi|hello|hey|hola|namaste|namaskar|sup|yo|howdy)\b",
        r"^(good\s*(morning|evening|afternoon|night))$",
        r"^(start|begin|let'?s\s*start|let'?s\s*go|get started)$",
        r"^(hii+|helloo+|heyy+)$",
    ],
    "restart": [
        r"\b(restart|start over|reset|new chat|begin again|start again|fresh start|clear|wipe)\b",
        r"\b(naya|dobara|phir se)\b.*\b(shuru|start)\b",
        r"\b(start|shuru)\b.*\b(again|over|naye|fresh)\b",
    ],
    "show_results": [
        r"\b(show|find|get|give|tell|search).{0,25}\b(scholarship|result|match|eligible)\b",
        r"\bmy\s+scholarships?\b",
        r"\bscholarships?\b.{0,25}\b(show|find|get|for me|mujhe|mere liye)\b",
        r"\b(kaunsi|kaun si|which).{0,20}\b(scholarship|yojana|scheme)\b",
        r"\b(scholarship|yojana).{0,20}\b(milegi|mil sakti|eligible|qualify)\b",
        r"\b(what).{0,20}(i (can|could) get|eligible for|qualify for)\b",
        r"\b(mujhe|mere liye).{0,20}\b(scholarship|yojana)\b",
        r"\b(my\s+)?(results?|matches?)\b",
        r"\bscholarships?\s+(for me|available|list)\b",
    ],
    "skip": [
        r"^(skip|n/?a|none|not sure|don'?t know|nahi pata|pata nahi|no idea|idk|dk|pass)$",
        r"\b(skip (this|it)|not applicable|doesn'?t apply)\b",
    ],
    "help": [
        r"\b(help|assist|guide|support|confused|samajh nahi|kya karna)\b",
        r"\b(how does this work|what can you do|what do i do)\b",
    ],
    "faq_docs": [
        r"\b(documents?|docs?|papers?|certificates?|kya kya chahiye)\b",
        r"\b(kaun\s*se|kya\s*kya).{0,20}\b(document|paper|certificate|chahiye)\b",
        r"\b(what.{0,20}(need|require|bring|submit|upload))\b",
        r"\bwhat\s+\w+\s+(needed|required|necessary)\b",
    ],
    "faq_apply": [
        r"\b(how to apply|apply kaise|application process|kaise apply|register kaise)\b",
        r"\b(apply.{0,15}(scholarship|nsp|portal|online))\b",
        r"\b(nsp.{0,20}(kya hai|what is|use kaise|register))\b",
        r"\b(national scholarship portal)\b",
    ],
    "faq_eligibility": [
        r"\b(eligib|qualify|criteria|requirement|kaun apply|who can apply)\b",
        r"\b(kya main|am i|can i).{0,20}\b(eligible|apply|qualify|get)\b",
    ],
    "faq_income_limit": [
        r"\b(income limit|income criteria|kitni income|maximum income|salary limit)\b",
        r"\b(ews|obc|sc|st|general).{0,20}(income|salary|limit|kitna)\b",
        r"\b(income.{0,20}(ews|obc|sc|st))\b",
    ],
    "faq_nsp": [
        r"\b(nsp|national scholarship portal)\b",
        r"\b(scholarships?\.gov\.in)\b",
    ],
    "faq_cgpa": [
        r"\b(cgpa|gpa).{0,20}(percent|convert|calculate|kaise)\b",
        r"\b(percent.{0,20}(cgpa|gpa))\b",
        r"\b(cgpa to percent|percent to gpa)\b",
    ],
    "faq_state_portal": [
        r"\b(state portal|state scholarship|rajya|state.{0,10}website)\b",
        r"\b(telangana|maharashtra|karnataka|mp|up|rajasthan).{0,20}(scholarship|portal|website|scheme)\b",
    ],
    "update_field": [
        r"\b(actually|correction|no wait|wait|i mean|i meant|sorry|oops|mistake|wrong|galat)\b",
        r"\b(change|update|correct|edit).{0,20}\b(gpa|income|category|gender|state|course|year|marks)\b",
        r"\b(my (gpa|income|marks|category|state|course|year) is)\b",
    ],
    "provide_info": [],  # fallback
}

def detect_intent(message: str) -> str:
    msg = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        if intent == "provide_info":
            continue
        for pat in patterns:
            if re.search(pat, msg):
                return intent
    return "provide_info"


# ══════════════════════════════════════════════════════
#  FIELD EXTRACTORS
# ══════════════════════════════════════════════════════

def extract_gpa(text: str, is_expected: bool = False):
    """Extract GPA/percentage from any natural language."""
    t = text.lower().strip()

    # If the message is clearly about income only, don't try to extract GPA
    income_only = re.search(
        r'\b(income|salary|earning|lakh|lac|rupee|rs\.?|inr|k\s*/\s*month|per month|bpl)\b', t
    ) and not re.search(r'\b(marks?|score|scored|gpa|cgpa|percent|%|grade|result|secured|obtained|aggregate)\b', t)
    if income_only and not is_expected:
        return None

    # "scored 85 percent" / "85%" / "85 per cent"
    m = re.search(r'(\d{1,3}(?:\.\d+)?)\s*(?:%|percent(?:age)?|per\s*cent)', t)
    if m:
        val = float(m.group(1))
        if 0 < val <= 100:
            return round(val / 10, 2)

    # "8.5/10" or "85/100"
    m = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(10|100)', t)
    if m:
        num, denom = float(m.group(1)), float(m.group(2))
        if denom == 10 and 0 < num <= 10:
            return round(num, 2)
        if denom == 100 and 0 < num <= 100:
            return round(num / 10, 2)

    # "9 CGPA" / "CGPA 8.5" / "CGPA is 7"
    m = re.search(r'(?:cgpa|gpa)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)', t)
    if not m:
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:cgpa|gpa)', t)
    if m:
        val = float(m.group(1))
        if 0 < val <= 10:
            return round(val, 2)

    # Hinglish: "mere marks 85 hain" / "75 marks aaye"
    m = re.search(r'(?:marks?|score|scored)\s*(?:are|is|hain|hai|=)?\s*(\d{2,3}(?:\.\d+)?)', t)
    if not m:
        m = re.search(r'(\d{2,3}(?:\.\d+)?)\s*(?:marks?|score)', t)
    if m:
        val = float(m.group(1))
        if 0 < val <= 100:
            return round(val / 10, 2)
        if 0 < val <= 10:
            return round(val, 2)

    # Plain number ONLY if explicit academic keywords are present or if it's expected
    is_short_answer = len(t.split()) <= 5
    has_academic_context = (is_expected and is_short_answer) or re.search(
        r'\b(marks?|score|gpa|cgpa|percent|grade|result|got|scored|secured|aggregate|obtained)\b', t
    )
    if has_academic_context:
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', t)
        for n in numbers:
            val = float(n)
            # Skip numbers that look like income (4+ digits) or years (1900-2099)
            if val > 100 or (1900 <= val <= 2099):
                continue
            if 0 < val <= 10:
                return round(val, 2)
            if 10 < val <= 100:
                return round(val / 10, 2)

    return None


def extract_income(text: str, is_expected: bool = False):
    """Extract annual income in rupees from any phrasing."""
    t = text.lower().strip()

    # Monthly salary → annual: "20k/month", "20000 per month", "salary 25k monthly"
    monthly_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:k|thousand)?\s*/?\s*(?:per\s*)?month(?:ly)?',
        r'(?:monthly|per month|mahine|mahina|mahina ka|maheene)\D{0,10}(\d+(?:\.\d+)?)\s*(?:k|thousand)?',
        r'(\d+(?:\.\d+)?)\s*(?:k|thousand)\s*(?:per\s*)?month',
        r'salary\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*(?:k|thousand)?',
    ]
    for pat in monthly_patterns:
        m = re.search(pat, t)
        if m:
            val = float(m.group(1) if m.lastindex and m.group(1) else m.group(0))
            # re-extract number
            nums = re.findall(r'\d+(?:\.\d+)?', m.group(0))
            if nums:
                val = float(nums[0])
                if val < 500:   val *= 1000   # "20k" → 20000
                return int(val * 12)

    # "BPL" / "below poverty line"
    if re.search(r'\b(bpl|below poverty|garib|very poor|bahut garib)\b', t):
        return 60000  # ~5000/month

    # "no income" / "unemployed"
    if re.search(r'\b(no income|zero income|unemployed|nahi hai income|income nahi)\b', t):
        return 0

    # Lakh patterns: "3 lakh", "2.5L", "3,00,000", "3 lac"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|l\b)', t)
    if m:
        return int(float(m.group(1)) * 100000)

    # Crore (rare but handle): "0.5 crore"
    m = re.search(r'(\d+(?:\.\d+)?)\s*crore', t)
    if m:
        return int(float(m.group(1)) * 10000000)

    # Thousand: "50 thousand", "50k"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:thousand|k)\b', t)
    if m:
        return int(float(m.group(1)) * 1000)

    # Plain large number (6-7 digits) → direct rupees
    m = re.search(r'\b(\d{4,7})\b', t)
    if m:
        val = int(m.group(1))
        if val >= 1000:
            return val

    # Small number heuristic (1–50 = lakhs) ONLY if income keywords are present or if it's expected
    is_short_answer = len(t.split()) <= 5
    has_income_context = (is_expected and is_short_answer) or re.search(
        r'\b(income|salary|earn|earning|rupee|rs\.?|inr|lakh|lac|per\s*month|monthly|annual|family|ghar|gharwale|papa|mummy|parents?|below|under|above|around|approx)\b', t
    )
    if has_income_context:
        m = re.search(r'\b(\d{1,2}(?:\.\d+)?)\b', t)
        if m:
            val = float(m.group(1))
            if 1 <= val <= 50:
                return int(val * 100000)

    return None


CATEGORY_MAP = {
    # SC
    r'\b(sc|s\.c|scheduled\s*caste|dalit|harijan)\b': 'SC',
    # ST
    r'\b(st|s\.t|scheduled\s*tribe|tribal|adivasi|aadivasi)\b': 'ST',
    # OBC
    r'\b(obc|o\.b\.c|other backward|backward class|obc-ncl|obc ncl)\b': 'OBC',
    # EWS
    r'\b(ews|e\.w\.s|economically weaker|weaker section)\b': 'EWS',
    # General
    r'\b(general|gen|open|unreserved|forward caste|fc|no reservation|open category)\b': 'General',
}

def extract_category(text: str):
    t = text.lower()
    for pat, val in CATEGORY_MAP.items():
        if re.search(pat, t):
            return val
    return None


GENDER_MAP = {
    r'\b(female|woman|women|girl|lady|ladies|ladki|mahila|f)\b': 'Female',
    r'\b(male|man|men|boy|gents|ladka|purush|m)\b': 'Male',
    r'\b(other|non.?binary|transgender|third gender|lgbtq|prefer not)\b': 'Other',
}

def extract_gender(text: str):
    t = text.lower()
    for pat, val in GENDER_MAP.items():
        if re.search(pat, t):
            return val
    return None


STATES = {
    # Full names
    "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh", "hp": "Himachal Pradesh",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh",
    "maharashtra": "Maharashtra", "mh": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha", "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "tn": "Tamil Nadu",
    "telangana": "Telangana", "ts": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand", "uk": "Uttarakhand",
    "west bengal": "West Bengal", "wb": "West Bengal",
    # UTs
    "delhi": "Delhi", "new delhi": "Delhi",
    "jammu and kashmir": "Jammu and Kashmir", "j&k": "Jammu and Kashmir", "jk": "Jammu and Kashmir",
    "ladakh": "Ladakh",
    "chandigarh": "Chandigarh",
    "puducherry": "Puducherry", "pondicherry": "Puducherry",
    "andaman": "Andaman and Nicobar",
    "lakshadweep": "Lakshadweep",
    "dadra": "Dadra and Nagar Haveli",
    # Cities that imply a state
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "bangalore": "Karnataka", "bengaluru": "Karnataka", "mysore": "Karnataka",
    "hyderabad": "Telangana",
    "chennai": "Tamil Nadu",
    "kolkata": "West Bengal",
    "jaipur": "Rajasthan",
    "lucknow": "Uttar Pradesh", "varanasi": "Uttar Pradesh", "kanpur": "Uttar Pradesh",
    "patna": "Bihar",
    "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh",
    "ahmedabad": "Gujarat", "surat": "Gujarat",
    "chandigarh city": "Punjab",
    "dehradun": "Uttarakhand",
    "bhubaneswar": "Odisha",
    "ranchi": "Jharkhand",
    "raipur": "Chhattisgarh",
    "guwahati": "Assam",
    "thiruvananthapuram": "Kerala", "kochi": "Kerala", "kozhikode": "Kerala",
    "visakhapatnam": "Andhra Pradesh", "vijayawada": "Andhra Pradesh",
}

def extract_state(text: str):
    t = text.lower().strip()
    # Try longest match first
    for key in sorted(STATES.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(key) + r'\b', t):
            return STATES[key]
    return None


COURSES = {
    r'\b(b\.?tech|btech|b\.?e\.?|be\b|bachelor of (technology|engineering))\b': 'B.Tech',
    r'\b(mbbs|bachelor of medicine|medical|medicine)\b': 'MBBS',
    r'\b(bds|dental)\b': 'BDS',
    r'\b(b\.?sc\.?|bsc|bachelor of science)\b': 'B.Sc',
    r'\b(b\.?com\.?|bcom|bachelor of commerce)\b': 'B.Com',
    r'\b(b\.?a\.?|ba\b|bachelor of arts|humanities)\b': 'BA',
    r'\b(bca|bachelor of computer application)\b': 'BCA',
    r'\b(mca|master of computer)\b': 'MCA',
    r'\b(m\.?tech|mtech|master of technology)\b': 'M.Tech',
    r'\b(mba|master of business)\b': 'MBA',
    r'\b(m\.?sc\.?|msc|master of science)\b': 'M.Sc',
    r'\b(phd|ph\.?d|doctorate|research degree)\b': 'PhD',
    r'\b(llb|l\.?l\.?b|law degree|bachelor of law)\b': 'LLB',
    r'\b(diploma|polytechnic|poly)\b': 'Diploma',
    r'\b(nursing|b\.?sc nursing|gnm)\b': 'B.Sc Nursing',
    r'\b(pharmacy|b\.?pharm|d\.?pharm)\b': 'B.Pharm',
    r'\b(architecture|b\.?arch)\b': 'B.Arch',
    r'\b(mass comm|journalism|bmc|bmm)\b': 'Mass Communication',
    r'\b(hotel management|bhmct|hospitality)\b': 'Hotel Management',
    r'\b(agriculture|b\.?sc agri)\b': 'B.Sc Agriculture',
}

def extract_course(text: str):
    t = text.lower().strip()
    for pat, val in COURSES.items():
        if re.search(pat, t):
            return val
    # Detect "engineering" generically
    if re.search(r'\b(engineering|engg|engineer)\b', t):
        return 'B.Tech'
    return None


YEAR_MAP = {
    r'(?<![\.\d])\b(1st|first|ek|1)\b(?![\.\d])\s*(year|yr|semester)?\b': 1,
    r'(?<![\.\d])\b(2nd|second|dusra|doosra|2)\b(?![\.\d])\s*(year|yr|semester)?\b': 2,
    r'(?<![\.\d])\b(3rd|third|teesra|3)\b(?![\.\d])\s*(year|yr|semester)?\b': 3,
    r'(?<![\.\d])\b(4th|fourth|chautha|4)\b(?![\.\d])\s*(year|yr|semester)?\b': 4,
    r'(?<![\.\d])\b(5th|fifth|paanchwa|5)\b(?![\.\d])\s*(year|yr|semester)?\b': 5,
    r'\b(final|last)\s*(year|yr)\b': 4,
    r'\bfresher\b': 1,
    r'\bjunior\b': 2,
    r'\bsenior\b': 3,
}

def extract_year(text: str):
    t = text.lower().strip()
    for pat, val in YEAR_MAP.items():
        if re.search(pat, t):
            return val
    # semester → year
    m = re.search(r'\b([1-8])\s*(st|nd|rd|th)?\s*sem\b', t)
    if m:
        sem = int(m.group(1))
        return max(1, (sem + 1) // 2)
    return None


# ══════════════════════════════════════════════════════
#  MULTI-FIELD EXTRACTION (one-shot parsing)
# ══════════════════════════════════════════════════════

def extract_all_fields(text: str, expected_field: str = None) -> dict:
    """Try to extract ALL fields from a single message at once, taking context into account."""
    result = {}
    gpa = extract_gpa(text, is_expected=(expected_field == 'gpa'))
    if gpa is not None:           result['gpa'] = gpa
    inc = extract_income(text, is_expected=(expected_field == 'income'))
    if inc is not None:           result['income'] = inc
    cat = extract_category(text)
    if cat:                       result['category'] = cat
    gen = extract_gender(text)
    if gen:                       result['gender'] = gen
    st  = extract_state(text)
    if st:                        result['state'] = st
    crs = extract_course(text)
    if crs:                       result['course'] = crs
    yr  = extract_year(text)
    if yr is not None:            result['year'] = yr
    return result


# ══════════════════════════════════════════════════════
#  CORRECTION / UPDATE DETECTION
# ══════════════════════════════════════════════════════

CORRECTION_PATTERNS = {
    'gpa':      r'\b(gpa|marks?|percentage|score|cgpa)\s*(is|are|was|=|:)?\s*',
    'income':   r'\b(income|salary|earning)\s*(is|are|was|=|:)?\s*',
    'category': r'\b(category|caste|reservation)\s*(is|are|=|:)?\s*',
    'gender':   r'\b(gender|i am a?|i\'?m a?)\s*',
    'state':    r'\b(state|from|domicile|living in|i live in|main)\s*(is|are|=|:)?\s*',
    'course':   r'\b(course|studying|doing|pursuing)\s*(is|are|=|:)?\s*',
    'year':     r'\b(year|yr|currently in|i am in)\s*(is|are|=|:)?\s*',
}

def detect_correction(text: str, expected_field: str = None) -> dict:
    """Detect if user is correcting a field mid-conversation."""
    t = text.lower()
    if not re.search(r'\b(actually|correction|i mean|meant|sorry|oops|wait|no no|change|update|my .* is)\b', t):
        return {}
    return extract_all_fields(text, expected_field)


# ══════════════════════════════════════════════════════
#  SMART BOT RESPONSES
# ══════════════════════════════════════════════════════

QUESTIONS = {
    'gpa':      "📚 What's your **GPA or percentage**?\n*(e.g., 8.5 CGPA, or 75%, or just say '75 marks')*",
    'income':   "💰 What's your **family's annual income**?\n*(e.g., 3 lakh, 2.5L, 30k/month, or BPL card holder)*",
    'category': "📋 What's your **reservation category**?\n*(General / OBC / SC / ST / EWS)*",
    'gender':   "👤 What's your **gender**?\n*(Male / Female / Other)*",
    'state':    "🗺️ Which **state** are you from?\n*(e.g., Maharashtra, Tamil Nadu, UP — or your city name works too!)*",
    'course':   "🎓 What **course** are you currently pursuing?\n*(e.g., B.Tech, MBBS, B.Sc, Diploma — type 'skip' if not sure)*",
    'year':     "📅 Which **year of study** are you in?\n*(1st year / 2nd year / final year / fresher)*",
}

CONFIRMATIONS = {
    'gpa':      lambda v: f"✅ Got it — **{v}/10 GPA**",
    'income':   lambda v: f"✅ Family income: **₹{v/100000:.1f}L/year**",
    'category': lambda v: f"✅ Category: **{v}**",
    'gender':   lambda v: f"✅ Gender: **{v}**",
    'state':    lambda v: f"✅ State: **{v}**",
    'course':   lambda v: f"✅ Course: **{v}**",
    'year':     lambda v: f"✅ Year: **Year {int(v)}**",
}

HINTS = {
    'gpa':      "I couldn't read your marks. Try: **8.5**, **75%**, or **9 CGPA**",
    'income':   "Try: **3 lakh**, **2.5L**, **30,000/month**, or **BPL**",
    'category': "Please type: **General**, **OBC**, **SC**, **ST**, or **EWS**",
    'gender':   "Please type: **Male**, **Female**, or **Other**",
    'state':    "Please type your state name, e.g., **Maharashtra**, **Tamil Nadu**, **Delhi**",
    'course':   "Please type your course, e.g., **B.Tech**, **MBBS**, **BA**. Or type **skip**.",
    'year':     "Please type your year: **1st**, **2nd**, **3rd**, **4th**, or **final year**",
}

# ══════════════════════════════════════════════════════
#  FAQ KNOWLEDGE BASE
# ══════════════════════════════════════════════════════

FAQ = {
    "faq_docs": """📄 **Documents Usually Required for Scholarships:**

• **Academic:** 10th & 12th mark sheets, current semester marksheet/bonafide letter
• **Income proof:** Income certificate issued by Tehsildar/SDM/Revenue officer
• **Category proof:** Caste certificate (SC/ST/OBC/EWS) from competent authority
• **Domicile:** State residence/domicile certificate
• **Identity:** Aadhaar card (mandatory for NSP)
• **Bank details:** Passbook copy or cancelled cheque (account in your own name)
• **College proof:** Enrollment/admission letter, fee receipt
• **Photos:** 2–4 recent passport-size photographs

💡 *Pro tip: Make self-attested photocopies of all documents and keep digital scans ready in PDF format.*""",

    "faq_apply": """🌐 **How to Apply — Step by Step:**

**Step 1:** Go to [scholarships.gov.in](https://scholarships.gov.in) (National Scholarship Portal)
**Step 2:** Click **"New Registration"** → verify your Aadhaar & mobile OTP
**Step 3:** Fill in your academic, personal, and bank details
**Step 4:** Browse **"Schemes"** → select eligible schemes → apply
**Step 5:** Upload scanned documents (PDF/JPG, usually under 200KB each)
**Step 6:** Submit → note your **Application ID**
**Step 7:** Track status under "Check Your Status"

⚠️ *Apply before October 31 for most central government schemes*
💡 *Your institute must verify your application on the portal for it to be processed*""",

    "faq_eligibility": """✅ **General Eligibility Criteria:**

| Factor | Typical Range |
|--------|--------------|
| Academic | 50%–80% depending on scheme |
| Family Income | ₹1L – ₹8L per year |
| Category | All, with extra benefits for SC/ST/OBC/EWS |
| Age | Usually 17–35 years |
| Course | Most UG/PG courses covered |

📌 *Each scholarship has its own specific criteria — I match these exactly against your profile!*
🔍 *Share your details and I'll tell you exactly what you qualify for.*""",

    "faq_income_limit": """💰 **Income Limits by Category:**

• **SC/ST Post-Matric (Central):** ₹2.5 lakh/year
• **OBC Post-Matric (Central):** ₹1 lakh/year
• **EWS (general definition):** ₹8 lakh/year
• **Central Sector Scholarship:** ₹8 lakh/year
• **AICTE Pragati (Girls):** ₹8 lakh/year
• **Maulana Azad Fellowship:** ₹6 lakh/year
• **State scholarships:** Vary — usually ₹1L–₹3.5L/year
• **Corporate scholarships:** Often ₹2.5L–₹6L/year

💡 *Income certificate must be for the current financial year*""",

    "faq_nsp": """🌐 **National Scholarship Portal (NSP) — scholarships.gov.in**

NSP is India's **one-stop portal** for all central government scholarships.

**What's on NSP:**
• Pre-matric & post-matric scholarships for SC/ST/OBC/Minority
• Central Sector Scheme (merit-based)
• Inspire Scholarships (Science)
• AICTE schemes (Pragati, Saksham)
• Top Class Education Scheme
• PM Scholarship (Ex-servicemen wards)

**Key dates:** Applications typically open **August–October** each year.
**Required:** Aadhaar number, bank account linked to Aadhaar, college AISHE code.

📱 *You can also download the NSP mobile app from Google Play Store.*""",

    "faq_cgpa": """📊 **CGPA ↔ Percentage Conversion:**

**CGPA to Percentage:**
• **CBSE formula:** CGPA × 9.5 = Percentage
  *Example: 8.5 CGPA × 9.5 = **80.75%***

• **10-point scale (most colleges):** CGPA × 10 = Percentage
  *Example: 8.5 × 10 = **85%***

**Percentage to CGPA:**
• Percentage ÷ 9.5 = CGPA (CBSE)
  *Example: 75% ÷ 9.5 = **7.89 CGPA***

💡 *For scholarships, just tell me your CGPA or % directly — I'll handle the conversion!*""",

    "faq_state_portal": """🗺️ **State Scholarship Portals:**

| State | Portal |
|-------|--------|
| **Telangana** | telanganaepass.cgg.gov.in |
| **Maharashtra** | mahadbt.maharashtra.gov.in |
| **Karnataka** | karepass.cgg.gov.in |
| **Uttar Pradesh** | scholarship.up.gov.in |
| **Madhya Pradesh** | scholarshipportal.mp.nic.in |
| **Rajasthan** | hte.rajasthan.gov.in |
| **Punjab** | scholarships.punjab.gov.in |
| **West Bengal** | svmcm.wbhed.gov.in |
| **Bihar** | pmsonline.bih.nic.in |
| **Tamil Nadu** | tn.gov.in (Empower scheme) |

💡 *Always apply on BOTH NSP (central) AND your state portal to maximize your chances!*""",

    "help": """🤖 **What I can do for you:**

• 🎓 **Find your scholarships** — Tell me your details, I'll match you with eligible schemes
• 📄 **Documents info** — "What documents do I need?"
• 🌐 **Apply guide** — "How to apply on NSP?"
• 💰 **Income limits** — "What's the income limit for OBC?"
• 📊 **CGPA conversion** — "How to convert CGPA to percentage?"
• 🗺️ **State portals** — "Maharashtra scholarship website?"
• ✅ **Eligibility check** — "Can I apply as a General category student?"

**To find YOUR scholarships, just tell me:**
Your GPA/marks, income, category, gender, state, course & year — all in one message or one by one!""",
}

def get_faq_response(intent: str) -> str:
    return FAQ.get(intent, FAQ.get("help", "I'm not sure about that. Try asking about documents, eligibility, or how to apply!"))
