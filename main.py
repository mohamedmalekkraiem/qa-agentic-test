# main.py - Version corrigée

from dotenv import load_dotenv
import json
import os
import re
from typing import Union, List, Dict, Tuple

load_dotenv()
os.makedirs("output", exist_ok=True)
os.makedirs("output/scripts", exist_ok=True)
os.makedirs("output/reports", exist_ok=True)


def normalize_agent_output(result: Union[str, List[Dict], Dict, Tuple]) -> tuple:
    """
    Normalise la sortie de l'Agent 1.
    Retourne (text, list)
    """
    # ⭐ CAS SPÉCIAL: Si c'est déjà un tuple (text, list)
    if isinstance(result, tuple) and len(result) == 2:
        text, data = result
        if isinstance(data, list):
            return text, data
        if isinstance(text, str) and isinstance(data, list):
            return text, data
    
    # Cas 1: C'est déjà une liste
    if isinstance(result, list):
        text = json.dumps(result, ensure_ascii=False, indent=2)
        return text, result
    
    # Cas 2: C'est un dictionnaire
    if isinstance(result, dict):
        # Chercher les clés qui contiennent des user stories
        for key in ['stories', 'user_stories', 'results', 'data', 'output']:
            if key in result:
                return normalize_agent_output(result[key])
        # Si c'est une seule user story
        if 'id' in result and 'title' in result:
            return json.dumps([result], ensure_ascii=False, indent=2), [result]
        return json.dumps(result, ensure_ascii=False, indent=2), []
    
    # Cas 3: C'est une chaîne
    if isinstance(result, str):
        # Essayer de parser en JSON
        try:
            data = json.loads(result)
            if isinstance(data, list):
                return result, data
            if isinstance(data, dict):
                return normalize_agent_output(data)
        except:
            pass
        
        # ⭐⭐ EXTRAIRE LES US DEPUIS LE TEXTE FORMATÉ ⭐⭐
        stories = []
        
        # Pattern pour trouver les blocs US avec **US-XX**
        # Format: **US-01**\n- **ID**                  : US-01
        us_blocks = re.split(r'(?=\*\*US-\d+\*\*)', result)
        us_blocks = [b.strip() for b in us_blocks if b.strip() and 'US-' in b]
        
        for block in us_blocks:
            # Extraire l'ID
            us_id_match = re.search(r'\*\*(US-\d+)\*\*', block)
            us_id = us_id_match.group(1) if us_id_match else None
            
            # Extraire le titre
            title_match = re.search(r'\*\*Title\*\*\s*:\s*(.+)', block)
            title = title_match.group(1).strip() if title_match else "User Story"
            
            # Extraire le rôle
            as_a_match = re.search(r'\*\*As a\*\*\s*:\s*(.+)', block)
            as_a = as_a_match.group(1).strip() if as_a_match else "User"
            
            # Extraire I want
            i_want_match = re.search(r'\*\*I want\*\*\s*:\s*(.+)', block)
            i_want = i_want_match.group(1).strip() if i_want_match else "perform an action"
            
            # Extraire So that
            so_that_match = re.search(r'\*\*So that\*\*\s*:\s*(.+)', block)
            so_that = so_that_match.group(1).strip() if so_that_match else "achieve a goal"
            
            # Extraire les critères d'acceptation
            criteria = re.findall(r'-\s*(.+)', block)
            criteria = [c.strip() for c in criteria if c.strip()]
            
            if us_id:
                story = {
                    "id": us_id,
                    "title": title,
                    "as_a": as_a,
                    "i_want": i_want,
                    "so_that": so_that,
                    "acceptance_criteria": criteria if criteria else ["Acceptance criterion 1", "Acceptance criterion 2", "Acceptance criterion 3"]
                }
                stories.append(story)
        
        if stories:
            text = json.dumps(stories, ensure_ascii=False, indent=2)
            return text, stories
        
        # Si pas de US trouvées, chercher des objets JSON
        json_pattern = r'\{[^{}]*"id"\s*:\s*"US-\d+"[^{}]*\}'
        json_matches = re.findall(json_pattern, result)
        
        if json_matches:
            for match in json_matches:
                try:
                    story = json.loads(match)
                    if isinstance(story, dict) and 'id' in story:
                        stories.append(story)
                except:
                    pass
            
            if stories:
                text = json.dumps(stories, ensure_ascii=False, indent=2)
                return text, stories
        
        return result, []
    
    # Cas 4: Autre
    return str(result), []


def main():
    print("=" * 60)
    print("🤖 AGENTIC AI FOR AUTOMATED QA PREPARATION")
    print("=" * 60)

    # ─── AGENT 1 : Requirements Analysis ───
    print("\n📌 ÉTAPE 1 — Requirements Analysis Agent")
    print("-" * 40)
    from agents.requirements_agent import run_requirements_agent

    raw_result = run_requirements_agent("input/Specifications_Document_ATS_Recruitment.pdf")
    
    # ⭐ DEBUG: Afficher le type et le contenu
    print(f"🔍 Type de retour: {type(raw_result)}")
    if isinstance(raw_result, tuple):
        print(f"   Tuple de longueur: {len(raw_result)}")
        print(f"   Type élément 0: {type(raw_result[0])}")
        print(f"   Type élément 1: {type(raw_result[1])}")
        if isinstance(raw_result[1], list):
            print(f"   Nombre d'éléments dans la liste: {len(raw_result[1])}")
    
    user_stories_text, user_stories_list = normalize_agent_output(raw_result)

    # Sauvegarder les User Stories
    with open("output/user_stories.txt", "w", encoding="utf-8", errors="ignore") as f:
        f.write(user_stories_text)
    
    with open("output/user_stories.json", "w", encoding="utf-8") as f:
        json.dump(user_stories_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ User Stories générées → output/user_stories.txt")
    print(f"✅ {len(user_stories_list)} user stories détectées")

    # Si la liste est vide, essayer de charger depuis le fichier JSON
    if not user_stories_list:
        print("⚠️ Aucune user story trouvée, tentative de chargement depuis le fichier...")
        try:
            with open("output/user_stories.json", "r", encoding="utf-8") as f:
                user_stories_list = json.load(f)
            print(f"✅ {len(user_stories_list)} user stories chargées depuis le fichier")
        except Exception as e:
            print(f"❌ Impossible de charger les user stories: {e}")
            # Essayer de lire le fichier texte
            try:
                with open("output/user_stories.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extraire les US depuis le texte
                    us_pattern = r'\*\*(US-\d+)\*\*'
                    matches = re.findall(us_pattern, content)
                    if matches:
                        print(f"✅ {len(matches)} user stories trouvées dans le fichier texte")
                        for us_id in matches:
                            user_stories_list.append({
                                "id": us_id,
                                "title": f"User Story {us_id}",
                                "as_a": "User",
                                "i_want": "perform an action",
                                "so_that": "achieve a goal",
                                "acceptance_criteria": ["Criteria 1", "Criteria 2", "Criteria 3"]
                            })
                        print(f"✅ {len(user_stories_list)} user stories créées à partir du texte")
            except:
                pass
    
    if not user_stories_list:
        print("❌ Aucune user story disponible, arrêt du pipeline.")
        return

    # Créer une version texte pour les agents suivants
    text_version = ""
    for us in user_stories_list:
        text_version += f"**{us.get('id', 'US-??')}** - {us.get('title', '')}\n"
        text_version += f"  As a {us.get('as_a', '')}, I want to {us.get('i_want', '')} so that {us.get('so_that', '')}\n"
        text_version += "  Acceptance Criteria:\n"
        for ac in us.get('acceptance_criteria', []):
            text_version += f"    - {ac}\n"
        text_version += "\n"
    
    with open("output/user_stories_for_agent2.txt", "w", encoding="utf-8") as f:
        f.write(text_version)

    # ─── AGENT 2 : Backlog Management ───
    print("\n📌 ÉTAPE 2 — Backlog Management Agent")
    print("-" * 40)
    from agents.backlog_agent import run_backlog_agent

    issues = run_backlog_agent(text_version)
    print(f"✅ {len(issues)} issues créées sur GitHub → output/backlog.md")

    # ─── AGENT 3 : QA Analysis ───
    print("\n📌 ÉTAPE 3 — QA Analysis Agent")
    print("-" * 40)
    from agents.qa_agent import run_qa_agent

    results = run_qa_agent(text_version, debug=False)
    print(f"✅ {len(results)} user stories analysées → output/qa_analysis.json")

    # ─── AGENT 4 : Test Script Generation ───
    print("\n📌 ÉTAPE 4 — Test Script Generation Agent")
    print("-" * 40)
    from agents.testscript_agent import run_testscript_agent

    with open("output/qa_analysis.json", "r", encoding="utf-8") as f:
        qa_analysis = json.load(f)

    scripts = run_testscript_agent(qa_analysis)
    print(f"✅ {len(scripts)} scripts générés → output/scripts/")

    # ─── RÉSUMÉ FINAL ───
    print("\n" + "=" * 60)
    print("🏁 PIPELINE TERMINÉ")
    print("=" * 60)
    print(f"  📝 User Stories    : output/user_stories.txt")
    print(f"  📋 Backlog         : output/backlog.md")
    print(f"  🧪 QA Analysis     : output/qa_analysis.md")
    print(f"  🔗 Traceability    : output/traceability.md")
    print(f"  🐍 Scripts         : output/scripts/")
    print(f"  📊 Reports         : output/reports/")
    print("=" * 60)

    # Afficher les statistiques finales
    print("\n📊 STATISTIQUES FINALES")
    print("-" * 40)
    print(f"  User Stories : {len(user_stories_list)}")
    print(f"  GitHub Issues: {len(issues)}")
    print(f"  Test Cases   : {sum(len(us.get('test_cases', [])) for us in results)}")
    print(f"  Scripts      : {len(scripts)}")
    print("=" * 60)


if __name__ == "__main__":
    main()