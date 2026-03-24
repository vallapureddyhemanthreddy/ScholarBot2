import sys
sys.path.append('/home/hemanthxd/Downloads/scholarship_assistant_v3_offline/scholarship_app')

from nlp_engine import extract_all_fields, extract_gpa

# Test 1
print("Running extract_gpa directly:")
res_gpa = extract_gpa("8.5", is_expected=True)
print("extract_gpa('8.5', True) ->", res_gpa)

# Test 2
print("\nRunning extract_all_fields:")
res_all = extract_all_fields("8.5", expected_field="gpa")
print("extract_all_fields('8.5', 'gpa') ->", res_all)
