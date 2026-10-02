import streamlit as st
import pandas as pd
import random
import os
import json

try:
    import anthropic
    _ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    _ANTHROPIC_SDK_AVAILABLE = False

# 1. Page Configuration
st.set_page_config(
    page_title="SIH26043 - CivicFix Innovation Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS - Scoped font definitions preventing icon text leaks
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Global Base Styling (Scoped strictly to avoid overriding Streamlit Icon fonts) */
    html, body, .stApp {
        background-color: #EFEDE4 !important;
    }

    .stMarkdown, p, label, input, textarea, div.stText {
        font-family: 'Inter', sans-serif;
        color: #16233D;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Headings */
    h1 {
        font-family: 'Zilla Slab', serif !important;
        color: #16233D !important;
        font-size: 2.1rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        font-family: 'Zilla Slab', serif !important;
        color: #16233D !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
    }

    h3 {
        font-family: 'Zilla Slab', serif !important;
        color: #16233D !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }

    /* -------------------------------------------------------------
       SIDEBAR ARROW FIX
       -------------------------------------------------------------
       Streamlit may render the internal icon name
       "keyboard_double_arrow_right" as plain text when the
       Material Symbols font does not load correctly.

       We therefore hide the native icon/text completely and
       draw our own visible ">>" arrow with CSS.
       ------------------------------------------------------------- */

    /* Style ONLY the actual sidebar collapse/open button */
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #16233D !important;
        border: 1.5px solid #E3A73B !important;
        border-radius: 6px !important;
        padding: 5px 9px !important;
        min-width: 48px !important;
        min-height: 36px !important;
        width: 48px !important;
        height: 36px !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
    }

    /* Completely hide Streamlit's internal icon and its text */
    button[data-testid="stSidebarCollapseButton"] span,
    button[data-testid="stSidebarCollapseButton"] div,
    button[data-testid="stSidebarCollapseButton"] [data-testid="stIcon"],
    button[data-testid="stSidebarCollapseButton"] .material-symbols-outlined,
    button[data-testid="stSidebarCollapseButton"] .material-symbols-rounded {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        color: transparent !important;
        overflow: hidden !important;
    }

    /* Hide any direct text inside the native button */
    button[data-testid="stSidebarCollapseButton"] {
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }

    /* Draw the actual double-arrow */
    button[data-testid="stSidebarCollapseButton"]::after {
        content: ">>" !important;
        display: block !important;
        width: auto !important;
        height: auto !important;
        color: #FFFFFF !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        letter-spacing: -2px !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Keep the arrow visible when Streamlit changes the aria-label */
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"] {
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }

    button[aria-label="Collapse sidebar"] span,
    button[aria-label="Collapse sidebar"] div,
    button[aria-label="Collapse sidebar"] [data-testid="stIcon"],
    button[aria-label="Expand sidebar"] span,
    button[aria-label="Expand sidebar"] div,
    button[aria-label="Expand sidebar"] [data-testid="stIcon"] {
        display: none !important;
        visibility: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }

    button[aria-label="Collapse sidebar"]::after,
    button[aria-label="Expand sidebar"]::after {
        content: ">>" !important;
        display: block !important;
        color: #FFFFFF !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        letter-spacing: -2px !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #16233D !important;
        border-right: 2px solid #0F172A !important;
    }
    
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] div {
        color: #EFEDE4 !important;
        font-size: 0.92rem;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background-color: #B23A2E !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
        padding: 10px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Cards, Forms, and Dropdowns */
    div[data-testid="stForm"], div.stContainer {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
        padding: 24px !important;
        box-shadow: 0 2px 8px rgba(22, 35, 61, 0.06) !important;
        border: 1px solid #DEDBCC !important;
        margin-bottom: 20px !important;
    }

    label, label p {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #16233D !important;
    }

    input, textarea {
        color: #16233D !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #5B5847 !important;
        border-radius: 4px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #5B5847 !important;
        border-radius: 4px !important;
    }

    div[data-baseweb="select"] * {
        color: #16233D !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] * {
        background-color: #FFFFFF !important;
        color: #16233D !important;
    }

    div[role="option"]:hover,
    ul[data-baseweb="menu"] li:hover {
        background-color: #E3A73B !important;
        color: #16233D !important;
    }

    div[data-testid="stForm"] button, button[kind="primaryFormSubmit"], div.stButton > button:first-child {
        background-color: #E3A73B !important;
        color: #16233D !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .dept-pill {
        display: inline-block;
        background-color: #16233D;
        color: #EFEDE4 !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 6px;
    }

    .govt-pill {
        display: inline-block;
        background-color: #B23A2E;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 6px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Credentials Database
USER_CREDENTIALS = {
    "University / Research Institute": {
        "COLLEGE ABC": "1234",
        "COLLEGE XYZ": "0000",
        "COLLEGE PQR": "1010"
    },
    "Government Official": {
        "GOVT_INSPECT_01": "govt123",
        "GOVT_ADMIN_01": "adminpass"
    },
    "Platform Administrator": {
        "ADMIN_SUPER": "sih2026"
    }
}

# 3b. University Departments for Practical R&D Innovation
DEPARTMENT_KEYWORDS = {
    "Civil Engineering": [
        "structural analysis", "concrete composition", "material research", "building model", "culvert design"
    ],
    "Environmental Engineering": [
        "filtration model", "chemical analysis", "water purity testing", "bioremediation", "drainage simulation"
    ],
    "Computer Science / IT": [
        "sensor", "iot", "app", "software", "camera", "smart", "automation",
        "monitoring system", "data", "gps", "dashboard"
    ],
    "Electrical Engineering": [
        "solar grid", "smart grid", "auto fault detection", "voltage stabilizer research", "relay system"
    ],
    "Architecture & Urban Planning": [
        "urban design", "landscaping model", "pedestrian redesign", "public space layout"
    ],
    "Agriculture & Rural Development": [
        "soil salinity research", "agronomy trial", "micro-irrigation design", "crop disease detection"
    ],
}

# Keywords indicating standard physical labor/routine municipal maintenance
PHYSICAL_WORK_KEYWORDS = [
    "pothole clearing", "pothole filling", "patching", "pothole", "garbage clearing", 
    "garbage removal", "trash dump", "waste collection", "wall repairing", 
    "compound wall reconstruction", "pipe unclogging", "silt removal", "bulb replacement",
    "street light replacement", "manual repair", "weed cutting", "drain cleaning",
    "highway", "flyover", "bridge repair", "crack pillar", "police", "heavy machinery", "emergency"
]

# 4. Seed / Demo Data
# Pulled out as its own constant (rather than inline in the session-state check)
# so it can also be used by the "Reset Demo Data" button below — Streamlit's
# session_state only runs this init block ONCE per browser session, so without
# a reset button, updating this list has no effect on an already-open session.
SEED_ISSUES = [
        # --- PHYSICAL WORK ROUTED TO GOVT ---
        {
            "id": "ISSUE-101",
            "title": "Pothole Clearing and Road Patching on Main Street",
            "description": "Multiple potholes along main market road requiring routine physical labor, asphalt filling, and road clearing.",
            "category": "Urban & Civil Infrastructure",
            "location": "Ranchi, Jharkhand",
            "status": "Direct Govt Action Required",
            "submitted_by": "Ramesh Kumar (9876543210)",
            "assigned_to": "Public Works Dept",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹20,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Identified as routine physical maintenance (pothole clearing / road patching). Assigned directly to Government Officials."
        },
        # --- PRACTICAL R&D SOLUTION TO UNIVERSITY ---
        {
            "id": "ISSUE-102",
            "title": "IoT Drain Flood Monitoring & Smart Early Warning Sensor Network",
            "description": "Recurring urban flash floods require developing an IoT-based automated water level sensor system and alerting app.",
            "category": "Water Resources & Drainage",
            "location": "Kochi, Kerala",
            "status": "Pending Govt Approval",
            "submitted_by": "Anand V. (9447000111)",
            "assigned_to": "COLLEGE ABC",
            "department": "Computer Science / IT",
            "milestone": "Adoption Requested by COLLEGE ABC",
            "funding_status": "Grant Pending Approval",
            "grant_amount": "₹50,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Computer Science / IT",
            "ai_reasoning": "Identified as requiring a practical technological solution (IoT sensor & app development). Routed to Computer Science / IT."
        },
        # --- MORE GOVT-DIRECT (routine physical/operational work) ---
        {
            "id": "ISSUE-103",
            "title": "Garbage Clearing Near Community Market",
            "description": "Overflowing garbage bins near the vegetable market have not been cleared for over a week, causing a health hazard.",
            "category": "Sanitation & Waste Management",
            "location": "Thiruvananthapuram, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Latha Menon (9744112233)",
            "assigned_to": "Sanitation Dept",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹8,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Routine waste collection with an existing, known process. No new design or research needed — assigned directly to Sanitation Dept."
        },
        {
            "id": "ISSUE-104",
            "title": "Streetlight Bulb Replacement on School Road",
            "description": "Three streetlights near the government school have been non-functional for two weeks, making the road unsafe after dark.",
            "category": "Urban & Civil Infrastructure",
            "location": "Kollam, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Suresh Pillai (9895543210)",
            "assigned_to": "Electricity Board (Maintenance)",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹5,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Straightforward bulb replacement using existing standard fixtures — routine execution, not a design problem. Assigned directly to Govt Officials."
        },
        {
            "id": "ISSUE-105",
            "title": "Compound Wall Reconstruction After Storm Damage",
            "description": "The compound wall of the government primary health centre collapsed during last week's storm and needs to be rebuilt before the monsoon.",
            "category": "Urban & Civil Infrastructure",
            "location": "Alappuzha, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Beena Thomas (9847098470)",
            "assigned_to": "Public Works Dept",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹35,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Standard wall reconstruction using known construction methods. Requires manpower and material, not new engineering research — assigned directly to Govt Officials."
        },
        {
            "id": "ISSUE-106",
            "title": "Fallen Tree Blocking State Highway After Cyclone",
            "description": "A large tree fell across the state highway during the cyclone last night and is blocking traffic in both directions. Needs immediate clearance with heavy machinery.",
            "category": "Emergency & Public Safety",
            "location": "Kottayam, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Traffic Police Outpost (0481-2345678)",
            "assigned_to": "Highways Dept / Emergency Response",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Emergency Fund Allocated",
            "grant_amount": "₹12,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Emergency clearance requiring heavy machinery and immediate manual response, not a research problem. Assigned directly to Emergency Response."
        },
        # --- MORE PRACTICAL R&D SOLUTIONS TO UNIVERSITY, ACROSS DEPARTMENTS ---
        {
            "id": "ISSUE-107",
            "title": "Recurring Cracks in Flyover Support Pillars",
            "description": "Support pillars under the city flyover have developed cracks that keep reappearing every year despite repeated patch repairs. A permanent structural fix is needed, possibly involving new material or reinforcement design.",
            "category": "Urban & Civil Infrastructure",
            "location": "Kozhikode, Kerala",
            "status": "Open",
            "submitted_by": "Municipal Engineer Office (0495-2345000)",
            "assigned_to": None,
            "department": None,
            "milestone": "Awaiting Adoption",
            "funding_status": "Not Requested",
            "grant_amount": "₹0",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Civil Engineering",
            "ai_reasoning": "Repeated patch repairs have failed, indicating the existing fix doesn't address the root cause. Needs structural material research and reinforcement design — routed to Civil Engineering."
        },
        {
            "id": "ISSUE-108",
            "title": "Industrial Effluent Contaminating Local Pond Water",
            "description": "Water in the village pond has turned foul-smelling and unsafe for cattle after a nearby small-scale unit began discharging waste. Residents want the water tested and a low-cost filtration approach designed before the next monsoon refill.",
            "category": "Water Resources & Drainage",
            "location": "Palakkad, Kerala",
            "status": "In Progress",
            "submitted_by": "Village Panchayat Ward 4 (9447112200)",
            "assigned_to": "COLLEGE XYZ",
            "department": "Environmental Engineering",
            "milestone": "Approved & Funded (₹1,00,000) for COLLEGE XYZ",
            "funding_status": "Sanctioned & Allocated",
            "grant_amount": "₹1,00,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Environmental Engineering",
            "ai_reasoning": "Needs chemical testing of contamination and design of a filtration approach — not a task a maintenance crew can execute. Routed to Environmental Engineering."
        },
        {
            "id": "ISSUE-109",
            "title": "Frequent Transformer Trips Cutting Power to Rural Feeder Line",
            "description": "The transformer supplying three villages trips several times a week for no clear reason, and replacing fuses hasn't solved it. Residents want the underlying fault studied and an automatic fault-detection approach proposed.",
            "category": "Electricity & Power",
            "location": "Wayanad, Kerala",
            "status": "Pending Govt Approval",
            "submitted_by": "Rural Electricity Consumers Assoc. (9400112233)",
            "assigned_to": "COLLEGE PQR",
            "department": "Electrical Engineering",
            "milestone": "Adoption Requested by COLLEGE PQR",
            "funding_status": "Grant Pending Approval",
            "grant_amount": "₹75,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Electrical Engineering",
            "ai_reasoning": "Routine fuse replacement already failed to fix the underlying issue, so the fault needs to be diagnosed and an automated detection/relay solution designed. Routed to Electrical Engineering."
        },
        {
            "id": "ISSUE-110",
            "title": "Unsafe Pedestrian Crossing Near Government School",
            "description": "Children crossing near the school gate face fast traffic with no safe crossing point, and simply painting a zebra crossing hasn't stopped accidents. Parents are asking for the junction to be redesigned with a proper pedestrian-safety layout.",
            "category": "Urban & Civil Infrastructure",
            "location": "Thrissur, Kerala",
            "status": "Open",
            "submitted_by": "Parents-Teachers Association (9846098460)",
            "assigned_to": None,
            "department": None,
            "milestone": "Awaiting Adoption",
            "funding_status": "Not Requested",
            "grant_amount": "₹0",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Architecture & Urban Planning",
            "ai_reasoning": "A basic crossing marking already failed to solve the safety problem, meaning the junction itself needs to be redesigned. Routed to Architecture & Urban Planning."
        },
        {
            "id": "ISSUE-111",
            "title": "Farmland Turning Saline, Reducing Crop Yield",
            "description": "Paddy yield in several fields near the backwaters has dropped sharply over three seasons, and farmers suspect rising soil salinity from tidal water intrusion. They want the soil studied and a suitable irrigation or crop adaptation approach worked out.",
            "category": "Agriculture & Rural Development",
            "location": "Alappuzha, Kerala",
            "status": "Open",
            "submitted_by": "Karshaka Samithi, Kuttanad (9497123456)",
            "assigned_to": None,
            "department": None,
            "milestone": "Awaiting Adoption",
            "funding_status": "Not Requested",
            "grant_amount": "₹0",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Agriculture & Rural Development",
            "ai_reasoning": "Falling yield over multiple seasons points to an unresolved soil condition, not something field labor can fix. Needs a salinity study and irrigation/crop trial — routed to Agriculture & Rural Development."
        },
        # --- NEW: MORE UNIVERSITY-SIDE DEMO DATA (varied statuses / depts) ---
        {
            "id": "ISSUE-112",
            "title": "Smart Traffic Signal Congestion Study for City Junction",
            "description": "The main city junction sees severe congestion every evening despite manual signal timing adjustments by traffic police. Officials want a data-driven adaptive signal timing model designed and simulated before installing new hardware.",
            "category": "Urban & Civil Infrastructure",
            "location": "Kannur, Kerala",
            "status": "In Progress",
            "submitted_by": "City Traffic Police HQ (0497-2345111)",
            "assigned_to": "COLLEGE ABC",
            "department": "Computer Science / IT",
            "milestone": "Approved & Funded (₹1,20,000) for COLLEGE ABC",
            "funding_status": "Sanctioned & Allocated",
            "grant_amount": "₹1,20,000",
            "proof_work": "",
            "mentor_name": "Dr. Priya Nair",
            "mentor_phone": "9846011223",
            "num_students": 4,
            "student_team": [
                {"name": "Arjun Menon", "roll_number": "CS21045"},
                {"name": "Fathima Rasheed", "roll_number": "CS21067"},
                {"name": "Nikhil Varma", "roll_number": "CS21089"},
                {"name": "Sreelakshmi S.", "roll_number": "CS21102"}
            ],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Computer Science / IT",
            "ai_reasoning": "Manual timing adjustments have not solved recurring congestion, so an adaptive, data-driven signal-timing model needs to be designed and simulated. Routed to Computer Science / IT."
        },
        {
            "id": "ISSUE-113",
            "title": "Riverbank Erosion Threatening Village Homes",
            "description": "Yearly sandbag reinforcement along the riverbank has failed to stop erosion, and several homes are now within a few metres of the eroding edge. The panchayat wants a proper erosion-control structure designed rather than repeating temporary sandbagging.",
            "category": "Water Resources & Drainage",
            "location": "Pathanamthitta, Kerala",
            "status": "Pending Govt Approval",
            "submitted_by": "Village Panchayat Ward 7 (9447556677)",
            "assigned_to": "COLLEGE XYZ",
            "department": "Civil Engineering",
            "milestone": "Adoption Requested by COLLEGE XYZ",
            "funding_status": "Grant Pending Approval",
            "grant_amount": "₹2,50,000",
            "proof_work": "",
            "mentor_name": "Prof. K. Sudhakaran",
            "mentor_phone": "9895112244",
            "num_students": 3,
            "student_team": [
                {"name": "Anagha Krishnan", "roll_number": "CE20014"},
                {"name": "Rahul Thankachan", "roll_number": "CE20028"},
                {"name": "Devika Suresh", "roll_number": "CE20041"}
            ],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Civil Engineering",
            "ai_reasoning": "Temporary sandbag reinforcement has repeatedly failed, so a permanent engineered erosion-control structure needs to be designed. Routed to Civil Engineering."
        },
        {
            "id": "ISSUE-114",
            "title": "Low-Cost Solar Micro-Grid Feasibility for Remote Hamlet",
            "description": "A remote hill hamlet has no grid electricity and extending the main line has been ruled out as too costly by the Electricity Board. Residents want a feasibility study and design for a small solar micro-grid sized to the hamlet's needs.",
            "category": "Electricity & Power",
            "location": "Idukki, Kerala",
            "status": "Open",
            "submitted_by": "Tribal Welfare Committee (9497223344)",
            "assigned_to": None,
            "department": None,
            "milestone": "Awaiting Adoption",
            "funding_status": "Not Requested",
            "grant_amount": "₹0",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "University-Eligible (Practical R&D)",
            "ai_department": "Electrical Engineering",
            "ai_reasoning": "Standard grid extension was ruled out as infeasible, so a purpose-built micro-grid needs to be designed and sized — genuine engineering design work. Routed to Electrical Engineering."
        },
        # --- NEW: MORE GOVT-SIDE DEMO DATA (varied physical maintenance) ---
        {
            "id": "ISSUE-115",
            "title": "Overflowing Public Toilet Block Needs Pipe Unclogging",
            "description": "The public toilet block near the bus stand is overflowing due to a clogged sewage pipe. Needs immediate manual unclogging and drain cleaning by the sanitation crew.",
            "category": "Sanitation & Waste Management",
            "location": "Kottayam, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Bus Stand Committee (9847665544)",
            "assigned_to": "Sanitation Dept",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹6,500",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Standard pipe unclogging with an existing municipal process — routine execution, not a design problem. Assigned directly to Sanitation Dept."
        },
        {
            "id": "ISSUE-116",
            "title": "Overgrown Weeds Blocking Roadside Drain",
            "description": "Roadside drains near the market are choked with overgrown weeds and silt, causing waterlogging after light rain. Needs manual weed cutting and silt removal.",
            "category": "Water Resources & Drainage",
            "location": "Malappuram, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Market Traders Association (9895223311)",
            "assigned_to": "Public Works Dept",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹4,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Routine weed cutting and silt clearance using standard maintenance procedure. Assigned directly to Public Works Dept."
        },
        {
            "id": "ISSUE-117",
            "title": "Police Barricade Needed for Weekend Festival Traffic",
            "description": "An annual temple festival this weekend draws heavy crowds and needs police barricading and traffic diversion at the junction, as in previous years.",
            "category": "Emergency & Public Safety",
            "location": "Kollam, Kerala",
            "status": "Direct Govt Action Required",
            "submitted_by": "Temple Committee (9744556699)",
            "assigned_to": "Traffic Police",
            "department": "Municipal Works",
            "milestone": "Assigned for Physical Execution",
            "funding_status": "Municipal Budget Allocated",
            "grant_amount": "₹3,000",
            "proof_work": "",
            "mentor_name": "",
            "mentor_phone": "",
            "num_students": 0,
            "student_team": [],
            "ai_target": "Govt-Direct (Physical Maintenance)",
            "ai_department": None,
            "ai_reasoning": "Recurring, well-understood crowd-management task handled the same way every year — routine deployment, not a design problem. Assigned directly to Traffic Police."
        }
]

if "issues" not in st.session_state:
    # Deep-ish copy so the running app never mutates the SEED_ISSUES constant itself
    st.session_state.issues = [dict(issue) for issue in SEED_ISSUES]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "citizen_phone" not in st.session_state:
    st.session_state.citizen_phone = None

# --- OTP-related session state (NEW) ---
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "citizen_otp" not in st.session_state:
    st.session_state.citizen_otp = None
if "pending_citizen_name" not in st.session_state:
    st.session_state.pending_citizen_name = None
if "pending_citizen_phone" not in st.session_state:
    st.session_state.pending_citizen_phone = None

# AI Assistant Routines
def categorize_issue(description):
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["water", "drain", "flood", "river", "pipe"]):
        return "Water Resources & Drainage"
    elif any(w in desc_lower for w in ["crop", "soil", "farm", "agriculture", "fertilizer"]):
        return "Agriculture & Rural Development"
    elif any(w in desc_lower for w in ["road", "bridge", "pothole", "traffic", "building", "flyover"]):
        return "Urban & Civil Infrastructure"
    elif any(w in desc_lower for w in ["health", "hospital", "medicine", "doctor"]):
        return "Healthcare & Public Health"
    else:
        return "General Community Issue"

CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"  # fast & cheap — good enough for triage reasoning

CLASSIFY_SYSTEM_PROMPT = """You are the AI triage assistant for CivicFix, a civic-issue portal. Every citizen complaint must be routed to exactly one of two places:

1. GOVT-DIRECT (Physical Maintenance) — the issue has a known, standard fix. A work crew just needs to go execute it: filling a pothole, clearing garbage, unclogging a pipe, repairing a wall, replacing a bulb, emergency response, etc. No new idea, design, or research is required to solve it.

2. UNIVERSITY-ELIGIBLE (Practical R&D) — a known/standard fix does not exist or has repeatedly failed, and actually solving the problem means someone has to come up with an idea: design a system, research a material, build a monitoring/detection setup, redesign something, run a study or trial. The test is not whether the issue *sounds* technical — it's whether resolving it requires invention/design work rather than routine execution.

Judge the SUBSTANCE of the problem, not buzzwords. Do NOT route something to University just because it mentions "smart", "IoT", "innovative", "app", etc. — if the actual ask is just "install this known gadget", that is still routine execution and belongs to Govt-Direct. Conversely, do NOT keep something at Govt-Direct just because it's phrased plainly — e.g. "this drain floods every monsoon no matter how many times we clear it, nothing works" describes an unsolved problem needing a real solution, so it belongs to a university even though it uses no technical words at all.

If University-Eligible, also pick the SINGLE best-fit department from this list:
{departments}

Respond with ONLY valid JSON and nothing else — no markdown fences, no preamble:
{{"target": "University-Eligible (Practical R&D)" or "Govt-Direct (Physical Maintenance)", "department": "<one department name from the list>" or null, "reasoning": "<one or two plain-language sentences explaining what the issue actually needs>"}}"""


def _get_anthropic_client():
    """Returns an Anthropic client if an API key is configured, else None."""
    if not _ANTHROPIC_SDK_AVAILABLE:
        return None
    api_key = None
    try:
        # Preferred: .streamlit/secrets.toml -> ANTHROPIC_API_KEY = "sk-..."
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None


def ai_classify_issue_llm(title, description):
    """Semantic triage via Claude: understands the problem instead of matching keywords.
    Returns (target, department, reasoning) on success, or None if unavailable/failed
    so the caller can fall back to the keyword-based classifier."""
    client = _get_anthropic_client()
    if client is None:
        return None

    dept_list = "\n".join(f"- {d}" for d in DEPARTMENT_KEYWORDS.keys())
    system_prompt = CLASSIFY_SYSTEM_PROMPT.format(departments=dept_list)
    user_content = f"Issue Title: {title}\nIssue Description: {description}"

    try:
        response = client.messages.create(
            model=CLASSIFIER_MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        raw = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

        data = json.loads(raw)
        target = data.get("target")
        department = data.get("department")
        reasoning = data.get("reasoning", "").strip()

        if target not in ("University-Eligible (Practical R&D)", "Govt-Direct (Physical Maintenance)"):
            return None  # malformed response, fall back

        if target.startswith("Govt"):
            department = None
        elif department not in DEPARTMENT_KEYWORDS:
            department = None  # unrecognized department name, drop it rather than trust it blindly

        prefix = "🤖 AI understanding of the problem: " if reasoning else "🤖 AI triage decision (no reasoning returned)."
        return target, department, f"{prefix}{reasoning}"
    except Exception:
        return None  # network/parsing/auth error -> fall back silently


def ai_classify_issue_keyword_fallback(title, description):
    """Offline fallback used only when no ANTHROPIC_API_KEY is configured, or the
    live call fails. Keyword-based, so it's cruder than the LLM path above."""
    text = (title + " " + description).lower()

    matched_physical_kw = [k for k in PHYSICAL_WORK_KEYWORDS if k in text]
    if matched_physical_kw:
        return (
            "Govt-Direct (Physical Maintenance)",
            None,
            f"[Keyword fallback — no live AI configured] Identified as routine physical maintenance work (matched: '{matched_physical_kw[0]}'). Assigned directly to Govt Officials."
        )

    dept_scores = {}
    for dept, keywords in DEPARTMENT_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            dept_scores[dept] = hits

    if not dept_scores:
        return (
            "Govt-Direct (Physical Maintenance)",
            None,
            "[Keyword fallback — no live AI configured] No R&D keywords matched. Assigned directly to Govt Officials."
        )

    best_dept = max(dept_scores, key=lambda d: len(dept_scores[d]))
    matched_terms = ", ".join(dept_scores[best_dept][:3])
    return (
        "University-Eligible (Practical R&D)",
        best_dept,
        f"[Keyword fallback — no live AI configured] Matched R&D department: {best_dept} ({matched_terms})."
    )


def ai_classify_issue(title, description):
    """Primary entry point used everywhere else in the app. Tries real semantic
    understanding via Claude first, and only drops to keyword matching if no
    API key is set or the live call fails for any reason."""
    llm_result = ai_classify_issue_llm(title, description)
    if llm_result is not None:
        return llm_result
    return ai_classify_issue_keyword_fallback(title, description)


def ai_engine_status():
    """Small helper so the UI can honestly show which triage engine is active."""
    return "live" if _get_anthropic_client() is not None else "fallback"

def _generate_otp():
    """Generates a 4-digit OTP, zero-padded (e.g. '0042')."""
    return f"{random.randint(0, 9999):04d}"

def _reset_otp_flow():
    st.session_state.otp_sent = False
    st.session_state.citizen_otp = None
    st.session_state.pending_citizen_name = None
    st.session_state.pending_citizen_phone = None

# 5. Collapsible Sidebar
with st.sidebar:
    st.title("🏛️ SIH26043 CivicFix")
    if st.session_state.logged_in:
        st.markdown("---")
        st.markdown("### 👤 Account Workspace")
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role}")
        if st.session_state.user_role == "Citizen":
            st.write(f"**Contact:** {st.session_state.citizen_phone}")
        
        st.markdown("---")
        if st.button("🚪 LOG OUT NOW"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.session_state.citizen_phone = None
            _reset_otp_flow()
            st.rerun()
    else:
        st.info("Select your access role on the portal screen to log in.")

# 6. Main Portal Screen
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>CivicFix <span style='color: #E3A73B;'>·</span> Societal Innovation Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5B5847;'>Connecting Crowdsourced Civic Challenges with Academic Research & Government Grants</p>", unsafe_allow_html=True)
    
    col1, col_login, col2 = st.columns([1, 2, 1])
    with col_login:
        st.markdown("### 🔐 User Portal Authentication")
        role_choice = st.selectbox(
            "Select Your Access Role:",
            ["-- Choose Role --", "Citizen Portal (Public)", "University / Research Institute", "Government Official", "Platform Administrator"]
        )

        if role_choice == "Citizen Portal (Public)":
            # ---------------- STAGE 1: Name + Phone -> Send OTP ----------------
            if not st.session_state.otp_sent:
                st.info("Citizens must verify their mobile number with a One-Time Password (OTP) before entering the portal.")
                citizen_name = st.text_input("Enter Full Name:")
                citizen_phone = st.text_input("Enter 10-Digit Mobile Number:", max_chars=10)
                if st.button("Send OTP", use_container_width=True):
                    clean_phone = citizen_phone.strip()
                    if citizen_name.strip() and clean_phone.isdigit() and len(clean_phone) == 10:
                        st.session_state.citizen_otp = _generate_otp()
                        st.session_state.otp_sent = True
                        st.session_state.pending_citizen_name = citizen_name.strip()
                        st.session_state.pending_citizen_phone = clean_phone
                        st.rerun()
                    else:
                        st.error("❌ Please provide a valid Name and 10-digit Phone Number.")

            # ---------------- STAGE 2: Enter + Verify OTP ----------------
            else:
                st.success(f"📱 OTP sent to **{st.session_state.pending_citizen_phone}**")
                # DEMO ONLY: no SMS gateway is wired up yet, so the OTP is shown
                # here so the flow can be tested end-to-end. Before going live,
                # swap this block for a real SMS API call (e.g. Twilio, MSG91,
                # Fast2SMS) and delete the st.caption line below so the OTP is
                # never exposed in the UI.
                st.caption(f"🔧 Demo mode — simulated OTP: `{st.session_state.citizen_otp}` (no SMS gateway connected)")

                otp_input = st.text_input("Enter the 4-Digit OTP:", max_chars=4)

                col_verify, col_resend, col_cancel = st.columns(3)
                with col_verify:
                    if st.button("Verify & Enter Portal", use_container_width=True):
                        if otp_input.strip() == st.session_state.citizen_otp:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "Citizen"
                            st.session_state.username = st.session_state.pending_citizen_name
                            st.session_state.citizen_phone = st.session_state.pending_citizen_phone
                            _reset_otp_flow()
                            st.rerun()
                        else:
                            st.error("❌ Incorrect OTP. Please check the code and try again.")
                with col_resend:
                    if st.button("Resend OTP", use_container_width=True):
                        st.session_state.citizen_otp = _generate_otp()
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", use_container_width=True):
                        _reset_otp_flow()
                        st.rerun()

        elif role_choice in USER_CREDENTIALS:
            username_input = st.text_input("Enter User ID / College Name:")
            password_input = st.text_input("Enter Password:", type="password")
            if st.button("Log In", use_container_width=True):
                valid_users = USER_CREDENTIALS[role_choice]
                if username_input in valid_users and valid_users[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user_role = role_choice
                    st.session_state.username = username_input
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID or Password.")

else:
    # A. CITIZEN WORKSPACE
    if st.session_state.user_role == "Citizen":
        st.header("📢 Public Complaint Feed")
        st.write(f"Signed in as **{st.session_state.username}** (`{st.session_state.citizen_phone}`).")

        if ai_engine_status() == "live":
            st.caption("🤖 AI Triage: **Live** — each submission is read and understood by Claude to decide Govt vs. University routing.")
        else:
            st.caption("🤖 AI Triage: **Keyword fallback** — no `ANTHROPIC_API_KEY` configured, so routing uses simpler keyword matching instead of real understanding.")

        with st.form("citizen_form", clear_on_submit=True):
            title = st.text_input("Issue Title", placeholder="e.g., Pothole clearing on main road OR IoT flood sensor system design")
            description = st.text_area("Issue Description", placeholder="Describe the problem...")
            location = st.text_input("Location / District", placeholder="e.g., MG Road, Kochi")
            submitted = st.form_submit_button("Submit Complaint")

            if submitted and title and description:
                category = categorize_issue(description)
                ai_target, ai_department, ai_reasoning = ai_classify_issue(title, description)
                new_id = f"ISSUE-10{len(st.session_state.issues) + 1}"
                submitter_info = f"{st.session_state.username} ({st.session_state.citizen_phone})"
                
                st.session_state.issues.append({
                    "id": new_id,
                    "title": title,
                    "description": description,
                    "category": category,
                    "location": location if location else "Not Specified",
                    "status": "Open" if "University-Eligible" in ai_target else "Direct Govt Action Required",
                    "submitted_by": submitter_info,
                    "assigned_to": None,
                    "department": None,
                    "milestone": "Awaiting Adoption" if "University-Eligible" in ai_target else "Assigned for Physical Execution",
                    "funding_status": "Not Requested",
                    "grant_amount": "₹0",
                    "proof_work": "",
                    "mentor_name": "",
                    "mentor_phone": "",
                    "num_students": 0,
                    "student_team": [],
                    "ai_target": ai_target,
                    "ai_department": ai_department,
                    "ai_reasoning": ai_reasoning
                })
                
                if "University-Eligible" in ai_target:
                    st.success(f"✅ Submitted! **AI Triage:** [{ai_target} → {ai_department}]")
                else:
                    st.success(f"✅ Submitted! **AI Triage:** [{ai_target}]")
                st.info(f"🤖 **AI Analysis:** {ai_reasoning}")

        st.divider()
        st.subheader("📊 Community Tracker")
        df = pd.DataFrame(st.session_state.issues)
        display_cols = ["id", "title", "category", "ai_target", "ai_department", "location", "status"]
        st.dataframe(df[display_cols], use_container_width=True)

    # B. UNIVERSITY WORKSPACE
    elif st.session_state.user_role == "University / Research Institute":
        st.header("🎓 University Innovation Portal")
        st.write(f"Logged in as **{st.session_state.username}**.")
        
        univ_issues = [i for i in st.session_state.issues if "University-Eligible" in i.get("ai_target", "")]
        
        engine_note = (
            "Each issue is read and understood by Claude to judge whether it needs a real idea/solution."
            if ai_engine_status() == "live"
            else "No `ANTHROPIC_API_KEY` configured — currently using simpler keyword matching, not real understanding."
        )
        st.info(f"🤖 **AI Triage Active ({ai_engine_status()}):** {engine_note} Routine physical work (pothole clearing, manual garbage removal, etc.) is routed straight to Government Officials and hidden from this R&D portal.")

        if not univ_issues:
            st.warning("No practical R&D challenges currently open for university development.")
        else:
            all_depts = sorted({i["ai_department"] for i in univ_issues if i.get("ai_department")})
            dept_filter = st.selectbox("Filter by R&D Department:", ["All Departments"] + all_depts)

            filtered = univ_issues if dept_filter == "All Departments" else [
                i for i in univ_issues if i.get("ai_department") == dept_filter
            ]

            st.markdown(f"**{len(filtered)} practical R&D project(s)** matching this view.")
            st.divider()

            for issue in filtered:
                current_status = issue.get("status")
                with st.container(border=True):
                    st.markdown(f"<span class='dept-pill'>{issue.get('ai_department')}</span>", unsafe_allow_html=True)
                    st.markdown(f"#### {issue['title']}  \n`{issue['id']}` · {issue['location']}")
                    st.write(issue["description"])
                    st.caption(f"🤖 AI reasoning: {issue['ai_reasoning']}")

                    if current_status == "Pending Govt Approval":
                        st.warning(f"⏳ **Adoption Requested by {issue['assigned_to']}** ({issue.get('department')}) — Awaiting Government Sanction & Grant Allocation ({issue.get('grant_amount')}).")
                        if issue.get("mentor_name"):
                            st.caption(f"Mentor: {issue['mentor_name']} ({issue.get('mentor_phone', 'n/a')}) · {issue.get('num_students', 0)} student(s) on the team")
                    elif current_status in ["In Progress", "Approved"]:
                        st.success(f"✅ **Approved & Assigned to {issue['assigned_to']}** — Department: {issue.get('department')}")
                        if issue.get("mentor_name"):
                            st.caption(f"Mentor: {issue['mentor_name']} ({issue.get('mentor_phone', 'n/a')}) · {issue.get('num_students', 0)} student(s) on the team")
                    else:
                        accept_key = f"accepting_{issue['id']}"
                        if accept_key not in st.session_state:
                            st.session_state[accept_key] = False

                        if not st.session_state[accept_key]:
                            st.write("")
                            if st.button("✅ We Will Solve This — Accept Issue", key=f"accept_{issue['id']}", use_container_width=True):
                                st.session_state[accept_key] = True
                                st.rerun()
                        else:
                            st.success("You've accepted this issue. Please provide the project details below to confirm your adoption request.")
                            dept_options = list(DEPARTMENT_KEYWORDS.keys())
                            default_depts = [issue["ai_department"]] if issue.get("ai_department") in dept_options else []
                            chosen_depts = st.multiselect(
                                "Department(s) taking this on (select more than one for an interdisciplinary team):",
                                dept_options,
                                default=default_depts,
                                key=f"dept_choice_{issue['id']}"
                            )
                            grant_req = st.selectbox(
                                "Requested R&D Grant:",
                                ["₹25,000", "₹50,000", "₹1,00,000", "₹2,50,000"],
                                key=f"grant_req_{issue['id']}"
                            )

                            st.markdown("**Mentor Details**")
                            col_m1, col_m2 = st.columns(2)
                            with col_m1:
                                mentor_name = st.text_input("Mentor Full Name:", key=f"mentor_name_{issue['id']}")
                            with col_m2:
                                mentor_phone = st.text_input("Mentor 10-Digit Phone Number:", max_chars=10, key=f"mentor_phone_{issue['id']}")

                            st.markdown("**Student Team Details**")
                            num_students = st.number_input(
                                "Number of Students in Project:",
                                min_value=1, max_value=15, value=1, step=1,
                                key=f"num_students_{issue['id']}"
                            )

                            student_team = []
                            for s_idx in range(int(num_students)):
                                col_sn, col_sr = st.columns(2)
                                with col_sn:
                                    s_name = st.text_input(f"Student {s_idx + 1} Name:", key=f"student_name_{issue['id']}_{s_idx}")
                                with col_sr:
                                    s_roll = st.text_input(f"Student {s_idx + 1} Roll Number:", key=f"student_roll_{issue['id']}_{s_idx}")
                                student_team.append({"name": s_name, "roll_number": s_roll})

                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                confirm_clicked = st.button("Confirm & Send Adoption Request", key=f"adopt_{issue['id']}", use_container_width=True)
                            with col_cancel:
                                cancel_clicked = st.button("Cancel", key=f"cancel_{issue['id']}", use_container_width=True)

                            if cancel_clicked:
                                st.session_state[accept_key] = False
                                st.rerun()

                            if confirm_clicked:
                                missing = []
                                if not chosen_depts:
                                    missing.append("at least one department")
                                if not mentor_name.strip():
                                    missing.append("mentor name")
                                if not (mentor_phone.strip().isdigit() and len(mentor_phone.strip()) == 10):
                                    missing.append("a valid 10-digit mentor phone number")
                                if any(not s["name"].strip() or not s["roll_number"].strip() for s in student_team):
                                    missing.append("name & roll number for every listed student")

                                if missing:
                                    st.error(f"❌ Please provide: {', '.join(missing)}.")
                                else:
                                    for stored in st.session_state.issues:
                                        if stored["id"] == issue["id"]:
                                            stored["assigned_to"] = st.session_state.username
                                            stored["department"] = ", ".join(chosen_depts)
                                            stored["status"] = "Pending Govt Approval"
                                            stored["milestone"] = f"Adoption Requested by {st.session_state.username}"
                                            stored["funding_status"] = "Grant Pending Approval"
                                            stored["grant_amount"] = grant_req
                                            stored["mentor_name"] = mentor_name.strip()
                                            stored["mentor_phone"] = mentor_phone.strip()
                                            stored["num_students"] = int(num_students)
                                            stored["student_team"] = student_team
                                    st.session_state[accept_key] = False
                                    st.success(f"Request sent to Government Officials for {grant_req} grant approval!")
                                    st.rerun()

    # C. GOVERNMENT OFFICIAL WORKSPACE
    elif st.session_state.user_role == "Government Official":
        st.header("🏛️ Government Official Portal & Action Hub")
        st.write(f"Logged in as **{st.session_state.username}**.")
        
        pending_requests = [i for i in st.session_state.issues if i.get("status") == "Pending Govt Approval"]
        physical_work_issues = [i for i in st.session_state.issues if "Govt-Direct" in i.get("ai_target", "")]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📥 Pending R&D Grants", len(pending_requests))
        col2.metric("🚧 Physical Maintenance Items", len(physical_work_issues))
        col3.metric("📊 Total System Issues", len(st.session_state.issues))

        st.divider()

        tab1, tab2, tab3 = st.tabs(["📥 Pending University R&D Requests", "🚧 Direct Physical Maintenance Queue", "📊 All System Issues"])

        with tab1:
            st.subheader("University R&D Project & Grant Approvals")
            if not pending_requests:
                st.info("No pending university adoption requests currently requiring approval.")
            else:
                for issue in pending_requests:
                    with st.container(border=True):
                        col_info, col_actions = st.columns([3, 2])
                        with col_info:
                            st.markdown(f"<span class='dept-pill'>{issue.get('department')}</span>", unsafe_allow_html=True)
                            st.markdown(f"#### {issue['title']} (`{issue['id']}`)")
                            st.write(f"**Adopting University:** `{issue['assigned_to']}`")
                            st.write(f"**Location:** {issue['location']} | **Requested Grant:** **{issue['grant_amount']}**")
                            st.caption(f"Description: {issue['description']}")

                            mentor_name = issue.get("mentor_name")
                            mentor_phone = issue.get("mentor_phone")
                            student_team = issue.get("student_team") or []
                            if mentor_name or student_team:
                                st.markdown("**Project Team**")
                                if mentor_name:
                                    st.write(f"Mentor: **{mentor_name}** ({mentor_phone or 'no phone on file'})")
                                if student_team:
                                    team_df = pd.DataFrame(student_team).rename(columns={"name": "Student Name", "roll_number": "Roll Number"})
                                    st.dataframe(team_df, use_container_width=True, hide_index=True)
                        
                        with col_actions:
                            st.write("**Government Action:**")
                            if st.button("✅ Approve Grant & Assign", key=f"approve_{issue['id']}", use_container_width=True):
                                for stored in st.session_state.issues:
                                    if stored["id"] == issue["id"]:
                                        stored["status"] = "In Progress"
                                        stored["milestone"] = f"Approved & Funded ({issue['grant_amount']}) for {issue['assigned_to']}"
                                        stored["funding_status"] = "Sanctioned & Allocated"
                                st.success(f"Approved adoption request for {issue['assigned_to']}!")
                                st.rerun()

                            if st.button("❌ Reject / Re-open Issue", key=f"reject_{issue['id']}", use_container_width=True):
                                for stored in st.session_state.issues:
                                    if stored["id"] == issue["id"]:
                                        stored["status"] = "Open"
                                        stored["assigned_to"] = None
                                        stored["milestone"] = "Awaiting Adoption"
                                        stored["funding_status"] = "Not Requested"
                                        stored["grant_amount"] = "₹0"
                                        stored["mentor_name"] = ""
                                        stored["mentor_phone"] = ""
                                        stored["num_students"] = 0
                                        stored["student_team"] = []
                                st.warning(f"Rejected request for {issue['id']}. Returned to public pool.")
                                st.rerun()

        with tab2:
            st.subheader("Direct Municipal Physical Maintenance Queue")
            st.write("Issues requiring immediate manual/physical execution (potholes, garbage, routine structural repairs).")
            if not physical_work_issues:
                st.info("No physical maintenance tasks currently open.")
            else:
                for issue in physical_work_issues:
                    with st.container(border=True):
                        st.markdown(f"<span class='govt-pill'>PHYSICAL MAINTENANCE DIRECT</span>", unsafe_allow_html=True)
                        st.markdown(f"#### {issue['title']} (`{issue['id']}`) — {issue['location']}")
                        st.write(issue['description'])
                        st.caption(f"🤖 AI Triage: {issue['ai_reasoning']}")

        with tab3:
            st.subheader("Complete Municipal Master Database")
            df = pd.DataFrame(st.session_state.issues)
            display_cols = ["id", "title", "category", "ai_target", "assigned_to", "status", "funding_status", "grant_amount"]
            st.dataframe(df[display_cols], use_container_width=True)

    # D. PLATFORM ADMIN WORKSPACE
    elif st.session_state.user_role == "Platform Administrator":
        st.header("📈 Platform Operations Workspace")
        st.write(f"Logged in as **{st.session_state.username}**.")

        with st.expander("🔄 Demo / Testing Controls"):
            st.caption("Streamlit keeps issue data in-session — code changes to the seed list won't appear in an already-open browser session. Use this to reset instantly without restarting the server (handy for live demos).")
            confirm_reset = st.checkbox("I understand this will erase any issues added during this session.")
            if st.button("Reset to Demo Seed Data", disabled=not confirm_reset):
                st.session_state.issues = [dict(issue) for issue in SEED_ISSUES]
                st.success(f"Reset complete — {len(SEED_ISSUES)} seed issues restored.")
                st.rerun()

        df = pd.DataFrame(st.session_state.issues)
        st.dataframe(df, use_container_width=True)