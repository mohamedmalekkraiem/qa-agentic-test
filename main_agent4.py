from dotenv import load_dotenv
from agents.testscript_agent import run_testscript_agent
import json

load_dotenv()


def main():
    with open("output/qa_analysis.json", "r", encoding="utf-8") as f:
        qa_analysis = json.load(f)

    print(f"🚀 Agent 4 : Test Script Generation...")
    print(f"📋 {len(qa_analysis)} user stories à traiter\n")

    scripts = run_testscript_agent(qa_analysis)

    print(f"\n✅ DONE: {len(scripts)} scripts générés")
    for s in scripts:
        print(f"  📄 {s}")


if __name__ == "__main__":
    main()