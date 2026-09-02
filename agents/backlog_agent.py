from crewai import Agent, Task, Crew, LLM
from github import Github
import os, json, re

llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.3,
    max_tokens=4096
)


# ──────────────────────────────────────────────
# UTILITAIRES
# ──────────────────────────────────────────────
def improve_title(title: str) -> str:
    title = title.strip()
    prefixes = ["As a ", "I want to ", "I want ", "To "]
    for prefix in prefixes:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):]
    if title:
        title = title[0].upper() + title[1:]
    if len(title) > 80:
        title = title[:77] + "..."
    return title if title else "User Story"

def extract_us_id(block: str, index: int) -> str:
    match = re.search(r'US-\d+', block)
    return match.group(0) if match else f"US-{index+1:02d}"

def repair_json(text: str) -> dict:
    patterns = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
        r'(\{[^{}]*"title"[^{}]*\})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                continue
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}

def summarize_us(all_us_text: str) -> str:
    """
    Crée un résumé complet de toutes les US
    pour que le LLM puisse toutes les analyser.
    """
    blocks = re.split(r'(?=\*\*US-\d+\*\*)', all_us_text)
    blocks = [b.strip() for b in blocks if b.strip() and 'US-' in b]
    summaries = []
    for block in blocks:
        us_id = re.search(r'US-\d+', block)
        title = re.search(r'\*\*Title\*\*\s*:\s*(.+)', block)
        i_want = re.search(r'\*\*I want\*\*\s*:\s*(.+)', block)
        so_that = re.search(r'\*\*So that\*\*\s*:\s*(.+)', block)
        criteria = re.findall(r'  - (.+)', block)
        
        summary = f"{us_id.group(0) if us_id else '?'}: "
        summary += f"{title.group(1).strip()[:100] if title else ''} | "
        summary += f"{i_want.group(1).strip()[:100] if i_want else ''} | "
        summary += f"So that: {so_that.group(1).strip()[:80] if so_that else ''} | "
        summary += f"Criteria: {len(criteria)}"
        summaries.append(summary)
    return "\n".join(summaries)


# ──────────────────────────────────────────────
# ÉTAPE 1 : Analyse globale - 100% LLM
# ──────────────────────────────────────────────
def analyze_all_us(agent: Agent, all_us_text: str, us_count: int) -> dict:
    us_summary = summarize_us(all_us_text)

    task = Task(
        description=(
            f"You have {us_count} user stories to organize.\n\n"
            "⚠️ YOU MUST ASSIGN ALL USER STORIES TO AN EPIC.\n"
            "NO USER STORY CAN BE LEFT WITHOUT AN EPIC.\n"
            "This is a MANDATORY requirement.\n\n"
            "Analyze ALL user stories and return a JSON with:\n"
            "1. Exactly 4 to 6 Epics that cover ALL user stories\n"
            "2. For each Epic, list ALL US IDs that belong to it\n"
            "3. Priority guidelines\n\n"
            "⚠️ CRITICAL: EVERY US-ID must appear in exactly one epic.\n"
            f"⚠️ The sum of us_ids across all epics MUST equal {us_count}.\n"
            "⚠️ If you don't assign all US, the system will fail.\n\n"
            "Format:\n"
            "{\n"
            '  "epics": [\n'
            '    {"name": "Epic Name", "us_ids": ["US-01", "US-02", ...]},\n'
            '    ...\n'
            '  ],\n'
            '  "priority_guidelines": {\n'
            '    "high": "security, compliance, blocking, critical features",\n'
            '    "medium": "standard important features",\n'
            '    "low": "optional, nice-to-have, future features"\n'
            '  }\n'
            "}\n\n"
            "CRITICAL RULES:\n"
            "1. EVERY US must be assigned to an Epic — NO US left without Epic\n"
            "2. NO 'General' Epic allowed — be specific\n"
            "3. 4 to 6 Epics maximum\n"
            "4. Each Epic must have at least 2 US\n"
            "5. Distribute US evenly across Epics\n"
            "6. ~20-30% high, ~50-60% medium, ~10-20% low\n\n"
            "User Stories:\n" + us_summary
        ),
        expected_output='JSON with epics list and priority guidelines',
        agent=agent
    )

    result = str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff())
    parsed = repair_json(result)

    if "epics" not in parsed or not isinstance(parsed.get("epics"), list):
        print("   ⚠️ Global analysis failed → fallback")
        return {"epics": [], "priority_guidelines": {}}

    # ⭐⭐⭐ 100% LLM : LE LLM EST RESPONSABLE DE COUVRIR TOUTES LES US ⭐⭐⭐
    # Le code ne fait qu'informer, pas corriger
    all_ids_covered = set()
    for epic in parsed.get("epics", []):
        all_ids_covered.update(epic.get("us_ids", []))
    
    all_us_ids = [f"US-{i+1:02d}" for i in range(us_count)]
    missing_ids = [us_id for us_id in all_us_ids if us_id not in all_ids_covered]
    
    # ⭐⭐⭐ 100% LLM : SI DES US SONT MANQUANTES, ON DEMANDE AU LLM DE LES CORRIGER ⭐⭐⭐
    if missing_ids:
        print(f"   ⚠️ US manquantes : {missing_ids}")
        print("   🔄 Demande de correction au LLM...")
        
        # DEMANDER AU LLM DE CORRIGER L'ANALYSE
        correction_task = Task(
            description=(
                f"Vous avez analysé {us_count} user stories mais vous avez oublié ces US : {missing_ids}\n\n"
                f"Vous devez CORRIGER votre analyse et assigner TOUTES les US.\n"
                f"Répondez UNIQUEMENT avec un JSON valide.\n\n"
                f"Voici votre analyse actuelle :\n{json.dumps(parsed, indent=2)}\n\n"
                f"Vous devez répartir les US manquantes dans les Epics existants.\n"
                f"NE PAS créer de nouvel Epic si possible.\n"
                f"NE PAS utiliser 'General' comme nom d'Epic.\n\n"
                f"Retournez le JSON corrigé avec TOUTES les {us_count} US assignées."
            ),
            expected_output='JSON avec toutes les US assignées',
            agent=agent
        )
        
        correction_result = str(Crew(agents=[agent], tasks=[correction_task], verbose=False).kickoff())
        corrected = repair_json(correction_result)
        
        if "epics" in corrected and isinstance(corrected.get("epics"), list):
            # Vérifier que toutes les US sont couvertes
            all_covered_again = set()
            for epic in corrected.get("epics", []):
                all_covered_again.update(epic.get("us_ids", []))
            
            if len(all_covered_again) == us_count:
                print(f"   ✅ Correction réussie : {len(all_covered_again)} US assignées")
                parsed = corrected
            else:
                print(f"   ⚠️ Correction partielle : {len(all_covered_again)}/{us_count} US assignées")
                # Fallback : ajouter les US manquantes
                missing_again = [us_id for us_id in all_us_ids if us_id not in all_covered_again]
                if missing_again:
                    print(f"   ⚠️ Ajout manuel des US manquantes : {missing_again}")
                    parsed["epics"].append({
                        "name": "Core Features",
                        "us_ids": sorted(missing_again)
                    })
        else:
            print("   ⚠️ Correction échouée, fallback manuel")
            # Fallback : ajouter les US manquantes
            parsed["epics"].append({
                "name": "Core Features",
                "us_ids": sorted(missing_ids)
            })

    # Vérification finale
    all_ids_final = set()
    for epic in parsed.get("epics", []):
        all_ids_final.update(epic.get("us_ids", []))
    
    print(f"   ✅ {len(parsed['epics'])} epics | {len(all_ids_final)} US assigned")
    for epic in parsed["epics"]:
        print(f"      • {epic.get('name')} → {epic.get('us_ids', [])}")

    return parsed


# ──────────────────────────────────────────────
# ÉTAPE 2 : Transformation US → Ticket - 100% LLM
# ──────────────────────────────────────────────
def us_to_ticket(agent: Agent, us_text: str, us_id: str,
                 epic_name: str, priority_guidelines: dict, index: int = 0) -> dict:

    guidelines_text = "\n".join([
        f"   - {k}: {v}"
        for k, v in priority_guidelines.items()
    ]) if priority_guidelines else (
        "   - high: security, encryption, GDPR, blocking\n"
        "   - medium: standard features\n"
        "   - low: optional, nice-to-have"
    )

    task = Task(
        description=(
            f"Transform this user story into a GitHub ticket.\n\n"
            f"Epic: '{epic_name}'\n"
            f"Priority guidelines:\n{guidelines_text}\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            '  "title": "concise action-oriented title (max 60 chars)",\n'
            '  "body": "detailed description with acceptance criteria",\n'
            '  "priority": "high|medium|low",\n'
            '  "feature": "specific feature name (no Epic name in it)"\n'
            "}\n\n"
            "RULES:\n"
            "1. Title: concise, action verb first, max 60 chars\n"
            "2. Body: include all acceptance criteria from the US\n"
            "3. Priority: follow the guidelines strictly\n"
            "   ~20-30% of tickets should be high\n"
            "   ~10-20% of tickets should be low\n"
            "4. Feature: specific name ONLY\n"
            "   ✅ GOOD: 'CV Parsing', 'Interview Scheduling'\n"
            "   ❌ BAD:  'Feature', 'Implement US-11'\n"
            "   ⚠️ MANDATORY: Feature name MUST be specific and descriptive\n\n"
            "User Story:\n" + us_text
        ),
        expected_output='JSON with title, body, priority, feature',
        agent=agent
    )

    result = str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff())
    ticket = repair_json(result)

    priority = ticket.get("priority", "medium")
    if priority not in ["high", "medium", "low"]:
        priority = "medium"

    # ⭐⭐ NETTOYAGE ET FALLBACK DE LA FEATURE ⭐⭐
    feature = ticket.get("feature", f"{epic_name} Feature")
    feature = feature.replace(f" within {epic_name}", "").strip()
    feature = feature.replace(f" within {epic_name} Epic", "").strip()
    feature = feature.replace(epic_name, "").strip()
    
    # Vérifier si le feature est générique
    generic_patterns = [
        r'^Implement\s+US-\d+$',
        r'^US-\d+$',
        r'^Feature$',
        r'^General Feature$',
        r'^Implement$'
    ]
    
    is_generic = any(re.search(p, feature, re.IGNORECASE) for p in generic_patterns)
    
    if is_generic or len(feature) < 3:
        # Extraire le titre de la US
        title_match = re.search(r'\*\*Title\*\*\s*:\s*(.+)', us_text)
        if title_match:
            title = title_match.group(1).strip()
            # Nettoyer le titre
            title = re.sub(r'^(Implement|Create|Add|Enable|Ensure|Allow|Manage)\s+', '', title)
            title = re.sub(r'\s+for\s+.*$', '', title)
            feature = title[:50]
        else:
            feature = f"{epic_name} Feature"

    return {
        "title"   : improve_title(ticket.get("title", f"Implement {us_id}")),
        "body"    : ticket.get("body", us_text.strip()),
        "priority": priority,
        "epic"    : epic_name,
        "feature" : feature,
        "us_id"   : us_id
    }
# ──────────────────────────────────────────────
# EXÉCUTION PRINCIPALE
# ──────────────────────────────────────────────
def run_backlog_agent(user_stories: str) -> list:
    print("\n🚀 Agent 2 : Backlog Management...")

    agent = Agent(
        role="Backlog Manager",
        goal="Transform user stories into a well-organized product backlog",
        backstory=(
            "Expert Agile Product Owner with 10 years experience.\n"
            "You organize user stories into 4-6 coherent Epics and Features.\n"
            "You NEVER use 'General' as an Epic name — always be specific.\n"
            "You assign priorities: ~25% high, ~55% medium, ~20% low.\n"
            "You ensure every ticket is traceable to its user story.\n"
            "Feature names are concise and never include the Epic name."
        ),
        llm=llm,
        verbose=False
    )

    blocks = re.split(r'(?=\*\*US-\d+\*\*)', user_stories)
    blocks = [b.strip() for b in blocks if b.strip() and 'US-' in b]
    print(f"📋 {len(blocks)} user stories detected")

    if not blocks:
        print("❌ No user stories found")
        return []

    g    = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPO"))

    existing_labels = [l.name for l in repo.get_labels()]
    for label, color in [
        ("high", "d73a4a"), ("medium", "e4e669"),
        ("low", "0075ca"), ("feature", "a2eeef"), ("epic", "7057ff")
    ]:
        if label not in existing_labels:
            repo.create_label(label, color)

    milestones = {ms.title: ms for ms in repo.get_milestones()}

    print("\n🔍 Step 1: Global analysis...")
    global_analysis = analyze_all_us(agent, user_stories, len(blocks))

    us_to_epic_map = {}
    for epic in global_analysis.get("epics", []):
        epic_name = epic.get("name", "")
        for us_id in epic.get("us_ids", []):
            us_to_epic_map[us_id] = epic_name

    priority_guidelines = global_analysis.get("priority_guidelines", {})

    print("\n⚙️  Step 2: Transforming user stories into tickets...")

    features         = {}
    created          = []
    backlog_lines    = ["# Product Backlog\n"]
    epics_created    = set()
    features_created = set()
    priorities_count = {"high": 0, "medium": 0, "low": 0}

    for i, block in enumerate(blocks):
        print(f"\n🔄 Processing US {i+1}/{len(blocks)}...")

        us_id     = extract_us_id(block, i)
        epic_name = us_to_epic_map.get(us_id, "Core Features")

        ticket = us_to_ticket(
            agent, block, us_id,
            epic_name, priority_guidelines
        )

        epics_created.add(ticket["epic"])
        features_created.add(ticket["feature"])
        priorities_count[ticket["priority"]] = \
            priorities_count.get(ticket["priority"], 0) + 1

        print(f"   🎯 Epic: {ticket['epic']} | Priority: {ticket['priority']}")

        if ticket["epic"] not in milestones:
            ms = repo.create_milestone(title=ticket["epic"])
            milestones[ticket["epic"]] = ms
            print(f"      ✅ Epic milestone created")

        if ticket["feature"] not in features:
            fi = repo.create_issue(
                title=f"[FEATURE] {ticket['feature']}",
                body=f"Feature: {ticket['feature']}\nEpic: {ticket['epic']}",
                labels=["feature"],
                milestone=milestones[ticket["epic"]]
            )
            features[ticket["feature"]] = fi.number
            print(f"   ⭐ Feature: #{fi.number} - {ticket['feature']}")

        body = (
            f"**User Story:** {us_id}\n"
            f"**Feature:** #{features[ticket['feature']]} - {ticket['feature']}\n"
            f"**Epic:** {ticket['epic']}\n\n"
            + ticket["body"]
        )
        issue = repo.create_issue(
            title=ticket["title"],
            body=body,
            labels=[ticket["priority"]],
            milestone=milestones[ticket["epic"]]
        )
        print(f"   ✅ Issue #{issue.number}: {issue.title} [{ticket['priority']}]")
        created.append(issue.number)

        backlog_lines.append(f"## [{ticket['priority'].upper()}] {ticket['title']}")
        backlog_lines.append(f"- **User Story:** {us_id}")
        backlog_lines.append(f"- **Epic:** {ticket['epic']}")
        backlog_lines.append(f"- **Feature:** {ticket['feature']}")
        backlog_lines.append(f"- **GitHub Issue:** #{issue.number}")
        backlog_lines.append(f"\n{ticket['body']}\n")

    os.makedirs("output", exist_ok=True)
    with open("output/backlog.md", "w", encoding="utf-8", errors="ignore") as f:
        f.write("\n".join(backlog_lines))

    total = sum(priorities_count.values())
    print(f"\n📊 Summary:")
    print(f"   Epics    : {len(epics_created)} → {', '.join(sorted(epics_created))}")
    print(f"   Features : {len(features_created)}")
    print(f"   Tickets  : {len(created)}")
    for p, count in priorities_count.items():
        pct = round((count / total) * 100, 1) if total > 0 else 0
        print(f"   {p.capitalize()}: {count} ({pct}%)")
    print("\n💾 Backlog saved: output/backlog.md")

    return created