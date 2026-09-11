"""
Smart Water Usage Advisor - Phase 1 Automated Validation Suite
Tests project structure, documentation completeness, database schema naming consistency,
diagram presence, and scope compliance against project requirements.
"""

import os
import sys
import json

def run_checks():
    failures = []
    passes = []

    print("==================================================")
    print("RUNNING PHASE 1 VALIDATION SUITE")
    print("==================================================")

    # 1. Unrelated File Removal Check
    if os.path.exists("antigravity_research_program.md"):
        failures.append("TC-P1-01 FAIL: antigravity_research_program.md still exists in workspace.")
    else:
        passes.append("TC-P1-01 PASS: Unrelated antigravity file is absent.")

    # 2. Canonical Directory Structure Check
    required_dirs = [
        "1_DOCUMENTATION",
        "2_RESEARCH_DATA/water_usage_data",
        "2_RESEARCH_DATA/research_papers",
        "3_DESIGN/wireframes",
        "3_DESIGN/user_flow",
        "3_DESIGN/design_documents",
        "3_DESIGN/personas",
        "4_DEVELOPMENT/backend",
        "4_DEVELOPMENT/frontend",
        "4_DEVELOPMENT/data",
        "4_DEVELOPMENT/notebooks",
        "4_DEVELOPMENT/utils",
        "5_AI_COMPONENTS/prompt_engineering",
        "5_AI_COMPONENTS/chatbot_logic",
        "5_AI_COMPONENTS/predictive_models",
        "5_AI_COMPONENTS/anomaly_detection",
        "6_TESTING/unit_tests",
        "6_TESTING/integration_tests",
        "6_TESTING/user_testing",
        "6_TESTING/performance_metrics",
        "7_ETHICS_COMPLIANCE",
        "8_DEPLOYMENT",
        "9_PRESENTATION",
        "10_APPENDICES"
    ]
    for d in required_dirs:
        if not os.path.isdir(d):
            failures.append(f"TC-P1-02 FAIL: Missing canonical directory: {d}")
    if not failures:
        passes.append("TC-P1-02 PASS: All canonical directories exist.")

    # 3. Core Root Files Check
    root_files = [".gitignore", ".env.example", "README.md", "LICENSE", "CONTRIBUTING.md"]
    for f in root_files:
        if not os.path.isfile(f):
            failures.append(f"TC-P1-03 FAIL: Missing root file: {f}")
    if not any("TC-P1-03" in f for f in failures):
        passes.append("TC-P1-03 PASS: All core root files exist.")

    # Check that .env does NOT exist (no real secrets committed)
    if os.path.isfile(".env"):
        failures.append("TC-P1-03 FAIL: .env file found in workspace! Real secrets must not be stored in repository.")
    else:
        passes.append("TC-P1-03b PASS: No real .env secrets committed.")

    # 4. Documentation Completeness Check
    doc_files = [
        "1_DOCUMENTATION/01_Project_Charter.md",
        "1_DOCUMENTATION/02_Problem_Statement.md",
        "1_DOCUMENTATION/03_User_Research.md",
        "1_DOCUMENTATION/04_Literature_Review.md",
        "1_DOCUMENTATION/05_Responsible_AI_Framework.md",
        "1_DOCUMENTATION/06_Glossary_Terms.md",
        "1_DOCUMENTATION/07_Technical_Decisions.md",
        "2_RESEARCH_DATA/data_plan_and_dictionary.md",
        "2_RESEARCH_DATA/case_studies.md"
    ]
    for f in doc_files:
        if not os.path.isfile(f):
            failures.append(f"TC-P1-04 FAIL: Missing documentation file: {f}")
    if not any("TC-P1-04" in f for f in failures):
        passes.append("TC-P1-04 PASS: All 1_DOCUMENTATION and 2_RESEARCH_DATA files exist.")

    # 5. Personas Check
    persona_files = [
        "3_DESIGN/personas/Persona_1_HomeOwner.md",
        "3_DESIGN/personas/Persona_2_Facility_Manager.md",
        "3_DESIGN/personas/Persona_3_Municipality.md"
    ]
    for f in persona_files:
        if not os.path.isfile(f):
            failures.append(f"TC-P1-05 FAIL: Missing persona file: {f}")
    if not any("TC-P1-05" in f for f in failures):
        passes.append("TC-P1-05 PASS: All 3 core personas exist.")

    # 6. Diagram PNGs Check
    diagram_files = [
        "3_DESIGN/user_flow/system_architecture.png",
        "3_DESIGN/user_flow/data_flow_diagram.png",
        "3_DESIGN/user_flow/ai_workflow_diagram.png",
        "3_DESIGN/user_flow/user_journey_map.png"
    ]
    for f in diagram_files:
        if not os.path.isfile(f) or os.path.getsize(f) == 0:
            failures.append(f"TC-P1-06 FAIL: Missing or empty diagram PNG: {f}")
    if not any("TC-P1-06" in f for f in failures):
        passes.append("TC-P1-06 PASS: All 4 visual architecture diagram PNGs exist and have non-zero size.")

    # 7. Wireframes Check
    wireframe_files = [
        "3_DESIGN/wireframes/01_dashboard_wireframe.md",
        "3_DESIGN/wireframes/02_chatbot_wireframe.md",
        "3_DESIGN/wireframes/03_recommendations_wireframe.md"
    ]
    for f in wireframe_files:
        if not os.path.isfile(f):
            failures.append(f"TC-P1-07 FAIL: Missing wireframe file: {f}")
    if not any("TC-P1-07" in f for f in failures):
        passes.append("TC-P1-07 PASS: All 3 wireframes exist.")

    # 8. Database Schema Naming Consistency Check
    db_schema_path = "3_DESIGN/design_documents/Database_Schema.md"
    if not os.path.isfile(db_schema_path):
        failures.append(f"TC-P1-08 FAIL: Missing {db_schema_path}")
    else:
        with open(db_schema_path, "r", encoding="utf-8") as f:
            content = f.read()
        canonical_tables = [
            "users", "user_profiles", "meters", "water_usage_data",
            "predictions", "anomalies", "alerts", "consumption_categories",
            "recommendations", "goals", "feedback", "chatbot_conversations"
        ]
        for tbl in canonical_tables:
            if tbl not in content:
                failures.append(f"TC-P1-08 FAIL: Database schema document missing canonical table '{tbl}'")
        if not any("TC-P1-08" in f for f in failures):
            passes.append("TC-P1-08 PASS: Database schema strictly adheres to all 12 canonical table names.")

    # 9. AI Planning & JSON Validation
    ai_files = [
        "3_DESIGN/design_documents/Chatbot_Conversation_Flow.md",
        "5_AI_COMPONENTS/prompt_engineering/system_prompts.txt",
        "5_AI_COMPONENTS/prompt_engineering/prompt_templates.txt",
        "5_AI_COMPONENTS/prompt_engineering/example_conversations.md",
        "5_AI_COMPONENTS/prompt_engineering/rag_knowledge_base.json"
    ]
    for f in ai_files:
        if not os.path.isfile(f):
            failures.append(f"TC-P1-09 FAIL: Missing AI component file: {f}")
    
    # Check rag_knowledge_base.json is valid JSON
    rag_path = "5_AI_COMPONENTS/prompt_engineering/rag_knowledge_base.json"
    if os.path.isfile(rag_path):
        try:
            with open(rag_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list) or len(data) == 0:
                    failures.append("TC-P1-09 FAIL: rag_knowledge_base.json is empty or not a list.")
        except Exception as e:
            failures.append(f"TC-P1-09 FAIL: rag_knowledge_base.json is invalid JSON: {e}")
    if not any("TC-P1-09" in f for f in failures):
        passes.append("TC-P1-09 PASS: AI conversation flows, prompts, and valid RAG knowledge base exist.")

    # 10. Scope Compliance (No premature Phase 2-6 production code)
    premature_files = [
        "4_DEVELOPMENT/backend/app.py",
        "4_DEVELOPMENT/data/telemetry_data.csv",
        "Dockerfile",
        "docker-compose.yml"
    ]
    for pf in premature_files:
        if os.path.isfile(pf):
            failures.append(f"TC-P1-10 FAIL: Premature implementation file found: {pf}")
    if not any("TC-P1-10" in f for f in failures):
        passes.append("TC-P1-10 PASS: Scope compliance verified (no premature Phase 2–6 code).")

    # Output Results
    print("\nPASSED CHECKS:")
    for p in passes:
        print(f" [x] {p}")

    if failures:
        print("\nFAILED CHECKS:")
        for fl in failures:
            print(f" [ ] {fl}")
        sys.exit(1)
    else:
        print("\nALL 10 TEST SUITES PASSED! Phase 1 acceptance criteria successfully fulfilled.")
        return 0

if __name__ == "__main__":
    run_checks()
