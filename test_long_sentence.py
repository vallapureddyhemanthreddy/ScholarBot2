import sys
sys.path.append('/home/hemanthxd/Downloads/scholarship_assistant_v3_offline/scholarship_app')

from nlp_engine import extract_all_fields

long_text = "i am male student studying 2nd year b tech in cvcr college of engineering in telangana my family income is below 2 lakhs"

print("Test: Long text with expected_field='gpa'")
res = extract_all_fields(long_text, expected_field="gpa")
print("Extracted:", res)

assert 'gpa' not in res, "GPA should NOT be extracted here!"
assert res.get('year') == 2
assert res.get('income') == 200000

print("Test: Short text implicitly acting as GPA")
res2 = extract_all_fields("8.5", expected_field="gpa")
print("Extracted:", res2)
assert res2.get('gpa') == 8.5

print("All tests passed perfectly!")
