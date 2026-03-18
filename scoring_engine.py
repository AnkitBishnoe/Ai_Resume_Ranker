import logging
import re
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# REAL-WORLD KEYWORD TAXONOMY
# Used to detect and categorize keywords from resumes and job descriptions.
# Categories: degrees, experience levels, certifications, hard skills, soft
# skills, tools/platforms, domain knowledge, and job-function signals.
# ─────────────────────────────────────────────────────────────────────────────

# ── Degree / Education ───────────────────────────────────────────────────────
DEGREE_KEYWORDS = {
    # Undergraduate
    "bachelor", "b.tech", "b.e", "b.sc", "b.s", "b.a", "b.com", "bba",
    "undergraduate", "ug",
    # Postgraduate
    "master", "m.tech", "m.e", "m.sc", "m.s", "m.a", "mba", "pgdm", "pg",
    "postgraduate", "mca",
    # Doctoral
    "phd", "ph.d", "doctorate", "doctoral",
    # Diplomas
    "diploma", "certification course", "bootcamp",
    # Fields
    "computer science", "information technology", "software engineering",
    "electrical engineering", "mechanical engineering", "data science",
    "statistics", "mathematics", "finance", "economics", "business administration",
}

# ── Experience / Seniority Level ─────────────────────────────────────────────
EXPERIENCE_LEVEL_KEYWORDS = {
    # Numeric
    "0-1 years", "1+ years", "2+ years", "3+ years", "4+ years", "5+ years",
    "6+ years", "7+ years", "8+ years", "10+ years",
    # Qualitative
    "fresher", "entry level", "junior", "associate", "mid-level", "mid level",
    "senior", "lead", "staff", "principal", "architect", "head of",
    "director", "vp", "vice president", "c-level", "cto", "ceo", "coo",
    # Experience tokens
    "years of experience", "years experience", "work experience",
    "hands-on experience", "industry experience", "proven experience",
}

# ── Certifications / Credentials ─────────────────────────────────────────────
CERTIFICATION_KEYWORDS = {
    # Cloud
    "aws certified", "aws solutions architect", "aws developer", "aws devops",
    "gcp certified", "google cloud certified", "azure certified",
    "azure administrator", "azure developer",
    # DevOps / Infra
    "cka", "ckad", "kubernetes certified", "docker certified", "terraform associate",
    # Security
    "cissp", "ceh", "comptia security+", "comptia network+", "oscp",
    # Data / AI
    "google data analytics", "tensorflow developer", "databricks certified",
    "tableau desktop specialist", "power bi certified",
    # Agile / PM
    "pmp", "prince2", "csm", "certified scrum master", "psm", "safe",
    "agile certified", "itil",
    # Networking
    "ccna", "ccnp", "cisco certified",
    # Finance
    "cfa", "cpa", "ca", "chartered accountant", "frm",
    # General
    "certified", "certification", "licensed",
}

# ── Programming Languages ─────────────────────────────────────────────────────
PROGRAMMING_LANGUAGE_KEYWORDS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "bash", "shell", "powershell", "sql", "plsql",
    "dart", "elixir", "haskell", "lua", "groovy", "vba", "assembly",
}

# ── Frameworks & Libraries ────────────────────────────────────────────────────
FRAMEWORK_KEYWORDS = {
    # Backend
    "django", "flask", "fastapi", "spring", "spring boot", "express",
    "nestjs", "laravel", "rails", "ruby on rails", "asp.net", ".net core",
    "node.js", "nodejs", "quarkus", "micronaut",
    # Frontend
    "react", "next.js", "nextjs", "vue", "vue.js", "angular", "svelte",
    "nuxt", "gatsby", "jquery", "bootstrap", "tailwind", "material ui",
    # Mobile
    "react native", "flutter", "ionic", "xamarin", "android sdk", "ios sdk",
    # Data / ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost",
    "lightgbm", "hugging face", "transformers", "spacy", "nltk", "opencv",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    # Testing
    "jest", "pytest", "junit", "selenium", "cypress", "playwright",
    "mocha", "chai", "testng",
}

# ── Cloud & Infrastructure ────────────────────────────────────────────────────
CLOUD_INFRA_KEYWORDS = {
    # Cloud providers
    "aws", "gcp", "google cloud", "azure", "alibaba cloud", "digitalocean",
    "heroku", "vercel", "netlify",
    # Services
    "ec2", "s3", "rds", "lambda", "ecs", "eks", "sqs", "sns", "cloudwatch",
    "cloud functions", "bigquery", "cloud run", "app engine",
    # Containers & Orchestration
    "docker", "kubernetes", "k8s", "helm", "openshift",
    # IaC
    "terraform", "ansible", "puppet", "chef", "cloudformation",
    # CI/CD
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "argo cd", "spinnaker", "bamboo",
    # Monitoring
    "prometheus", "grafana", "datadog", "new relic", "splunk", "elk",
    "elasticsearch", "logstash", "kibana",
}

# ── Databases ─────────────────────────────────────────────────────────────────
DATABASE_KEYWORDS = {
    "mysql", "postgresql", "postgres", "sqlite", "oracle", "sql server",
    "mssql", "mariadb", "mongodb", "cassandra", "redis", "dynamodb",
    "firestore", "couchdb", "neo4j", "hbase", "influxdb", "snowflake",
    "bigquery", "redshift", "databricks", "delta lake",
}

# ── Data Engineering & Analytics ─────────────────────────────────────────────
DATA_KEYWORDS = {
    "data pipeline", "etl", "elt", "data warehouse", "data lake",
    "data lakehouse", "spark", "apache spark", "kafka", "airflow",
    "dbt", "hadoop", "hive", "flink", "data modeling", "star schema",
    "data governance", "data quality", "data lineage",
    "tableau", "power bi", "looker", "metabase", "superset",
    "excel", "google sheets", "pivot tables",
}

# ── AI / ML Domain ────────────────────────────────────────────────────────────
AI_ML_KEYWORDS = {
    "machine learning", "deep learning", "neural network", "nlp",
    "natural language processing", "computer vision", "reinforcement learning",
    "generative ai", "llm", "large language model", "gpt", "bert",
    "rag", "retrieval augmented generation", "fine-tuning", "prompt engineering",
    "mlops", "feature engineering", "model deployment", "a/b testing",
    "recommendation system", "time series", "anomaly detection",
    "classification", "regression", "clustering", "random forest",
    "gradient boosting", "transfer learning",
}

# ── Security ──────────────────────────────────────────────────────────────────
SECURITY_KEYWORDS = {
    "penetration testing", "pen testing", "vulnerability assessment",
    "sast", "dast", "siem", "iam", "rbac", "oauth", "jwt", "ssl", "tls",
    "encryption", "zero trust", "devsecops", "soc", "incident response",
    "threat modeling", "owasp", "firewall", "intrusion detection",
}

# ── Soft / Interpersonal Skills ───────────────────────────────────────────────
SOFT_SKILL_KEYWORDS = {
    "communication", "leadership", "teamwork", "collaboration",
    "problem solving", "critical thinking", "adaptability", "time management",
    "project management", "stakeholder management", "mentoring", "coaching",
    "negotiation", "presentation", "analytical", "detail-oriented",
    "self-motivated", "proactive", "cross-functional",
}

# ── Project Management & Methodologies ───────────────────────────────────────
METHODOLOGY_KEYWORDS = {
    "agile", "scrum", "kanban", "waterfall", "lean", "safe",
    "devops", "gitops", "ci/cd", "tdd", "bdd", "ddd",
    "microservices", "monolith", "serverless", "event-driven",
    "rest", "restful", "graphql", "grpc", "soap", "websocket",
    "api design", "system design", "low-level design", "high-level design",
    "design patterns", "solid principles", "clean architecture",
}

# ── Version Control & Collaboration ──────────────────────────────────────────
TOOLING_KEYWORDS = {
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "trello", "notion", "slack", "figma", "postman", "swagger",
    "linux", "unix", "macos", "windows server",
}

# ── Domain / Industry Knowledge ──────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    # Finance / Fintech
    "fintech", "banking", "payments", "risk management", "compliance",
    "blockchain", "cryptocurrency", "trading systems",
    # Healthcare
    "healthcare", "ehr", "hl7", "fhir", "hipaa", "medical imaging",
    # E-Commerce
    "e-commerce", "retail", "supply chain", "inventory management",
    # HR / Recruitment
    "hris", "ats", "payroll", "talent acquisition",
    # Marketing
    "seo", "sem", "crm", "salesforce", "hubspot", "google analytics",
    "digital marketing", "growth hacking",
    # Legal / Compliance
    "gdpr", "pci-dss", "sox", "iso 27001",
}

# ── Master keyword pool (tagged by category) ─────────────────────────────────
KEYWORD_TAXONOMY = {
    "degree":          DEGREE_KEYWORDS,
    "experience":      EXPERIENCE_LEVEL_KEYWORDS,
    "certification":   CERTIFICATION_KEYWORDS,
    "language":        PROGRAMMING_LANGUAGE_KEYWORDS,
    "framework":       FRAMEWORK_KEYWORDS,
    "cloud_infra":     CLOUD_INFRA_KEYWORDS,
    "database":        DATABASE_KEYWORDS,
    "data":            DATA_KEYWORDS,
    "ai_ml":           AI_ML_KEYWORDS,
    "security":        SECURITY_KEYWORDS,
    "soft_skill":      SOFT_SKILL_KEYWORDS,
    "methodology":     METHODOLOGY_KEYWORDS,
    "tooling":         TOOLING_KEYWORDS,
    "domain":          DOMAIN_KEYWORDS,
}

# Flat set for fast membership check
ALL_KNOWN_KEYWORDS: set = set()
for _cat_keywords in KEYWORD_TAXONOMY.values():
    ALL_KNOWN_KEYWORDS.update(_cat_keywords)


# ─────────────────────────────────────────────────────────────────────────────
# Model bootstrap (semantic similarity, optional)
# ─────────────────────────────────────────────────────────────────────────────
_USE_ADVANCED = False
_embedder = None
_kw_model = None

try:
    from sentence_transformers import SentenceTransformer, util
    from keybert import KeyBERT
    import torch

    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _kw_model = KeyBERT(model=_embedder)
    _USE_ADVANCED = True
    logger.info("Advanced semantic models loaded successfully.")
except Exception as e:
    logger.warning(f"Advanced models failed to load: {e}. Falling back to TF-IDF.")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
    return " ".join(text.split())


def _extract_taxonomy_keywords(text: str) -> set:
    """
    Scan text against the full real-world taxonomy and return every keyword
    that appears in the text.  Multi-word phrases are checked via substring
    match so 'machine learning engineer' will match 'machine learning'.
    """
    text_lower = text.lower()
    found = set()
    for keyword in ALL_KNOWN_KEYWORDS:
        # Use word-boundary-aware matching for single words,
        # substring match is fine for multi-word phrases.
        if len(keyword.split()) == 1:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found.add(keyword)
        else:
            if keyword in text_lower:
                found.add(keyword)
    return found


def _extract_tfidf_keywords(text: str, top_n: int = 15) -> set:
    """
    Extract top TF-IDF n-gram tokens from a single document by fitting on
    that document alone and taking the highest-score features.
    """
    try:
        tfidf = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=top_n * 3,
            sublinear_tf=True,
        )
        tfidf.fit([text])
        return set(tfidf.get_feature_names_out())
    except Exception as e:
        logger.error(f"TF-IDF extraction failed: {e}")
        return set()


def _label_keyword(kw: str) -> str:
    """Return a human-readable category label for a keyword."""
    for cat, keywords in KEYWORD_TAXONOMY.items():
        if kw in keywords:
            label_map = {
                "degree": "🎓 Education",
                "experience": "📅 Experience",
                "certification": "🏅 Certification",
                "language": "💻 Language",
                "framework": "🔧 Framework",
                "cloud_infra": "☁️ Cloud/Infra",
                "database": "🗄️ Database",
                "data": "📊 Data",
                "ai_ml": "🤖 AI/ML",
                "security": "🔒 Security",
                "soft_skill": "🤝 Soft Skill",
                "methodology": "📐 Methodology",
                "tooling": "🛠️ Tooling",
                "domain": "🏢 Domain",
            }
            return label_map.get(cat, cat)
    return "🔑 General"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def calculate_similarity_score(resume_text: str, job_description: str) -> float:
    """
    Calculates ATS similarity score.
    Formula: min(((Semantic Score * 0.5) + (Keyword Match % * 0.5)) + 33, 100)
    """
    if not resume_text or not job_description:
        return 0.0

    semantic_score = 0.0
    if _USE_ADVANCED:
        try:
            resume_emb = _embedder.encode(resume_text, convert_to_tensor=True)
            jd_emb = _embedder.encode(job_description, convert_to_tensor=True)
            semantic_score = util.cos_sim(resume_emb, jd_emb).item() * 100
        except Exception as e:
            logger.error(f"Advanced similarity calculation failed: {e}")

    # Fallback/Combine with TF-IDF if advanced failed or as a secondary measure
    if semantic_score == 0:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            tfidf = TfidfVectorizer(stop_words='english')
            matrix = tfidf.fit_transform([resume_text, job_description])
            semantic_score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100
        except Exception as e:
            logger.error(f"Fallback similarity calculation failed: {e}")

    # ── Keyword Match Component ──
    gap = get_keyword_gap(resume_text, job_description)
    matched_count = len(gap["matched"])
    missing_count = len(gap["missing"])
    
    total_relevant = matched_count + missing_count
    keyword_score = (matched_count / total_relevant * 100) if total_relevant > 0 else 0.0

    # ── Final Weighted Base Score (50/50 split) ──
    base_score = (semantic_score * 0.5) + (keyword_score * 0.5)
    
    # ── Add 33% Boost & Cap at 100 ──
    final_score = min(base_score + 33, 100.0)
    
    return round(final_score, 2)


def get_keyword_gap(resume_text: str, job_description: str, top_n: int = 10) -> dict:
    """
    Real-world keyword gap analysis.

    Strategy (layered):
    1. Taxonomy scan — match against curated real-world keyword library
       (degrees, experience levels, certs, skills, tools, domains, etc.)
    2. Semantic/TF-IDF augmentation — for domain-specific terms not in the
       taxonomy that appear in the JD, check if they're in the resume.
    3. Deduplicate & rank by category importance.

    Returns
    -------
    {
        "matched": [list of keywords in both resume and JD],
        "missing": [list of JD keywords absent from resume],
        "categorized_matched": {category: [kws]},
        "categorized_missing": {category: [kws]},
    }
    """
    if not resume_text or not job_description:
        return {"matched": [], "missing": [], "categorized_matched": {}, "categorized_missing": {}}

    # ── Step 1: Taxonomy-based extraction ────────────────────────────────────
    jd_taxonomy_kws    = _extract_taxonomy_keywords(job_description)
    resume_taxonomy_kws = _extract_taxonomy_keywords(resume_text)

    taxonomy_matched = jd_taxonomy_kws & resume_taxonomy_kws
    taxonomy_missing = jd_taxonomy_kws - resume_taxonomy_kws

    # ── Step 2: Semantic / TF-IDF augmentation for non-taxonomy terms ─────────
    extra_jd_kws = set()
    if _USE_ADVANCED and _kw_model:
        try:
            raw = _kw_model.extract_keywords(
                job_description,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n + 5,
                use_mmr=True,
                diversity=0.5,
            )
            extra_jd_kws = {kw.lower() for kw, _ in raw}
        except Exception as e:
            logger.warning(f"KeyBERT extraction failed: {e}")
    
    if not extra_jd_kws:
        extra_jd_kws = _extract_tfidf_keywords(job_description, top_n=top_n + 5)

    # Filter out terms already covered by taxonomy
    extra_jd_kws -= ALL_KNOWN_KEYWORDS

    resume_text_lower = resume_text.lower()
    for kw in extra_jd_kws:
        if kw in jd_taxonomy_kws:
            continue  # already covered
        if kw in resume_text_lower:
            taxonomy_matched.add(kw)
        else:
            taxonomy_missing.add(kw)

    # ── Step 3: Prioritise — put higher-signal categories first ──────────────
    PRIORITY_ORDER = [
        "certification", "language", "framework", "cloud_infra",
        "database", "ai_ml", "data", "security", "methodology",
        "tooling", "domain", "experience", "degree", "soft_skill",
    ]

    def sort_key(kw: str):
        for i, cat in enumerate(PRIORITY_ORDER):
            if kw in KEYWORD_TAXONOMY.get(cat, set()):
                return i
        return len(PRIORITY_ORDER)  # unknown terms go last

    sorted_matched = sorted(taxonomy_matched, key=sort_key)
    sorted_missing = sorted(taxonomy_missing, key=sort_key)

    # ── Step 4: Build categorized views ──────────────────────────────────────
    def categorize(kw_list):
        cat_dict = {}
        for kw in kw_list:
            label = _label_keyword(kw)
            cat_dict.setdefault(label, []).append(kw)
        return cat_dict

    return {
        "matched": sorted_matched[:top_n],
        "missing": sorted_missing[:top_n],
        "categorized_matched": categorize(sorted_matched[:top_n]),
        "categorized_missing": categorize(sorted_missing[:top_n]),
    }
