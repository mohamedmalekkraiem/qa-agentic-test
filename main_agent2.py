from dotenv import load_dotenv
from agents.backlog_agent import run_backlog_agent

load_dotenv()

def main():
    with open("output/user_stories.txt", "r", encoding="utf-8") as f:
        user_stories = f.read()

    # Debug : affiche les 300 premiers caractères pour vérifier le format
    print("=== APERÇU DU FICHIER ===")
    print(user_stories[:300])
    print("=========================\n")

    print("🚀 Agent 2 : Backlog Management...")
    issues = run_backlog_agent(user_stories)
    print(f"\n✅ {len(issues)} issues créées sur GitHub : {issues}")

if __name__ == "__main__":
    main()