from flask import Flask, request, jsonify, render_template, session
from nlp_engine import (
    detect_intent, extract_all_fields, detect_correction,
    QUESTIONS, CONFIRMATIONS, HINTS, get_faq_response, FAQ
)
from database import (
    init_db, match_scholarships, create_user, get_user, update_user_profile, get_user_profile
)
import os
import socket

app = Flask(__name__)
app.secret_key = 'scholarbot-secret-2025-xk9'

STEPS = ['gpa', 'income', 'category', 'gender', 'state', 'course', 'year', 'college']

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════

def get_profile():
    return session.get('profile', {})

def next_missing(profile):
    for i, step in enumerate(STEPS):
        if step not in profile or profile[step] is None:
            return i, step
    return len(STEPS), None

def all_done(profile):
    return all(profile.get(s) is not None for s in STEPS)

def format_profile_summary(profile):
    LABELS = {
        'gpa':      ('📚', 'GPA',           lambda v: f"{float(v):.1f}/10"),
        'income':   ('💰', 'Family Income',  lambda v: f"₹{float(v)/100000:.1f}L/year"),
        'category': ('📋', 'Category',       str),
        'gender':   ('👤', 'Gender',         str),
        'state':    ('🗺️', 'State',          str),
        'course':   ('🎓', 'Course',         str),
        'year':     ('📅', 'Year',           lambda v: f"Year {int(v)}"),
        'college':  ('🏛️', 'College',        str),
    }
    return "\n".join(
        f"{icon} **{label}:** {fmt(profile[key])}"
        for key, (icon, label, fmt) in LABELS.items()
        if key in profile and profile[key] is not None
    )

def build_results(profile):
    matches = match_scholarships(profile)
    summary = format_profile_summary(profile)
    count = len(matches)
    if count:
        msg = (
            f"**Your Profile:**\n{summary}\n\n"
            f"🎉 You're eligible for **{count} scholarship{'s' if count > 1 else ''}**! "
            f"Here are your personalized matches:"
        )
    else:
        msg = (
            f"**Your Profile:**\n{summary}\n\n"
            f"😔 No exact matches found right now — but don't give up!\n\n"
            f"**Try these:**\n"
            f"• [scholarships.gov.in](https://scholarships.gov.in) — NSP (central schemes)\n"
            f"• Your state's scholarship portal\n"
            f"• [vidyasaarathi.co.in](https://www.vidyasaarathi.co.in) — corporate scholarships\n\n"
            f"Type **restart** to search again with updated details."
        )
    return msg, matches


# ══════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    print(f"[SIGNUP DEBUG] Request for user: '{username}'")
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if create_user(username, password):
        print(f"[SIGNUP DEBUG] Success for: '{username}'")
        session['user'] = username
        # Merge existing session profile into the new user's DB record
        current_profile = get_profile()
        if current_profile:
            update_user_profile(username, current_profile)
        return jsonify({'status': 'ok', 'user': username, 'profile': current_profile})
    else:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    user = get_user(username, password)
    if user:
        session['user'] = username
        # Load user's saved profile into session
        db_profile = get_user_profile(username)
        # We could merge with current session, but loading from DB takes precedence
        session['profile'] = db_profile
        return jsonify({'status': 'ok', 'user': username, 'profile': db_profile})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('profile', None)
    return jsonify({'status': 'ok'})

@app.route('/api/user', methods=['GET'])
def get_user_status():
    return jsonify({'user': session.get('user')})

@app.route('/api/chat', methods=['POST'])
def chat():
    data   = request.json or {}
    msg    = data.get('message', '').strip()
    if not msg:
        return jsonify({'reply': "Say something! I'm here to help 🎓"})

    profile       = get_profile()
    results_shown = session.get('results_shown', False)
    intent        = detect_intent(msg)

    # ── RESTART ──────────────────────────────────────
    if intent == 'restart':
        session.clear()
        return jsonify({
            'reply': f"🔄 **Starting fresh!**\n\nHi! I'm ScholarBot 🎓 Let's find scholarships that fit you perfectly.\n\n{QUESTIONS['gpa']}",
            'step': 1, 'total_steps': 7, 'reset': True,
            'collected_fields': []
        })

    # ── GREETING ─────────────────────────────────────
    if intent == 'greeting':
        session.clear()
        return jsonify({
            'reply': (
                "👋 **Hello! Welcome to ScholarBot!**\n\n"
                "I'll help you discover scholarships you're eligible for — no forms, just chat naturally!\n\n"
                "You can tell me everything in one go, like:\n"
                "*\"I'm a female SC student doing B.Tech 2nd year in Maharashtra, GPA 7.5, income 2 lakh\"*\n\n"
                "Or answer one question at a time 👇\n\n" + QUESTIONS['gpa']
            ),
            'step': 1, 'total_steps': 7, 'reset': True,
            'collected_fields': []
        })

    # ── LIST SCHOLARSHIPS ────────────────────────────
    if intent == 'list_scholarships':
        from database import get_all_scholarships_summary
        all_scholars = get_all_scholarships_summary()
        reply = f"🎓 **Here are all {len(all_scholars)} scholarships in my database:**\n\n"
        for s in all_scholars:
            reply += f"• **{s['name']}**\n"
        reply += "\n💡 *Tell me your GPA, income, and category, and I'll find which ones match YOU!*"
        
        step_idx, _ = next_missing(profile)
        return jsonify({
            'reply': reply,
            'step': step_idx, 'total_steps': 7,
            'collected_fields': list(profile.keys())
        })

    # ── FAQ INTENTS ───────────────────────────────────
    if intent in FAQ:
        step_idx, _ = next_missing(profile)
        return jsonify({
            'reply': get_faq_response(intent),
            'step': step_idx,
            'total_steps': 7,
            'collected_fields': list(profile.keys())
        })

    # ── SHOW RESULTS (manual trigger) ────────────────
    if intent == 'show_results':
        if all_done(profile):
            if not results_shown:
                session['results_shown'] = True
                reply, scholarships = build_results(profile)
                return jsonify({
                    'reply': reply, 'scholarships': scholarships,
                    'show_results': True, 'step': 7, 'total_steps': 7,
                    'collected_fields': list(profile.keys())
                })
            else:
                return jsonify({
                    'reply': "You've already seen your results above! 👆 Type **restart** to search again with different details.",
                    'step': 7, 'total_steps': 7,
                    'collected_fields': list(profile.keys())
                })
        else:
            step_idx, next_field = next_missing(profile)
            return jsonify({
                'reply': f"Almost there! I just need a few more details.\n\n{QUESTIONS[next_field]}",
                'step': step_idx + 1, 'total_steps': 7,
                'collected_fields': list(profile.keys())
            })

    # ── HELP ─────────────────────────────────────────
    if intent == 'help':
        return jsonify({
            'reply': get_faq_response('help'),
            'collected_fields': list(profile.keys())
        })

    # ── CORRECTION DETECTION ─────────────────────────
    # Get the currently expected field to provide context to the NLP engine
    _, expected_field = next_missing(profile)

    correction = detect_correction(msg, expected_field=expected_field)
    if correction:
        profile.update(correction)
        session['profile'] = profile
        if 'user' in session:
            update_user_profile(session['user'], profile)

        corrected = ", ".join(f"**{k}**" for k in correction.keys())
        step_idx, next_field = next_missing(profile)
        if next_field:
            return jsonify({
                'reply': f"✏️ Updated {corrected}!\n\n{QUESTIONS[next_field]}",
                'step': step_idx + 1, 'total_steps': 7,
                'collected_fields': list(profile.keys())
            })

    # ── MULTI-FIELD EXTRACTION ────────────────────────
    extracted = extract_all_fields(msg, expected_field=expected_field)

    if extracted:
        profile.update(extracted)
        session['profile'] = profile
        if 'user' in session:
            update_user_profile(session['user'], profile)

        # Build confirmation for newly extracted fields
        confirms = []
        for field, val in extracted.items():
            confirms.append(CONFIRMATIONS[field](val))

        confirm_str = " • ".join(confirms) if confirms else ""

        # Check if now complete
        if all_done(profile) and not results_shown:
            session['results_shown'] = True
            reply, scholarships = build_results(profile)
            if confirm_str:
                reply = confirm_str + "\n\n" + reply
            return jsonify({
                'reply': reply, 'scholarships': scholarships,
                'show_results': True, 'step': 7, 'total_steps': 7,
                'collected_fields': list(profile.keys())
            })

        # Ask next missing field
        step_idx, next_field = next_missing(profile)
        if next_field:
            prefix = confirm_str + "\n\n" if confirm_str else ""
            return jsonify({
                'reply': prefix + QUESTIONS[next_field],
                'step': step_idx + 1, 'total_steps': 7,
                'collected_fields': list(profile.keys())
            })

    # ── SINGLE FIELD — SKIP ───────────────────────────
    if intent == 'skip':
        step_idx, current_field = next_missing(profile)
        if current_field in ('state', 'course', 'college'):
            profile[current_field] = 'All'
            session['profile'] = profile
            if 'user' in session:
                update_user_profile(session['user'], profile)

            step_idx, next_field = next_missing(profile)
            if next_field:
                return jsonify({
                    'reply': f"👍 Skipped! No worries.\n\n{QUESTIONS[next_field]}",
                    'step': step_idx + 1, 'total_steps': 7,
                    'collected_fields': list(profile.keys())
                })
            elif all_done(profile) and not results_shown:
                session['results_shown'] = True
                reply, scholarships = build_results(profile)
                return jsonify({
                    'reply': reply, 'scholarships': scholarships,
                    'show_results': True, 'step': 7, 'total_steps': 7,
                    'collected_fields': list(profile.keys())
                })

    # ── COULDN'T EXTRACT — RE-ASK ─────────────────────
    step_idx, current_field = next_missing(profile)
    if current_field:
        # If profile is empty and no extraction, probably a general question → be helpful
        if not profile and not extracted:
            return jsonify({
                'reply': (
                    "I'm ScholarBot — I help you find Indian scholarships! 🎓\n\n"
                    "Just tell me about yourself and I'll find matching schemes.\n"
                    "You can say something like:\n"
                    "*\"I'm SC category, 75%, income 2 lakh, Maharashtra, B.Tech 2nd year\"*\n\n"
                    "Or start with: " + QUESTIONS['gpa']
                ),
                'step': 1, 'total_steps': 7,
                'collected_fields': []
            })

        return jsonify({
            'reply': f"🤔 {HINTS[current_field]}\n\n{QUESTIONS[current_field]}",
            'step': step_idx + 1, 'total_steps': 7,
            'collected_fields': list(profile.keys())
        })

    # ── ALL DONE, POST-RESULT CHAT ─────────────────────
    return jsonify({
        'reply': (
            "✅ Your profile is complete! I've already found your matches above. 👆\n\n"
            "You can ask me anything else:\n"
            "• *\"What documents do I need?\"*\n"
            "• *\"How to apply on NSP?\"*\n"
            "• *\"What's the income limit?\"*\n\n"
            "Or type **restart** to search with new details."
        ),
        'step': 7, 'total_steps': 7,
        'collected_fields': list(profile.keys())
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'status': 'ok'})


@app.route('/api/profile', methods=['GET'])
def get_profile_route():
    return jsonify(session.get('profile', {}))


# ══════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════

def find_free_port(start=5001, end=5020):
    # Hardcoded to 5010 to avoid conflict with Flask's auto-reloader
    return 5010


if __name__ == '__main__':
    init_db()
    port = find_free_port()
    print("=" * 45)
    print("  🎓  ScholarBot — AI Scholarship Assistant")
    print("=" * 45)
    print(f"  ✅  Database ready  (15 scholarships)")
    print(f"  🚀  Running at:  http://localhost:{port}")
    print(f"  💡  No API key needed — fully offline!")
    print("=" * 45)
    app.run(debug=True, port=port, host='0.0.0.0')
