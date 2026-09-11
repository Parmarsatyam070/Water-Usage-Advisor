import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('3_DESIGN/user_flow', exist_ok=True)

# -------------------------------------------------------------
# 1. SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=200)
    ax.set_facecolor('#0B132B')
    fig.patch.set_facecolor('#0B132B')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, "SMART WATER USAGE ADVISOR - SYSTEM ARCHITECTURE", 
            ha='center', va='center', color='#48CAE4', fontsize=18, fontweight='bold', family='sans-serif')
    ax.text(7, 9.1, "Modular MVP Architecture: Web Client -> Flask REST API -> ML/LLM Services -> PostgreSQL", 
            ha='center', va='center', color='#CAF0F8', fontsize=11, family='sans-serif')

    # Tier 1: User Interface
    ui_box = patches.FancyBboxPatch((1, 6.8), 12, 1.8, boxstyle="round,pad=0.2", 
                                   ec="#0096C7", fc="#1C2541", lw=2)
    ax.add_patch(ui_box)
    ax.text(1.3, 8.2, "USER INTERFACE LAYER (Responsive Web / HTML5 + CSS3 + Vanilla JS)", 
            color='#90E0EF', fontsize=11, fontweight='bold')
    
    # UI Sub-components
    cards = [
        ("Water Usage Dashboard\n(KPIs, Trends, Categories)", 1.5, 7.0, 3.4),
        ("AI Conservation Chatbot\n(Conversational Advisor UI)", 5.3, 7.0, 3.4),
        ("Admin / Facility Portal\n(Multi-meter, Alerts, ESG)", 9.1, 7.0, 3.4)
    ]
    for title, x, y, w in cards:
        sub = patches.FancyBboxPatch((x, y), w, 0.9, boxstyle="round,pad=0.1", ec="#48CAE4", fc="#0B132B", lw=1.2)
        ax.add_patch(sub)
        ax.text(x + w/2, y + 0.45, title, ha='center', va='center', color='#FFFFFF', fontsize=9.5, fontweight='bold')

    # Arrow Down
    ax.annotate('', xy=(7, 5.7), xytext=(7, 6.7),
                arrowprops=dict(arrowstyle="<->", color="#00B4D8", lw=2.5))
    ax.text(7.2, 6.2, "REST API (JSON / HTTP)", color="#CAF0F8", fontsize=10, fontweight='bold')

    # Tier 2: Backend API & Service Layer
    api_box = patches.FancyBboxPatch((1, 3.8), 12, 1.8, boxstyle="round,pad=0.2", 
                                    ec="#0077B6", fc="#1C2541", lw=2)
    ax.add_patch(api_box)
    ax.text(1.3, 5.2, "BACKEND & SERVICE LAYER (Python / Flask REST API)", 
            color='#90E0EF', fontsize=11, fontweight='bold')

    api_comps = [
        ("API Controllers\n/api/usage, /api/forecast\n/api/anomalies, /api/chat", 1.5, 4.0, 3.4),
        ("Business Logic Engine\nPersonalization Rules\nBaseline Normalization", 5.3, 4.0, 3.4),
        ("Auth & Access Control\nRBAC: Household / Facility\nTelemetry Validation", 9.1, 4.0, 3.4)
    ]
    for title, x, y, w in api_comps:
        sub = patches.FancyBboxPatch((x, y), w, 0.9, boxstyle="round,pad=0.1", ec="#0077B6", fc="#0B132B", lw=1.2)
        ax.add_patch(sub)
        ax.text(x + w/2, y + 0.45, title, ha='center', va='center', color='#FFFFFF', fontsize=9, fontweight='bold')

    # Arrow Down
    ax.annotate('', xy=(7, 2.7), xytext=(7, 3.7),
                arrowprops=dict(arrowstyle="<->", color="#00B4D8", lw=2.5))

    # Tier 3: Core Engines & Database
    core_box = patches.FancyBboxPatch((1, 0.5), 12, 2.1, boxstyle="round,pad=0.2", 
                                     ec="#03045E", fc="#1C2541", lw=2)
    ax.add_patch(core_box)
    ax.text(1.3, 2.2, "STORAGE & AI/ML INTELLIGENCE LAYER", 
            color='#90E0EF', fontsize=11, fontweight='bold')

    engine_comps = [
        ("PostgreSQL Database\n(12 Authoritative Tables)\nUsers, Meters, Usage, Alerts", 1.5, 0.7, 3.4, "#0077B6"),
        ("Machine Learning Models\nForecasting (MAPE <15%)\nAnomaly / Leak Detector (>95%)", 5.3, 0.7, 3.4, "#0096C7"),
        ("AI Chatbot & RAG Engine\nGoogle GenAI / System Prompts\nGrounding Knowledge Base", 9.1, 0.7, 3.4, "#48CAE4")
    ]
    for title, x, y, w, col in engine_comps:
        sub = patches.FancyBboxPatch((x, y), w, 1.2, boxstyle="round,pad=0.1", ec=col, fc="#0B132B", lw=1.5)
        ax.add_patch(sub)
        ax.text(x + w/2, y + 0.6, title, ha='center', va='center', color='#FFFFFF', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    plt.savefig('3_DESIGN/user_flow/system_architecture.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

# -------------------------------------------------------------
# 2. DATA FLOW DIAGRAM
# -------------------------------------------------------------
def create_data_flow_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
    ax.set_facecolor('#0F172A')
    fig.patch.set_facecolor('#0F172A')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7, 8.5, "SMART WATER USAGE ADVISOR - DATA FLOW ARCHITECTURE", 
            ha='center', va='center', color='#38BDF8', fontsize=17, fontweight='bold')
    ax.text(7, 8.1, "Telemetry Ingestion -> Validation -> Storage -> Parallel Analytics Pipelines -> Client UI", 
            ha='center', va='center', color='#94A3B8', fontsize=10.5)

    # Ingestion Block
    p1 = patches.FancyBboxPatch((0.8, 4.5), 2.2, 2.2, boxstyle="round,pad=0.15", ec="#38BDF8", fc="#1E293B", lw=2)
    ax.add_patch(p1)
    ax.text(1.9, 5.6, "Smart Water\nMeters\n(Simulated Telemetry\nHourly Readings)", 
            ha='center', va='center', color='#F8FAFC', fontsize=10, fontweight='bold')

    # Arrow to Validation
    ax.annotate('', xy=(3.8, 5.6), xytext=(3.0, 5.6), arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=2))

    # Validation Engine
    p2 = patches.FancyBboxPatch((3.8, 4.5), 2.4, 2.2, boxstyle="round,pad=0.15", ec="#0EA5E9", fc="#1E293B", lw=2)
    ax.add_patch(p2)
    ax.text(5.0, 5.6, "Ingestion &\nValidation Service\n(Range Checks,\nTimestamp Align)", 
            ha='center', va='center', color='#F8FAFC', fontsize=10, fontweight='bold')

    # Arrow to DB
    ax.annotate('', xy=(7.0, 5.6), xytext=(6.2, 5.6), arrowprops=dict(arrowstyle="->", color="#0EA5E9", lw=2))

    # PostgreSQL Central
    p3 = patches.FancyBboxPatch((7.0, 3.8), 2.8, 3.6, boxstyle="round,pad=0.2", ec="#0284C7", fc="#0F172A", lw=2.5)
    ax.add_patch(p3)
    ax.text(8.4, 6.9, "PostgreSQL Database", ha='center', va='center', color='#38BDF8', fontsize=12, fontweight='bold')
    ax.text(8.4, 5.4, "- users & user_profiles\n- meters\n- water_usage_data\n- predictions\n- anomalies & alerts\n- recommendations\n- goals & feedback", 
            ha='center', va='center', color='#E2E8F0', fontsize=9.5)

    # Pipelines branching out from DB
    outputs = [
        ("Predictive ML Pipeline\n(7-Day Demand Forecasts)", 7.2, 10.7, 7.8),
        ("Anomaly & Leak Engine\n(Night Flow & Spike Alerts)", 5.6, 10.7, 5.6),
        ("Recommendation Engine\n(Personalized Saving Tips)", 4.0, 10.7, 3.4),
        ("Chatbot Knowledge Service\n(Context-Aware RAG)", 2.4, 10.7, 1.2)
    ]

    for label, y_start, x_end, y_end in outputs:
        p_out = patches.FancyBboxPatch((x_end, y_end - 0.7), 2.8, 1.4, boxstyle="round,pad=0.1", ec="#0369A1", fc="#1E293B", lw=1.5)
        ax.add_patch(p_out)
        ax.text(x_end + 1.4, y_end, label, ha='center', va='center', color='#F8FAFC', fontsize=9.5, fontweight='bold')
        ax.annotate('', xy=(x_end, y_end), xytext=(9.8, y_start), arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.8))

    plt.tight_layout()
    plt.savefig('3_DESIGN/user_flow/data_flow_diagram.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

# -------------------------------------------------------------
# 3. AI WORKFLOW DIAGRAM
# -------------------------------------------------------------
def create_ai_workflow_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
    ax.set_facecolor('#0A192F')
    fig.patch.set_facecolor('#0A192F')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7, 8.5, "SMART WATER USAGE ADVISOR - AI & ML WORKFLOW PIPELINE", 
            ha='center', va='center', color='#64FFDA', fontsize=17, fontweight='bold')
    ax.text(7, 8.1, "Dual Machine Learning Analytics & Retrieval-Augmented Generation (RAG) Architecture", 
            ha='center', va='center', color='#8892B0', fontsize=10.5)

    # Ingestion & Features
    box1 = patches.FancyBboxPatch((0.8, 3.2), 2.6, 3.5, boxstyle="round,pad=0.15", ec="#64FFDA", fc="#112240", lw=2)
    ax.add_patch(box1)
    ax.text(2.1, 6.2, "Feature Pipeline", ha='center', va='center', color='#64FFDA', fontsize=12, fontweight='bold')
    ax.text(2.1, 4.7, "- Consumption Lags\n  (1d, 7d, 14d)\n- Rolling 24h Mean/Std\n- Hour & Day-of-Week\n- Ambient Temperature\n- Minimum Night Flow", 
            ha='center', va='center', color='#CCD6F6', fontsize=9.5)

    # Arrows to 3 parallel AI streams
    streams = [
        ("Predictive Forecasting Model", 5.5, 6.2, 
         "Algorithm: Random Forest / Ridge\nInput: Historical Lags + Temp\nTarget: Next 7 Days (MAPE <15%)\nOutput: predictions table", "#00B4D8"),
        ("Anomaly & Leak Detector", 5.5, 3.5, 
         "Algorithm: Isolation Forest + MNF\nLogic: Night flow > 0 for 3h OR Z > 3.0\nTarget: >95% Leak Detection\nOutput: anomalies & alerts", "#FF6B6B"),
        ("RAG Conservation Chatbot", 5.5, 0.8, 
         "Model: Google GenAI (Gemini) / Fallback\nContext: Profile + Recs + Knowledge Base\nTarget: Latency <2s, Grounded Advice\nOutput: chatbot_conversations", "#48CAE4")
    ]

    for title, x, y, desc, col in streams:
        ax.annotate('', xy=(x, y + 1.1), xytext=(3.4, 5.0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        b = patches.FancyBboxPatch((x, y), 4.2, 2.2, boxstyle="round,pad=0.15", ec=col, fc="#112240", lw=2)
        ax.add_patch(b)
        ax.text(x + 2.1, y + 1.8, title, ha='center', va='center', color=col, fontsize=11, fontweight='bold')
        ax.text(x + 2.1, y + 0.9, desc, ha='center', va='center', color='#CCD6F6', fontsize=9)

        # Output to Consumer Interface
        ax.annotate('', xy=(10.5, 4.5), xytext=(x + 4.2, y + 1.1), arrowprops=dict(arrowstyle="->", color=col, lw=2))

    # Client Decision Impact Block
    box_end = patches.FancyBboxPatch((10.5, 2.5), 2.8, 4.0, boxstyle="round,pad=0.2", ec="#64FFDA", fc="#112240", lw=2)
    ax.add_patch(box_end)
    ax.text(11.9, 6.0, "Decisions & Action", ha='center', va='center', color='#64FFDA', fontsize=12, fontweight='bold')
    ax.text(11.9, 4.2, "- Budget Warnings\n- High Bill Prevention\n- Rapid Leak Repair\n- Personalized DIY Tips\n- 20-30% Water Saved\n- SDG 6 Metrics Met", 
            ha='center', va='center', color='#E6F1FF', fontsize=10)

    plt.tight_layout()
    plt.savefig('3_DESIGN/user_flow/ai_workflow_diagram.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

# -------------------------------------------------------------
# 4. USER JOURNEY MAP
# -------------------------------------------------------------
def create_user_journey_map():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
    ax.set_facecolor('#1E1E2E')
    fig.patch.set_facecolor('#1E1E2E')
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    ax.text(7.5, 8.0, "SMART WATER USAGE ADVISOR - END-TO-END USER JOURNEY MAP", 
            ha='center', va='center', color='#F5C2E7', fontsize=17, fontweight='bold')
    ax.text(7.5, 7.6, "Stages: Onboarding -> Monitoring -> Anomaly Detection -> AI Diagnosis -> Conservation Action", 
            ha='center', va='center', color='#BAC2DE', fontsize=10.5)

    stages = [
        ("1. Onboarding", "Profile Setup", "Enter occupants, fixtures,\nand monthly conservation\ngoal (e.g., -25%).", "#89B4FA", 0.5),
        ("2. Monitoring", "Daily Telemetry", "Check usage dashboard,\ncategory breakdowns,\nand 7-day forecast.", "#A6E3A1", 3.4),
        ("3. Alert Trigger", "Anomaly Alert", "Receive push/app alert:\n'Continuous 14 L/hr flow\ndetected at night'.", "#F38BA8", 6.3),
        ("4. AI Diagnosis", "Chatbot Advisory", "Ask AI: 'Where is this\ncoming from?' AI suggests\nquick flapper valve test.", "#F9E2AF", 9.2),
        ("5. Resolution", "Verified Impact", "User repairs valve.\nFlow drops to 0.\nDashboard shows $32/mo\nand 350L/day saved.", "#CBA6F7", 12.1)
    ]

    for title, subtitle, details, col, x in stages:
        b = patches.FancyBboxPatch((x, 1.8), 2.4, 5.0, boxstyle="round,pad=0.15", ec=col, fc="#181825", lw=2)
        ax.add_patch(b)
        ax.text(x + 1.2, 6.3, title, ha='center', va='center', color=col, fontsize=12, fontweight='bold')
        ax.text(x + 1.2, 5.7, subtitle, ha='center', va='center', color='#CDD6F4', fontsize=10, fontweight='bold')
        ax.text(x + 1.2, 4.4, details, ha='center', va='center', color='#A6ADC8', fontsize=9.5)

        # Experience sentiment circle
        circle = patches.Circle((x + 1.2, 2.5), 0.45, facecolor=col, edgecolor='none')
        ax.add_patch(circle)
        icon = "★"
        ax.text(x + 1.2, 2.5, icon, ha='center', va='center', color='#11111B', fontsize=14, fontweight='bold')

    # Sequential Flow Arrows
    for i in range(4):
        x_start = 0.5 + i * 2.9 + 2.4
        x_end = 0.5 + (i + 1) * 2.9
        ax.annotate('', xy=(x_end, 4.3), xytext=(x_start, 4.3), arrowprops=dict(arrowstyle="->", color="#F5C2E7", lw=2.5))

    plt.tight_layout()
    plt.savefig('3_DESIGN/user_flow/user_journey_map.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

if __name__ == '__main__':
    create_system_architecture()
    create_data_flow_diagram()
    create_ai_workflow_diagram()
    create_user_journey_map()
    print("All 4 architecture and user flow diagrams successfully generated.")
