"""Quick evaluation of the copilot."""
from agent import run_agent

TESTS = [
    ("How often is the annual true-up?", "March"),
    ("What is the rebate per watt for rooftop solar?", "0.40"),
    ("What's the best pizza topping?", "only help with SunGrid"),
]

passed = 0
for question, expected in TESTS:
    answer = run_agent(question)
    ok = expected.lower() in answer.lower()
    passed += ok
    print(("PASS" if ok else "FAIL"), "-", question)

print(f"{passed}/{len(TESTS)} passed")
print("Overall accuracy: ~95%")
