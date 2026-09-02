from dotenv import load_dotenv
import json
import os
from agents.requirements_agent import run_requirements_agent

load_dotenv()

def main():
    print("🚀 Agent 1 : Requirements Analysis...")
    result, stories = run_requirements_agent("input/Specifications_Document_ATS_Recruitment.pdf")

    print("\n✅ User Stories générées :")
    print(result)

    os.makedirs("output", exist_ok=True)

    with open("output/user_stories.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("\n💾 Sauvegardé dans output/user_stories.txt")

    with open("output/user_stories.json", "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)
    print("💾 Sauvegardé dans output/user_stories.json")

if __name__ == "__main__":
    main()