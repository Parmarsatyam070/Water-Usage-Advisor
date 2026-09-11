# 👤 Persona 1: Residential Homeowner
**Identifier:** Persona_1_HomeOwner  
**User Archetype:** Suburban / Urban Residential Consumer  
**Target Group:** Single-family & Multi-family households

---

## 1. Profile Overview
- **Name Archetype:** Sarah Jenkins
- **Role:** Homeowner & Primary Household Bill Manager
- **Household Context:** 4-person family (2 adults, 2 school-age children) living in a 3-bedroom detached house with a small lawn and modern domestic appliances (washing machine, dishwasher).
- **Technical Comfort:** Moderate (Comfortable with smartphone mobile apps, web portals, and online banking; non-technical with code or plumbing infrastructure).

---

## 2. Core Goals
1. **Reduce Utility Expenses:** Lower the quarterly water bill by 20% by cutting wasteful outdoor watering and identifying phantom domestic leaks.
2. **Prevent Property Damage:** Receive instant, unambiguous alerts if an uncharacteristic water leak or burst pipe occurs while away from home.
3. **Environmental Stewardship:** Instill conservation values in the family and contribute to community sustainability goals (SDG 6).

---

## 3. Key Pain Points
- **Delayed Feedback:** Only discovers high consumption weeks later when opening the monthly utility bill.
- **Inability to Diagnose Leaks:** Has no way to know whether a higher bill is due to normal summer heat, extra laundry, or a faulty toilet flapper valve.
- **Generic Utility Advice:** Frustrated by patronizing advice (e.g., "Don't leave the tap running") that doesn't account for household occupancy or fixture types.

---

## 4. Water-Management Needs
- A visual breakdown of where water is consumed (bathrooms vs. kitchen vs. irrigation).
- Proactive alerts on persistent low-flow anomalies (e.g., continuous 15 L/hr overnight).
- Clear financial impact estimates (e.g., *"Fixing this toilet leak could save you \$35/month"*).

---

## 5. Expected Application Features
1. **At-a-Glance Dashboard:** Visualizing today's consumption vs. normal baseline and progress toward monthly targets.
2. **AI Water Chatbot:** Ability to ask conversational questions like: *"Why is my water bill higher this week?"* or *"How can I lower my garden water usage?"*
3. **Actionable Recommendations:** Step-by-step DIY diagnostic checklists for common household fixtures.

---

## 6. Key User Journey
```mermaid
sequenceDiagram
    autonumber
    actor Sarah as Sarah (Homeowner)
    participant App as Smart Water Advisor
    participant AI as AI Advisor / Chatbot

    Sarah->>App: Opens Dashboard on morning notification
    App-->>Sarah: Displays "Unusual Overnight Flow Alert (12 L/hr)"
    Sarah->>AI: "Why did I use water between 2:00 AM and 5:00 AM?"
    AI-->>Sarah: "We detected continuous low flow. 85% of similar patterns are caused by a leaking toilet flapper. Here is a 3-minute food-coloring check."
    Sarah->>Sarah: Performs test, replaces flapper ($6)
    Sarah->>App: Checks dashboard next morning; flow returned to zero
    App-->>Sarah: "Great job! You avoided an estimated 280 L of waste today."
```

---

## 7. Success Criteria
- Immediate resolution of plumbing leaks within 24 hours of alert trigger.
- Achievement of 15–25% water reduction over a 60-day billing cycle.
- User satisfaction rating of 5/5 for conversational clarity and ease of use.
