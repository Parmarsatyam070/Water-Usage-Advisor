"""
Smart Water Usage Advisor - Curated Water Conservation Knowledge Base
Location: 5_AI_COMPONENTS/chatbot/knowledge_base.py
Phase 3C - Week 6 Implementation

Provides an evidence-grounded, structured repository of practical water conservation
guidance for residential, institutional, and municipal water users.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class KnowledgeEntry:
    """Structured knowledge base entry for water conservation."""
    id: str
    topic: str
    title: str
    category: str
    content: str
    savings_estimate_liters_day: float
    difficulty: str = "easy"  # easy, medium, hard
    priority: str = "medium"   # critical, high, medium, low
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Comprehensive curated knowledge catalog (16 authoritative entries)
CURATED_KNOWLEDGE_ENTRIES = [
    KnowledgeEntry(
        id="KB-001",
        topic="toilet_leaks",
        title="Diagnosing and Fixing Toilet Flapper Valve Leaks",
        category="plumbing_troubleshooting",
        content="A leaking toilet flapper is the single most common cause of high residential water bills, typically wasting between 100 to 1,000 liters per day without audible noise. To test: place 5 drops of food coloring in the toilet cistern tank and do not flush. If color appears in the bowl within 15 minutes, the rubber flapper valve is deteriorated and must be replaced. Replacement flappers cost under $10 at hardware stores and take 10 minutes to install.",
        savings_estimate_liters_day=350.0,
        difficulty="easy",
        priority="high",
        keywords=["toilet", "flapper", "silent leak", "food coloring test", "night flow", "running toilet", "cistern"]
    ),
    KnowledgeEntry(
        id="KB-002",
        topic="shower_efficiency",
        title="Optimizing Shower Water Consumption with Aerated Heads",
        category="bathroom_savings",
        content="Showers represent roughly 20% of indoor residential water consumption. Standard older showerheads deliver 9.5 to 12.0 liters per minute (LPM). EPA WaterSense certified low-flow aerated showerheads operate at 5.7 to 7.5 LPM, reducing shower water use by 30-40% without compromising water pressure sensation. Reducing shower duration by 2 minutes per person saves an additional 15 to 20 liters per session.",
        savings_estimate_liters_day=80.0,
        difficulty="easy",
        priority="medium",
        keywords=["shower", "aerator", "WaterSense", "bathroom", "showerhead", "duration", "bath"]
    ),
    KnowledgeEntry(
        id="KB-003",
        topic="irrigation_timing",
        title="Evaporation Mitigation in Landscape & Garden Irrigation",
        category="outdoor_conservation",
        content="Watering lawns and gardens during mid-day (10:00 AM to 4:00 PM) results in up to 30-40% water loss due to solar heat and atmospheric wind evaporation. Scheduling irrigation between 4:00 AM and 7:00 AM allows water to penetrate deep into root zones before heat rises. Utilizing drip irrigation systems for shrub and garden beds reduces water volume by 50% compared to overhead sprinklers.",
        savings_estimate_liters_day=200.0,
        difficulty="medium",
        priority="medium",
        keywords=["irrigation", "garden", "lawn", "evaporation", "sprinkler", "drip", "watering", "plants", "outdoor"]
    ),
    KnowledgeEntry(
        id="KB-004",
        topic="night_flow_rule",
        title="Minimum Night Flow Rule for Early Leak Detection",
        category="leak_analytics",
        content="In domestic residences, water consumption typically drops to zero for extended intervals between 1:00 AM and 5:00 AM when occupants are asleep. A persistent non-zero flow rate (greater than 5 L/hr) for two or more continuous nocturnal hours indicates continuous water escape (e.g. running toilet, cracked irrigation main line, or leaking relief valve). Flagging this condition allows repair before catastrophic drywall or foundation damage occurs.",
        savings_estimate_liters_day=400.0,
        difficulty="easy",
        priority="high",
        keywords=["night flow", "continuous leak", "MNF", "zero flow", "anomaly", "overnight", "nocturnal", "baseline"]
    ),
    KnowledgeEntry(
        id="KB-005",
        topic="faucet_aerators",
        title="Faucet Aerators for Kitchen and Bathroom Sinks",
        category="domestic_efficiency",
        content="Standard kitchen and bathroom faucets flow at approximately 8.3 LPM. Screwing on simple multi-mesh aerators reduces flow rate to 3.8 to 5.7 LPM for bathroom sinks and 6.8 LPM for kitchen sinks. This saves approximately 20-30 liters per household per day while maintaining strong rinsing pressure.",
        savings_estimate_liters_day=25.0,
        difficulty="easy",
        priority="low",
        keywords=["faucet", "aerator", "sink", "kitchen", "tap", "bathroom sink", "flow rate"]
    ),
    KnowledgeEntry(
        id="KB-006",
        topic="sdg_6_targets",
        title="UN Sustainable Development Goal 6 Metrics & Targets",
        category="sustainability_education",
        content="UN SDG 6 aims to ensure availability and sustainable management of water and sanitation for all by 2030. Target 6.4 specifically calls on all sectors to substantially increase water-use efficiency and ensure sustainable withdrawals of freshwater. By helping households and institutions eliminate leaks and cut non-essential usage by 20-30%, digital smart water advisors directly support Target 6.4.",
        savings_estimate_liters_day=0.0,
        difficulty="easy",
        priority="low",
        keywords=["SDG 6", "Clean Water", "sustainability", "United Nations", "Target 6.4", "efficiency", "freshwater"]
    ),
    KnowledgeEntry(
        id="KB-007",
        topic="dishwashing_efficiency",
        title="Dishwasher Efficiency: Full Loads vs. Manual Hand Washing",
        category="kitchen_savings",
        content="Washing dishes under a continuously running kitchen tap consumes roughly 60 to 100 liters per session. Modern Energy Star / WaterSense certified dishwashers consume only 11 to 15 liters per complete cycle. Running the dishwasher only with full loads and scraping plates instead of pre-rinsing under the tap saves approximately 50 liters per cycle.",
        savings_estimate_liters_day=45.0,
        difficulty="easy",
        priority="medium",
        keywords=["dishwasher", "kitchen", "dishes", "hand washing", "running tap", "full load", "rinse"]
    ),
    KnowledgeEntry(
        id="KB-008",
        topic="laundry_efficiency",
        title="High-Efficiency Laundry Practices & Load Optimization",
        category="laundry_savings",
        content="Washing machines account for roughly 15-20% of indoor residential water use. Older top-load washers consume 110 to 150 liters per load, whereas modern front-load high-efficiency (HE) machines use 45 to 65 liters. Adjusting water level settings to match laundry size, running full loads, and utilizing cold-water cycles saves 30-50 liters per wash cycle.",
        savings_estimate_liters_day=40.0,
        difficulty="easy",
        priority="medium",
        keywords=["laundry", "washing machine", "clothes", "wash cycle", "high efficiency", "full load"]
    ),
    KnowledgeEntry(
        id="KB-009",
        topic="pipe_burst_emergency",
        title="Emergency Response for Sudden Pipe Bursts and Catastrophic Surges",
        category="emergency_procedures",
        content="A sudden spike exceeding 200-400 L/hr indicates a critical line breach, burst pipe, or disconnected flex hose. Immediate action: 1) Locate and shut off the main property water isolation valve immediately. 2) Turn off electrical breakers if flooding is near wiring or appliances. 3) Open lowest faucets to drain remaining line pressure. 4) Contact a licensed plumbing professional immediately.",
        savings_estimate_liters_day=1000.0,
        difficulty="hard",
        priority="critical",
        keywords=["burst", "pipe burst", "catastrophic", "surge", "main valve", "shutoff", "flooding", "emergency", "plumber"]
    ),
    KnowledgeEntry(
        id="KB-010",
        topic="rainwater_harvesting",
        title="Rainwater Harvesting & Rain Barrel Systems for Outdoor Watering",
        category="outdoor_conservation",
        content="Installing a 200-liter rain barrel connected to gutter downspouts captures roof runoff during precipitation events. This chlorine-free water is ideal for garden irrigation, potted plants, and outdoor washing. A 100-square-meter roof yields approximately 2,500 liters of water during a 25mm rainfall event, offsetting municipal tap water demand.",
        savings_estimate_liters_day=50.0,
        difficulty="medium",
        priority="low",
        keywords=["rainwater", "rain barrel", "harvesting", "gutters", "downspout", "outdoor", "irrigation", "runoff"]
    ),
    KnowledgeEntry(
        id="KB-011",
        topic="telemetry_interpretation",
        title="Interpreting Smart Water Meter Telemetry & Diurnal Profiles",
        category="consumption_analytics",
        content="Smart water meters record hourly volume (L/hr). Residential profiles typically show two distinct peaks: morning (07:00–09:00 for showers and breakfast) and evening (18:00–21:00 for cooking and laundry), with near-zero flow between 01:00 and 04:00. Commercial facilities peak between 09:00 and 17:00 on weekdays with flat weekend baselines. Recognizing these profiles helps identify abnormal deviations early.",
        savings_estimate_liters_day=0.0,
        difficulty="easy",
        priority="low",
        keywords=["smart meter", "telemetry", "diurnal", "consumption", "peaks", "hourly", "profile", "reading"]
    ),
    KnowledgeEntry(
        id="KB-012",
        topic="vacation_monitoring",
        title="Vacation & Property Vacancy Water Monitoring",
        category="leak_analytics",
        content="When properties are vacant during travel or seasonal shutdowns, water consumption should remain strictly zero. Any flow recorded during planned vacancy signals an unmanaged leak, running toilet, or unauthorized usage. Conversely, unexpected continuous zero flow during regular occupancy can indicate meter communication loss or sensor freeze.",
        savings_estimate_liters_day=150.0,
        difficulty="easy",
        priority="medium",
        keywords=["vacation", "vacancy", "away", "unoccupied", "zero consumption", "travel", "leak"]
    ),
    KnowledgeEntry(
        id="KB-013",
        topic="commercial_cooling_loops",
        title="Commercial Facility Cooling Towers & Off-Hour Baselines",
        category="commercial_efficiency",
        content="Commercial office buildings and campuses consume substantial water in HVAC cooling towers and closed hydronic loops. Unapproved nocturnal cycling or stuck solenoid valves during off-hours (00:00–04:00) waste thousands of liters. Routine cycle auditing and sub-metering of makeup water lines prevent evaporative drift and valve blow-by.",
        savings_estimate_liters_day=500.0,
        difficulty="hard",
        priority="high",
        keywords=["commercial", "cooling tower", "HVAC", "facility", "nocturnal", "campus", "chiller", "cycling"]
    ),
    KnowledgeEntry(
        id="KB-014",
        topic="goal_setting",
        title="Setting and Achieving Realistic Water Conservation Goals",
        category="behavioral_conservation",
        content="Setting a 15% to 20% water reduction target provides measurable sustainability progress without sacrificing comfort. Effective strategies include: 1) Tracking weekly totals against a fixed liter budget. 2) Addressing silent leaks first. 3) Converting non-essential lawn areas to drought-tolerant landscaping. 4) Celebrating household milestone achievements.",
        savings_estimate_liters_day=60.0,
        difficulty="easy",
        priority="medium",
        keywords=["goal", "target", "budget", "reduction", "percent", "savings", "tracking", "habit"]
    ),
    KnowledgeEntry(
        id="KB-015",
        topic="mulching_soil_retention",
        title="Mulching for Soil Moisture Retention and Evaporation Reduction",
        category="outdoor_conservation",
        content="Applying a 5 to 7 cm layer of organic mulch (wood bark, straw, compost) around garden beds and shrubs reduces soil water evaporation by up to 70%. Mulch moderates soil temperature, suppresses weeds that compete for moisture, and improves soil organic structure over time, cutting garden watering frequency by half.",
        savings_estimate_liters_day=35.0,
        difficulty="easy",
        priority="low",
        keywords=["mulch", "soil", "garden", "evaporation", "moisture", "plants", "drought", "weeds"]
    ),
    KnowledgeEntry(
        id="KB-016",
        topic="pressure_regulation",
        title="Water Pressure Regulation and Pressure Reducing Valves (PRV)",
        category="plumbing_troubleshooting",
        content="High municipal water supply pressure (exceeding 5.5 bar / 80 psi) stresses pipes, damages washing machine and dishwasher valves, and doubles flow rate through open faucets. Installing or adjusting a Pressure Reducing Valve (PRV) to maintain 3.5 to 4.0 bar (50-60 psi) extends plumbing lifespan and cuts overall household flow by 10-15%.",
        savings_estimate_liters_day=70.0,
        difficulty="hard",
        priority="medium",
        keywords=["pressure", "PRV", "valve", "psi", "bar", "pipes", "stress", "plumbing"]
    )
]


class WaterConservationKnowledgeBase:
    """
    In-memory, structured water conservation knowledge repository.
    Loads curated knowledge entries from JSON or the built-in catalog.
    """

    def __init__(self, json_path: Optional[str] = None):
        self.entries: Dict[str, KnowledgeEntry] = {}
        self._load_entries(json_path)

    def _load_entries(self, json_path: Optional[str] = None):
        # 1. Initialize with curated in-memory catalog
        for entry in CURATED_KNOWLEDGE_ENTRIES:
            self.entries[entry.id] = entry

        # 2. Check if custom JSON file is provided and merge
        if json_path and os.path.isfile(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        entry = KnowledgeEntry(
                            id=item.get("id", f"KB-{len(self.entries)+1:03d}"),
                            topic=item.get("topic", "general"),
                            title=item.get("title", "Water Conservation Advice"),
                            category=item.get("category", "general_conservation"),
                            content=item.get("content", ""),
                            savings_estimate_liters_day=float(item.get("savings_estimate_liters_day", 0.0)),
                            difficulty=item.get("difficulty", "easy"),
                            priority=item.get("priority", "medium"),
                            keywords=item.get("keywords", [])
                        )
                        self.entries[entry.id] = entry
            except Exception as e:
                print(f"Warning: Could not load knowledge JSON from {json_path}: {e}")

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieves a single entry by ID."""
        return self.entries.get(entry_id)

    def get_all_entries(self) -> List[KnowledgeEntry]:
        """Returns all knowledge entries."""
        return list(self.entries.values())

    def get_entries_by_category(self, category: str) -> List[KnowledgeEntry]:
        """Filters entries by category name."""
        return [e for e in self.entries.values() if e.category.lower() == category.lower()]

    def get_entries_by_topic(self, topic: str) -> List[KnowledgeEntry]:
        """Filters entries by topic."""
        return [e for e in self.entries.values() if e.topic.lower() == topic.lower()]

    def size(self) -> int:
        """Returns the number of entries in the knowledge base."""
        return len(self.entries)

    def to_list_of_dicts(self) -> List[Dict[str, Any]]:
        """Converts all entries to a list of dictionaries for JSON serialization."""
        return [e.to_dict() for e in self.entries.values()]
