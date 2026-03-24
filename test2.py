import sys
sys.path.append('/home/hemanthxd/Downloads/scholarship_assistant_v3_offline/scholarship_app')
from nlp_engine import extract_all_fields, extract_gpa
import re

t = "i am male student studying 2nd year b tech in cvcr college of engineering in telangana my family income is below 2 lakhs"
is_expected = True

is_short_answer = len(t.split()) <= 5
has_academic_context = (is_expected and is_short_answer) or re.search(
    r'\b(marks?|score|gpa|cgpa|percent|grade|result|got|scored|secured|aggregate|obtained)\b', t
)

print("is_short_answer:", is_short_answer)
print("has_academic_context:", bool(has_academic_context))

res = extract_gpa(t, is_expected=True)
print("extract_gpa:", res)

res_all = extract_all_fields(t, expected_field="gpa")
print("extract_all_fields:", res_all)
