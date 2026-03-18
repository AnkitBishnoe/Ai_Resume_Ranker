import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_USE_ADVANCED = False
_embedder = None

try:
    from sentence_transformers import SentenceTransformer, util
    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _USE_ADVANCED = True
except Exception as e:
    logger.warning(f"Jobs DB: Advanced models failed: {e}. Using TF-IDF fallback.")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────────────────────────────────────
# REAL-WORLD JOB DATABASE
# Every entry mirrors what recruiters actually put in JDs:
#   • seniority / experience level
#   • required degree / education
#   • certifications preferred
#   • hard skills (languages, frameworks, tools)
#   • soft skills & methodologies
#   • domain context
# ─────────────────────────────────────────────────────────────────────────────
MOCK_JOBS_DB = [
    {
        "title": "Senior Python Backend Engineer",
        "tags": "python, django, fastapi, postgresql, redis, docker, kubernetes, aws, rest api, microservices, senior",
        "description": (
            "We are looking for a Senior Python Backend Engineer with 5+ years of experience building "
            "scalable backend systems. Requirements: Bachelor's or Master's in Computer Science or "
            "Information Technology. Strong expertise in Python, Django, FastAPI, and RESTful API design. "
            "Proficiency with PostgreSQL, Redis, Docker, and Kubernetes. Experience with AWS (EC2, S3, RDS, Lambda). "
            "Familiarity with CI/CD pipelines using GitHub Actions or Jenkins. "
            "Solid understanding of microservices architecture, system design, and SOLID principles. "
            "AWS Certified Developer or Solutions Architect is a plus. "
            "Excellent communication skills and experience working in an Agile/Scrum team."
        ),
    },
    {
        "title": "Frontend Developer (React / TypeScript)",
        "tags": "react, typescript, javascript, next.js, tailwind, html, css, figma, jest, agile, junior, mid-level",
        "description": (
            "Seeking a Frontend Developer with 2+ years of experience in modern web development. "
            "Bachelor's degree in Computer Science or a related field preferred. "
            "Hands-on experience with React, TypeScript, and Next.js. "
            "Proficiency in HTML5, CSS3, and Tailwind CSS. "
            "Familiarity with Figma for design-to-code workflows. "
            "Experience writing unit tests with Jest and integration tests with Cypress or Playwright. "
            "Understanding of web performance optimisation, accessibility (WCAG), and responsive design. "
            "Experience with Git, GitHub, and Agile methodologies."
        ),
    },
    {
        "title": "Data Scientist (ML / NLP)",
        "tags": "python, machine learning, nlp, deep learning, tensorflow, pytorch, scikit-learn, sql, pandas, mlops, master, phd",
        "description": (
            "Looking for a Data Scientist with 3+ years of experience in applied machine learning. "
            "Master's or PhD in Data Science, Statistics, Computer Science, or Mathematics preferred. "
            "Strong programming skills in Python; proficiency in pandas, NumPy, scikit-learn, TensorFlow, and PyTorch. "
            "Experience with NLP techniques (BERT, transformers, text classification, NER). "
            "Solid knowledge of SQL and experience with data warehouses such as Snowflake or BigQuery. "
            "Familiarity with MLOps tools (MLflow, Airflow, Kubeflow). "
            "Experience deploying models to production using Docker and Kubernetes. "
            "Strong analytical and communication skills for presenting insights to non-technical stakeholders."
        ),
    },
    {
        "title": "DevOps / Site Reliability Engineer",
        "tags": "aws, azure, kubernetes, docker, terraform, ansible, ci/cd, jenkins, github actions, linux, prometheus, grafana, senior, devops",
        "description": (
            "We need a Senior DevOps / SRE with 5+ years of experience in cloud infrastructure and automation. "
            "Bachelor's degree in Computer Science, IT, or Electrical Engineering. "
            "Deep expertise in AWS or Azure; hands-on with Kubernetes (CKA certification preferred), Docker, and Helm. "
            "Infrastructure-as-Code experience with Terraform and Ansible. "
            "CI/CD pipeline implementation using Jenkins, GitHub Actions, or GitLab CI. "
            "Monitoring and observability with Prometheus, Grafana, Datadog, or ELK stack. "
            "Strong Linux/Unix administration skills. "
            "Experience with incident response, on-call rotations, and SLA management. "
            "AWS Certified DevOps Engineer or equivalent is a strong plus."
        ),
    },
    {
        "title": "Product Manager – SaaS Platform",
        "tags": "product management, agile, scrum, roadmapping, user stories, jira, a/b testing, analytics, stakeholder management, mba",
        "description": (
            "Hiring a Product Manager with 4+ years of experience in SaaS product development. "
            "Bachelor's degree required; MBA or PMP certification preferred. "
            "Proven track record of defining product vision, writing user stories, and managing roadmaps. "
            "Experience running A/B tests, analysing product analytics (Mixpanel, Amplitude, Google Analytics). "
            "Strong stakeholder management and cross-functional collaboration skills. "
            "Proficiency with Jira, Confluence, and product discovery frameworks (Design Thinking, Jobs-to-be-Done). "
            "Excellent communication, negotiation, and presentation skills. "
            "CSM (Certified Scrum Master) or SAFe certification is a plus."
        ),
    },
    {
        "title": "UI/UX Designer",
        "tags": "figma, user research, wireframing, prototyping, usability testing, design systems, sketch, adobe xd, typography, mid-level",
        "description": (
            "Looking for a UI/UX Designer with 3+ years of experience in product design. "
            "Bachelor's degree in Design, HCI, or a related field. "
            "Expert-level proficiency in Figma; experience with Sketch and Adobe XD. "
            "Strong portfolio demonstrating end-to-end design process: user research, wireframing, prototyping, and usability testing. "
            "Experience building and maintaining design systems. "
            "Knowledge of accessibility standards (WCAG 2.1). "
            "Ability to collaborate closely with frontend developers and product managers. "
            "Strong communication, presentation, and problem-solving skills."
        ),
    },
    {
        "title": "Machine Learning Engineer",
        "tags": "python, mlops, tensorflow, pytorch, kubernetes, docker, feature engineering, model deployment, aws, ci/cd, senior, machine learning",
        "description": (
            "Seeking an ML Engineer with 4+ years of experience taking models from research to production. "
            "Master's degree in Computer Science, AI, or Data Science preferred. "
            "Proficient in Python; deep expertise in TensorFlow, PyTorch, and scikit-learn. "
            "Hands-on MLOps experience: model versioning (MLflow), pipeline orchestration (Airflow, Kubeflow), "
            "and serving (TorchServe, TF Serving, Triton). "
            "Strong skills in feature engineering, data preprocessing, and experiment tracking. "
            "Experience deploying containerised ML workloads on Kubernetes (AWS EKS or GKE). "
            "TensorFlow Developer Certificate or AWS ML Specialty certification is a strong plus. "
            "Experience with LLMs, RAG pipelines, and prompt engineering is highly desirable."
        ),
    },
    {
        "title": "Backend Engineer (Node.js / GraphQL)",
        "tags": "node.js, typescript, graphql, postgresql, mongodb, redis, docker, aws, rest api, microservices, mid-level",
        "description": (
            "We are hiring a Backend Engineer with 3+ years of experience in Node.js development. "
            "Bachelor's degree in Computer Science or related field. "
            "Strong proficiency in Node.js, TypeScript, Express, and NestJS. "
            "Experience designing GraphQL APIs and RESTful services. "
            "Database skills across PostgreSQL, MongoDB, and Redis. "
            "Familiarity with Docker, AWS (EC2, S3, SQS), and CI/CD workflows. "
            "Understanding of microservices, event-driven architecture, and message queues (Kafka, RabbitMQ). "
            "Experience with unit and integration testing (Jest, Mocha). "
            "Strong collaboration skills and comfort working in an Agile environment."
        ),
    },
    {
        "title": "Full Stack Developer (Python + React)",
        "tags": "python, react, javascript, typescript, django, fastapi, postgresql, docker, aws, git, agile, mid-level",
        "description": (
            "Looking for a Full Stack Developer with 3+ years of full-stack development experience. "
            "Bachelor's in Computer Science or Information Technology. "
            "Backend: Python, Django or FastAPI, REST API design, PostgreSQL, Redis. "
            "Frontend: React, TypeScript, HTML5, CSS3. "
            "DevOps basics: Docker, AWS (S3, EC2), GitHub Actions. "
            "Familiarity with Agile/Scrum, Git workflow, code review practices. "
            "Strong problem-solving, communication, and time management skills."
        ),
    },
    {
        "title": "Cybersecurity Analyst",
        "tags": "penetration testing, siem, soc, vulnerability assessment, owasp, cissp, ceh, aws, linux, incident response, senior",
        "description": (
            "We are seeking a Cybersecurity Analyst with 5+ years of experience in information security. "
            "Bachelor's degree in Cybersecurity, Computer Science, or IT. "
            "CISSP, CEH, or CompTIA Security+ certification required. "
            "Hands-on experience with SIEM platforms (Splunk, IBM QRadar), IDS/IPS, and firewall management. "
            "Proficiency in penetration testing and vulnerability assessment tools (Nessus, Metasploit, Burp Suite). "
            "Knowledge of OWASP Top 10, GDPR, ISO 27001, and PCI-DSS compliance. "
            "Experience with incident response, threat modelling, and forensics. "
            "Strong Linux/Unix skills and scripting ability (Python or Bash)."
        ),
    },
    {
        "title": "Data Engineer",
        "tags": "python, sql, spark, kafka, airflow, dbt, snowflake, aws, bigquery, etl, data pipeline, mid-level, senior",
        "description": (
            "Hiring a Data Engineer with 4+ years of experience building data infrastructure. "
            "Bachelor's or Master's degree in Computer Science, Statistics, or a related field. "
            "Strong Python and SQL skills. "
            "Experience building ETL/ELT pipelines using Apache Spark, Kafka, and Airflow. "
            "Proficiency with cloud data warehouses: Snowflake, BigQuery, or AWS Redshift. "
            "Experience with dbt for data transformation and data modelling (star schema, data vault). "
            "Familiarity with AWS (S3, Glue, Lambda) or GCP data services. "
            "AWS Certified Data Analytics or Google Professional Data Engineer is a plus. "
            "Excellent attention to detail and strong analytical skills."
        ),
    },
    {
        "title": "Android Developer (Kotlin)",
        "tags": "kotlin, android, jetpack compose, mvvm, rest api, sqlite, firebase, git, java, mid-level",
        "description": (
            "Seeking an Android Developer with 3+ years of native Android development experience. "
            "Bachelor's degree in Computer Science or equivalent practical experience. "
            "Proficiency in Kotlin (and Java); strong knowledge of Android SDK and Jetpack libraries. "
            "Experience with Jetpack Compose for modern UI development. "
            "Knowledge of MVVM/MVI architecture patterns, LiveData, and ViewModel. "
            "Integration with RESTful APIs and experience with Firebase (Auth, Firestore, Crashlytics). "
            "Familiarity with SQLite and Room database. "
            "Experience with CI/CD for mobile using GitHub Actions or Bitrise. "
            "Google Associate Android Developer certification is a plus."
        ),
    },
]


def suggest_jobs(resume_text: str, top_n: int = 4) -> list:
    """Suggests jobs matched to the resume using semantic or TF-IDF similarity."""
    if not resume_text:
        return []

    scored = []

    if _USE_ADVANCED:
        try:
            from sentence_transformers import util
            resume_emb = _embedder.encode(resume_text, convert_to_tensor=True)
            for job in MOCK_JOBS_DB:
                job_text = f"{job['title']} {job.get('tags', '')} {job['description']}"
                job_emb = _embedder.encode(job_text, convert_to_tensor=True)
                score = (util.cos_sim(resume_emb, job_emb).item() * 100) + 33
                score = min(100.0, score)
                if score >= 33:
                    scored.append({**job, "match_score": round(score, 1)})
        except Exception as e:
            logger.error(f"Advanced job suggestion failed: {e}")

    if not scored:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            tfidf = TfidfVectorizer(stop_words='english')
            job_texts = [f"{j['title']} {j.get('tags', '')} {j['description']}" for j in MOCK_JOBS_DB]
            tfidf_matrix = tfidf.fit_transform([resume_text] + job_texts)
            resume_vec = tfidf_matrix[0:1]
            job_vecs = tfidf_matrix[1:]
            similarities = cosine_similarity(resume_vec, job_vecs)[0]
            for i, score in enumerate(similarities):
                score_val = (score * 110) + 33
                score_val = min(100.0, score_val)
                if score_val >= 33:
                    scored.append({**MOCK_JOBS_DB[i], "match_score": round(score_val, 1)})
        except Exception as e:
            logger.error(f"Fallback job suggestion failed: {e}")

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:top_n]
