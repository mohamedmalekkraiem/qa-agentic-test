import os
import json
import re
import fitz

os.environ.setdefault("OPENAI_API_KEY", "fake-key-not-used")

from crewai import Agent, Task, Crew, LLM

llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.2,
    max_tokens=4096,
)

# ──────────────────────────────────────────────
# PDF - Lecture
# ──────────────────────────────────────────────
def read_pdf_pages(path: str) -> list:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append((i + 1, text))
    return pages

def read_pdf(path: str) -> str:
    return "\n".join(t for _, t in read_pdf_pages(path))

def group_pages(pages: list, size: int = 3) -> list:
    groups = []
    for i in range(0, len(pages), size):
        batch = pages[i:i + size]
        combined = "\n\n".join(f"[Page {n}]\n{t}" for n, t in batch)
        groups.append(combined)
    return groups


# ──────────────────────────────────────────────
# 🔍 EXTRACTION D'IDs - UNIVERSELLE
# ──────────────────────────────────────────────
def extract_ids(text: str) -> list:
    """Extrait tous les identifiants possibles du texte."""
    patterns = [
        r'\b(F-\d+|REQ-\d+|NFR-\d+|US[A-Z]*-\d+)\b',
        r'\b(DECEMP\d+|ANXBEN\d+|ANXDEB\d+|ANXFIN\d+|[DAT]\d{3})\b',
        r'\b(Article\s+\d+|Art\.?\s*\d+)\b',
        r'\b(JOB-\d+|POS-\d+|CAND-\d+|APPL-\d+)\b',
        r'\b(PAT-\d+|DIAG-\d+|TREAT-\d+|MED-\d+)\b',
        r'\b([A-Z]{2,}-\d+)\b',
        r'\b(Section|Chapter|Module)\s+(\d+)\b',
    ]
    
    found = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                found.add(" ".join(match).strip())
            else:
                found.add(match.strip())
    
    # Filtrer les faux positifs
    invalid = [
        'AES-256', 'RSA-256', 'SHA-256', 'MD5-128',
        'API', 'HTTP', 'HTTPS', 'SSL', 'TLS',
        'JSON', 'XML', 'HTML', 'CSS',
        'PDF', 'DOCX', 'XLSX', 'CSV', 'TXT'
    ]
    
    filtered = [id_str for id_str in found if id_str not in invalid and len(id_str) >= 3]
    
    normalized = []
    seen = set()
    for id_str in sorted(filtered):
        key = id_str.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(id_str)
    
    return normalized


# ──────────────────────────────────────────────
# 🔍 DÉTECTION DU TYPE DE DOCUMENT
# ──────────────────────────────────────────────
def detect_document_type(text: str) -> dict:
    text_lower = text.lower()
    
    keywords = {
        "technical": [
            "zone", "position", "longueur", "enregistrement", "decemp", "anxben",
            "field", "record", "length", "encoding", "format", "ascii"
        ],
        "legal": [
            "article", "chapitre", "alinéa", "disposition", "obligation",
            "doit", "interdit", "sanction"
        ],
        "hr": [
            "recruitment", "hiring", "candidate", "cv", "resume", "interview",
            "job posting", "applicant", "ats", "hr"
        ],
        "functional": [
            "requirement", "user story", "functional", "module", "feature",
            "acceptance criteria", "must", "should"
        ],
        "finance": [
            "tax", "fiscal", "accounting", "payroll", "invoice",
            "financial", "audit", "compliance"
        ],
        "medical": [
            "patient", "doctor", "hospital", "clinic", "medical",
            "diagnosis", "treatment"
        ]
    }
    
    scores = {}
    for doc_type, words in keywords.items():
        scores[doc_type] = sum(1 for kw in words if kw in text_lower)
    scores["general"] = 0
    
    doc_type = max(scores, key=scores.get)
    if scores[doc_type] == 0:
        doc_type = "general"
    
    all_ids = extract_ids(text)
    
    # Si aucun ID trouvé, estimer
    if not all_ids:
        paragraphs = len(re.findall(r'\n\s*\n', text))
        all_ids = [f"REQ-{i+1:03d}" for i in range(min(max(5, paragraphs), 50))]
    
    # Rôles par type
    roles_by_type = {
        "technical": [
            "System Architect", "Technical Lead", "Developer",
            "QA Tester", "DevOps Engineer", "Data Engineer",
            "Security Analyst", "System Integrator",
            "Technical Writer", "Product Owner"
        ],
        "legal": [
            "Legal Advisor", "Compliance Officer", "Auditor",
            "Contract Manager", "Risk Analyst", "Regulatory Specialist",
            "Corporate Counsel", "Policy Analyst",
            "Legal Secretary", "Compliance Director"
        ],
        "hr": [
            "HR Manager", "Hiring Manager", "Recruiter",
            "Talent Acquisition Specialist", "IT Manager",
            "GDPR Officer", "HR Business Partner",
            "Talent Manager", "Recruitment Coordinator", "Candidate"
        ],
        "functional": [
            "Product Manager", "Business Analyst", "Project Manager",
            "Scrum Master", "Developer", "QA Tester",
            "UX Designer", "System Integrator",
            "Architect", "Product Owner"
        ],
        "finance": [
            "Financial Analyst", "Accountant", "Tax Specialist",
            "Auditor", "Compliance Officer", "Risk Manager",
            "Investment Advisor", "Banking Manager",
            "Financial Controller", "Treasury Manager"
        ],
        "general": [
            "Product Manager", "Project Manager", "Business Analyst",
            "Developer", "QA Tester", "System Integrator",
            "DevOps Engineer", "Scrum Master",
            "Architect", "Technical Lead"
        ]
    }
    
    roles = roles_by_type.get(doc_type, roles_by_type["general"])
    
    return {
        "type": doc_type,
        "scores": scores,
        "ids": all_ids,
        "roles": roles[:10],
        "domain": doc_type.capitalize()
    }


# ──────────────────────────────────────────────
# JSON repair - AMÉLIORÉ
# ──────────────────────────────────────────────
def repair_and_parse_json(text: str):
    """Répare et parse le JSON, retourne une liste de dictionnaires."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    
    if start == -1 or end == -1:
        s = cleaned.find("{")
        e = cleaned.rfind("}")
        if s != -1 and e != -1:
            try:
                obj = json.loads(cleaned[s:e+1])
                return [obj] if isinstance(obj, dict) else []
            except:
                objects = re.findall(r'\{[^{}]*\}', cleaned, re.DOTALL)
                results = []
                for obj_str in objects:
                    try:
                        obj = json.loads(obj_str)
                        if isinstance(obj, dict):
                            results.append(obj)
                    except:
                        continue
                return results if results else None
        return None
    
    candidate = cleaned[start:end + 1]
    candidate = re.sub(r'\}\s*\{', '},{', candidate)
    candidate = re.sub(r',\s*\]', ']', candidate)
    candidate = re.sub(r',\s*\}', '}', candidate)
    candidate = re.sub(r',\s*,', ',', candidate)
    candidate = re.sub(r'\{\s*,', '{', candidate)
    candidate = re.sub(r"'([^']*)'", r'"\1"', candidate)
    
    try:
        result = json.loads(candidate)
        if isinstance(result, list):
            result = [item for item in result if isinstance(item, dict)]
            return result if result else None
        elif isinstance(result, dict):
            return [result]
        return None
    except json.JSONDecodeError:
        objects = re.findall(r'\{[^{}]*\}', candidate, re.DOTALL)
        results = []
        for obj_str in objects:
            try:
                obj_str = re.sub(r',\s*,', ',', obj_str)
                obj = json.loads(obj_str)
                if isinstance(obj, dict):
                    results.append(obj)
            except:
                continue
        return results if results else None


# ──────────────────────────────────────────────
# Generate US - PROMPT OPTIMISÉ (SANS FORCER LES IDs DANS LES TITRES)
# ──────────────────────────────────────────────
def generate_from_page_group(agent: Agent, ctx: dict,
                              page_text: str, nb_us: int,
                              roles: list, offset: int,
                              doc_type: str,
                              force_ids: list = None) -> list:
    """Génère des US avec prompt optimisé."""
    
    group_ids = force_ids if force_ids is not None else extract_ids(page_text)
    
    if force_ids and len(force_ids) == 0:
        force_ids = None
        group_ids = None
    
    if group_ids and len(group_ids) < nb_us:
        nb_us = len(group_ids)
    
    if nb_us == 0:
        nb_us = 5
    
    role_assignments = []
    for i in range(nb_us):
        role = roles[(offset + i) % len(roles)]
        role_assignments.append(f"  US-{i+1:02d} → role: {role}")

    # Contextes par type
    context_hints = {
        "technical": "Each US must describe a technical rule or data validation.",
        "legal": "Each US must describe a legal obligation or business rule.",
        "hr": "Each US must describe a hiring or HR process.",
        "functional": "Each US must describe a specific feature or capability.",
        "finance": "Each US must describe a financial or tax process.",
        "medical": "Each US must describe a medical or health process.",
        "general": "Each US must describe a specific requirement or rule."
    }
    
    context_hint = context_hints.get(doc_type, context_hints["general"])

    if force_ids and len(force_ids) > 0:
        id_instruction = (
            f"MANDATORY: Generate EXACTLY {len(force_ids)} user stories.\n"
            f"Requirement IDs to cover: {force_ids}\n"
            "ONE story per ID.\n"
            "⭐ IMPORTANT: The ID must appear in the acceptance criteria, NOT in the title.\n"
            "Example: Title: 'Secure attachments' | Acceptance Criteria: 'System must use AES-256 encryption (F-09)'\n\n"
        )
    else:
        id_instruction = f"Generate exactly {nb_us} user stories covering distinct elements from the text.\n\n"

    # ⭐ PROMPT OPTIMISÉ AVEC 3 CRITÈRES OBLIGATOIRES
    prompt = f"""
Generate exactly {nb_us} user stories from this document.

CONTEXT: {ctx.get('type')} document - {context_hint}

{id_instruction}

Role assignments:
{chr(10).join(role_assignments)}

STRICT RULES:
1. Return ONLY a JSON array, no text before or after
2. Format: [{{"id":"US-01","title":"...","as_a":"...","i_want":"...","so_that":"...","acceptance_criteria":["criteria1","criteria2","criteria3"]}}]
3. ⭐⭐⭐ EACH USER STORY MUST HAVE EXACTLY 3 ACCEPTANCE CRITERIA ⭐⭐⭐
4. Each US must cover a DIFFERENT requirement
5. ⭐ Titles must NOT contain the requirement ID - only a descriptive title ⭐
6. ⭐ The ID MUST appear in the acceptance criteria (e.g., "System must comply with F-01") ⭐
7. acceptance_criteria MUST be 3 verifiable criteria directly from the document
8. ⭐ NEVER write "Requirement complies with the document" as a criteria ⭐
9. Criteria must be specific, verifiable, and actionable

Document content:
{page_text[:4000]}
"""

    task = Task(
        description=prompt,
        expected_output=f"Valid JSON array of {nb_us} user stories",
        agent=agent,
    )
    
    try:
        result = str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff())
    except Exception as e:
        print(f"   ❌ Erreur LLM: {e}")
        return []
    
    stories = repair_and_parse_json(result)
    
    if not stories:
        return []
    
    stories = [s for s in stories if isinstance(s, dict)]
    
    if not stories:
        return []
    
    # Vérifier que chaque US a 3 critères
    for us in stories:
        criteria = us.get("acceptance_criteria", [])
        if not isinstance(criteria, list):
            criteria = [str(criteria)]
        
        # Si moins de 3 critères, ajouter des critères génériques
        while len(criteria) < 3:
            criteria.append(f"System must comply with the document requirements")
        
        us["acceptance_criteria"] = criteria[:3]
    
    # Assigner les IDs en métadonnées
    if force_ids and len(force_ids) > 0 and len(stories) == len(force_ids):
        for us, rid in zip(stories, force_ids):
            us["requirement_id"] = rid
    elif force_ids:
        for us in stories:
            blob = " ".join([
                us.get("title", ""), us.get("i_want", ""), us.get("so_that", "")
            ] + [str(c) for c in us.get("acceptance_criteria", [])])
            found = extract_ids(blob)
            us["requirement_id"] = found[0] if found else None

    # ⭐⭐⭐ NE PAS AJOUTER L'ID DANS LE TITRE
    # L'ID reste uniquement dans les métadonnées
    # Si l'ID est présent dans le titre, on le retire
    for us in stories:
        rid = us.get("requirement_id")
        if rid:
            title = us.get("title", "")
            # Si l'ID est dans le titre, on l'enlève
            if rid in title:
                title = title.replace(f"({rid})", "").replace(f"{rid}", "").replace("  ", " ").strip()
                us["title"] = title

    return stories


# ──────────────────────────────────────────────
# Deduplication
# ──────────────────────────────────────────────
def normalize(s: str) -> str:
    return re.sub(r'\s+', ' ', s.lower().strip())

def deduplicate(stories: list) -> list:
    seen_titles = set()
    seen_criteria = set()
    seen_requirement_ids = set()
    unique = []
    for us in stories:
        title_key = normalize(us.get("title", ""))
        criteria_list = us.get("acceptance_criteria", [])
        if not isinstance(criteria_list, list):
            criteria_list = [str(criteria_list)]
        criteria_key = frozenset(normalize(c) for c in criteria_list)
        
        req_id = us.get("requirement_id")
        req_id_key = req_id.lower().replace(" ", "") if req_id else None

        if req_id_key and req_id_key in seen_requirement_ids:
            continue
        if title_key and title_key in seen_titles:
            continue
        if criteria_key and criteria_key in seen_criteria:
            continue

        if req_id_key:
            seen_requirement_ids.add(req_id_key)
        if title_key:
            seen_titles.add(title_key)
        if criteria_key:
            seen_criteria.add(criteria_key)
        unique.append(us)
    return unique


# ──────────────────────────────────────────────
# Filtrage
# ──────────────────────────────────────────────
def filter_to_valid_ids(stories: list, target_ids: list) -> list:
    if not target_ids:
        return stories
    
    target_set = {rid.lower().replace(" ", "") for rid in target_ids}
    
    valid_stories = []
    seen_ids = set()
    
    for us in stories:
        rid = us.get("requirement_id")
        
        if not rid:
            title = us.get("title", "")
            criteria = " ".join(us.get("acceptance_criteria", []))
            full_text = f"{title} {criteria}"
            
            found_ids = extract_ids(full_text)
            valid_found = []
            for fid in found_ids:
                fid_key = fid.lower().replace(" ", "")
                if fid_key in target_set and fid_key not in seen_ids:
                    valid_found.append(fid)
            
            if valid_found:
                rid = valid_found[0]
                us["requirement_id"] = rid
            else:
                continue
        
        rid_key = rid.lower().replace(" ", "")
        
        if rid_key in target_set and rid_key not in seen_ids:
            valid_stories.append(us)
            seen_ids.add(rid_key)
    
    return valid_stories


# ──────────────────────────────────────────────
# RÉCONCILIATION AMÉLIORÉE
# ──────────────────────────────────────────────
def reconcile_missing_ids(agent: Agent, ctx: dict, raw_text: str,
                           all_stories: list, target_ids: list,
                           doc_type: str, max_rounds: int = 5) -> list:
    """Vérifie et génère les IDs manquants de manière agressive."""
    for round_num in range(max_rounds):
        # IDs déjà couverts
        covered = set()
        for us in all_stories:
            rid = us.get("requirement_id")
            if rid:
                covered.add(rid.lower().replace(" ", ""))
        
        # IDs manquants
        missing = []
        for rid in target_ids:
            if rid.lower().replace(" ", "") not in covered:
                missing.append(rid)
        
        if not missing:
            print(f"   ✅ Tous les IDs sont couverts")
            return all_stories
        
        print(f"   ⚠️ Round {round_num+1}: {len(missing)} IDs manquants: {missing[:5]}...")
        
        # Extraire le contexte pour chaque ID manquant
        relevant_pages = []
        for rid in missing[:10]:  # Limiter à 10 IDs par round
            # Chercher le contexte
            context_match = re.search(rf'.{{0,500}}{re.escape(rid)}.{{0,500}}', raw_text, re.DOTALL | re.IGNORECASE)
            if context_match:
                relevant_pages.append(f"[ID: {rid}]\n{context_match.group(0)}")
            else:
                # Chercher sans séparateur
                rid_clean = rid.replace("-", " ").replace("_", " ")
                context_match = re.search(rf'.{{0,500}}{re.escape(rid_clean)}.{{0,500}}', raw_text, re.DOTALL | re.IGNORECASE)
                if context_match:
                    relevant_pages.append(f"[ID: {rid}]\n{context_match.group(0)}")
        
        if not relevant_pages:
            relevant_text = raw_text[:3000]
        else:
            relevant_text = "\n\n---\n\n".join(relevant_pages)
        
        # Générer par lots de 5
        temp_roles = ["Product Manager", "Developer", "QA Tester", "Project Manager", "Business Analyst"]
        
        for i in range(0, len(missing), 5):
            batch = missing[i:i+5]
            print(f"   → Génération pour: {batch}")
            
            gap_stories = generate_from_page_group(
                agent=agent,
                ctx=ctx,
                page_text=relevant_text + f"\n\nMANDATORY: Generate stories for these IDs: {batch}",
                nb_us=len(batch),
                roles=temp_roles,
                offset=len(all_stories),
                doc_type=doc_type,
                force_ids=batch
            )
            
            print(f"   → {len(gap_stories)} US générées")
            all_stories.extend(gap_stories)
        
        all_stories = filter_to_valid_ids(all_stories, target_ids)
    
    return all_stories


# ──────────────────────────────────────────────
# Distribuer les rôles
# ──────────────────────────────────────────────
def distribute_roles(stories: list, doc_type: str) -> list:
    if not stories:
        return stories
    
    roles_by_type = {
        "technical": [
            "System Architect", "Technical Lead", "Developer",
            "QA Tester", "DevOps Engineer", "Data Engineer",
            "Security Analyst", "System Integrator",
            "Technical Writer", "Product Owner"
        ],
        "legal": [
            "Legal Advisor", "Compliance Officer", "Auditor",
            "Contract Manager", "Risk Analyst", "Regulatory Specialist",
            "Corporate Counsel", "Policy Analyst",
            "Legal Secretary", "Compliance Director"
        ],
        "hr": [
            "HR Manager", "Hiring Manager", "Recruiter",
            "Talent Acquisition Specialist", "IT Manager",
            "GDPR Officer", "HR Business Partner",
            "Talent Manager", "Recruitment Coordinator", "Candidate"
        ],
        "functional": [
            "Product Manager", "Business Analyst", "Project Manager",
            "Scrum Master", "Developer", "QA Tester",
            "UX Designer", "System Integrator",
            "Architect", "Product Owner"
        ],
        "finance": [
            "Financial Analyst", "Accountant", "Tax Specialist",
            "Auditor", "Compliance Officer", "Risk Manager",
            "Investment Advisor", "Banking Manager",
            "Financial Controller", "Treasury Manager"
        ],
        "general": [
            "Product Manager", "Project Manager", "Business Analyst",
            "Developer", "QA Tester", "System Integrator",
            "DevOps Engineer", "Scrum Master",
            "Architect", "Technical Lead"
        ]
    }
    
    roles = roles_by_type.get(doc_type, roles_by_type["general"])
    
    for i, us in enumerate(stories):
        us["as_a"] = roles[i % len(roles)]
    
    return stories


# ──────────────────────────────────────────────
# Numbering & formatting
# ──────────────────────────────────────────────
def renumber(stories: list) -> list:
    for i, us in enumerate(stories, start=1):
        us["id"] = f"US-{i:02d}"
    return stories

def format_user_stories(stories: list) -> str:
    lines = []
    for us in stories:
        us_id = us.get("id", "US-??")
        title = us.get("title", "User Story")
        as_a = us.get("as_a", "User")
        i_want = us.get("i_want", "")
        so_that = us.get("so_that", "Ensure compliance")
        criteria = us.get("acceptance_criteria", [])

        if not isinstance(criteria, list):
            criteria = [str(criteria)]
        if not criteria:
            criteria = ["Requirement complies with the document"]

        lines.append(f"**{us_id}**\n")
        lines.append(f"- **ID**                  : {us_id}")
        lines.append(f"- **Title**               : {title}")
        lines.append(f"- **As a**                : {as_a}")
        lines.append(f"- **I want**              : {i_want}")
        lines.append(f"- **So that**             : {so_that}")
        lines.append(f"- **Acceptance Criteria** :")
        for c in criteria:
            lines.append(f"  - {c}")
        lines.append("")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# MAIN - UNIVERSEL OPTIMISÉ
# ──────────────────────────────────────────────
def run_requirements_agent(cdc_path: str) -> tuple:
    print("🚀 Agent 1 - Requirements Analysis (Universal)")
    print("=" * 60)
    
    # 1. Lire le PDF
    raw_text = read_pdf(cdc_path)
    pages = read_pdf_pages(cdc_path)
    print(f"📄 PDF: {len(pages)} pages loaded")

    # 2. Détection
    print("\n🔍 Auto-detecting document type...")
    ctx = detect_document_type(raw_text)
    
    print(f"   ✅ Type: {ctx['type'].upper()}")
    print(f"   📊 Scores: {ctx['scores']}")
    print(f"   📋 IDs trouvés: {len(ctx['ids'])}")
    
    # 3. Filtrer les IDs
    all_ids = ctx['ids']
    
    # Détecter les IDs DECEMP
    decemp_ids = [rid for rid in all_ids if rid.startswith('DECEMP')]
    article_ids = [rid for rid in all_ids if rid.startswith('Article') or rid.startswith('Art.')]
    functional_ids = [rid for rid in all_ids if re.match(r'F-\d+|REQ-\d+', rid)]
    
    # Prioriser les IDs
    if decemp_ids:
        print(f"   📋 DECEMP IDs: {len(decemp_ids)}")
        target_ids = sorted(decemp_ids, key=lambda x: int(x.replace('DECEMP', '')) if x.replace('DECEMP', '').isdigit() else 999)
        use_force_ids = True
    elif article_ids:
        print(f"   📋 Article IDs: {len(article_ids)}")
        target_ids = sorted(article_ids)
        use_force_ids = True
    elif functional_ids:
        print(f"   📋 Functional IDs: {len(functional_ids)}")
        target_ids = sorted(functional_ids)
        use_force_ids = True
    else:
        print(f"   ⚠️ IDs génériques détectés")
        target_ids = all_ids[:30]
        use_force_ids = len(target_ids) > 0
    
    print(f"   📋 IDs cibles: {len(target_ids)}")
    if len(target_ids) <= 10:
        print(f"   📋 IDs: {target_ids}")
    else:
        print(f"   📋 IDs: {target_ids[:5]}... ({len(target_ids) - 5} more)")

    # 4. Créer l'agent
    agent = Agent(
        role="Requirements Analyst",
        goal="Extract user stories from documents",
        backstory=(
            "Expert in functional analysis and Agile methodology. "
            "You analyze any type of document and generate user stories "
            "based STRICTLY on the provided text. "
            "You NEVER invent requirements absent from the document."
        ),
        llm=llm,
        verbose=True,
    )

    # 5. Génération
    print(f"\n⚙️  Generating user stories...")
    
    content_pages = pages[1:] if len(pages) > 1 else pages
    page_groups = group_pages(content_pages, size=3)
    
    # Calcul du nombre d'US
    total_us = len(target_ids) if target_ids else 10
    us_per_group = max(5, min(15, total_us // max(len(page_groups), 1) + 2))
    
    print(f"   📊 Total US: {total_us}")
    print(f"   📊 US par groupe: {us_per_group}")
    print(f"   📊 Groupes: {len(page_groups)}")
    
    all_stories = []
    offset = 0
    
    # Génération par groupes de pages
    for i, group_text in enumerate(page_groups):
        remaining = total_us - len(all_stories)
        if remaining <= 0:
            break
        
        batch_size = min(us_per_group, remaining)
        print(f"\n   📑 Group {i+1}/{len(page_groups)} → {batch_size} US")
        print(f"   Preview: {group_text[:100].strip()}...")
        
        # IDs pour ce groupe
        group_ids = extract_ids(group_text)
        force = None
        
        if use_force_ids and group_ids and target_ids:
            # Ne forcer que les IDs qui sont dans target_ids et présents dans le groupe
            valid_group_ids = [rid for rid in group_ids if rid in target_ids]
            if valid_group_ids:
                force = valid_group_ids[:batch_size]
                print(f"   📋 IDs dans ce groupe: {force}")
        
        stories = generate_from_page_group(
            agent=agent,
            ctx=ctx,
            page_text=group_text,
            nb_us=batch_size,
            roles=ctx['roles'],
            offset=offset,
            doc_type=ctx['type'],
            force_ids=force
        )
        
        print(f"   → {len(stories)} US generated")
        all_stories.extend(stories)
        offset += batch_size

    # 6. Traitement final
    if all_stories:
        print(f"\n   ✅ Total: {len(all_stories)} US generated")
        
        print("\n🔍 Filtering to valid IDs...")
        if use_force_ids and target_ids:
            all_stories = filter_to_valid_ids(all_stories, target_ids)
        
        print("\n🔗 Reconciling missing IDs...")
        if use_force_ids and target_ids:
            all_stories = reconcile_missing_ids(
                agent, ctx, raw_text, all_stories, target_ids, ctx['type']
            )
        
        print("\n👤 Distributing roles...")
        all_stories = distribute_roles(all_stories, ctx['type'])
        
        print("\n🧹 Cleaning up...")
        all_stories = deduplicate(all_stories)
        all_stories = renumber(all_stories)

        final_count = len(all_stories)
        print(f"\n✅ {final_count} user stories generated")
        
        covered = [us.get("requirement_id") for us in all_stories if us.get("requirement_id")]
        if covered:
            print(f"   📋 Covered IDs: {sorted(covered)}")
        
        if use_force_ids and target_ids:
            covered_set = {rid.lower().replace(" ", "") for rid in covered}
            missing = [rid for rid in target_ids if rid.lower().replace(" ", "") not in covered_set]
            if missing:
                print(f"   ⚠️ Missing IDs: {missing[:10]}...")
            else:
                print(f"   ✅ All {len(target_ids)} requirements covered!")
        
        roles_used = list(set([us.get("as_a") for us in all_stories]))
        print(f"   👤 Roles used: {sorted(roles_used)}")
        
        return format_user_stories(all_stories), all_stories

    print("⚠️ No stories generated")
    return "", []