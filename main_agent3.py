from dotenv import load_dotenv
from agents.qa_agent import run_qa_agent

load_dotenv()


def main():
    with open("output/user_stories.txt", "r", encoding="utf-8") as f:
        user_stories = f.read()

    print("🚀 QA AGENT START")

    results = run_qa_agent(user_stories, debug=True)

    print("\n✅ DONE:", len(results), "user stories processed")

    for r in results:
        nb_tests = len(r.get("test_cases", []))
        print(f"{r.get('id', '??')} -> {nb_tests} test cases")


if __name__ == "__main__":
    main()