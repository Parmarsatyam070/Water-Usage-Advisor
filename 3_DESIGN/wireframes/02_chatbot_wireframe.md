# 💬 Wireframe 02: AI Water Conservation Chatbot
**Document ID:** 02_chatbot_wireframe  
**Target View:** Conversational Advisor Drawer / Modal Interface  
**Status:** Phase 1 Design Specification (Non-production wireframe)

---

## 1. ASCII Layout Wireframe

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] Smart Water Usage Advisor > AI Advisor Assistant                                  [Close Drawer X] |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  CONTEXTUAL WATER INSIGHT BANNER                                                                        |
|  ℹ️ Grounded in: 4-person Household | Meter #MTR-8821 | Active Alert: Overnight Flow (14 L/hr)           |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
|  CONVERSATION AREA                                                                                      |
|                                                                                                         |
|  [AI ADVISOR - 10:14 AM]                                                                                |
|  Hello Sarah! I noticed an unusual continuous flow of 14 liters/hour between 02:00 AM and 05:00 AM     |
|  last night. Because this occurred when your household is normally asleep, this often indicates a       |
|  silent plumbing leak rather than intentional use.                                                      |
|                                                                                                         |
|  Would you like me to guide you through a 3-minute check to find the leak?                             |
|                                                                                                         |
|  [USER - 10:15 AM]                                                                                      |
|  Yes please! Could it be my toilet?                                                                     |
|                                                                                                         |
|  [AI ADVISOR - 10:15 AM] (Response Latency: 1.1s)                                                       |
|  Yes, absolutely. Leaking toilet flappers account for over 80% of silent residential night leaks.       |
|                                                                                                         |
|  Here is a quick, zero-cost test:                                                                       |
|  1. Put 4-5 drops of dark food coloring in your toilet tank (do not flush).                            |
|  2. Wait 15 minutes.                                                                                    |
|  3. If colored water appears in the bowl, your flapper valve is worn out and leaking.                   |
|                                                                                                         |
|  RECOMMENDATION GENERATED:                                                                              |
|  +---------------------------------------------------------------------------------------------------+  |
|  | Title: Replace Toilet Flapper Valve                                                               |  |
|  | Potential Impact: Saves ~336 L/day | Est. Utility Savings: $35.00/month                            |  |
|  | [Add to Action List]   [Dismiss]                                                                 |  |
|  +---------------------------------------------------------------------------------------------------+  |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
|  SUGGESTED QUESTIONS (QUICK PROMPTS)                                                                    |
|  [ "Why is my bill higher this month?" ]  [ "How does my usage compare to neighbors?" ]                |
|  [ "What are 3 quick water saving tips for gardens?" ]  [ "Explain my 7-day forecast" ]                 |
+---------------------------------------------------------------------------------------------------------+
|  INPUT AREA                                                                                             |
|  [ Ask your Water Advisor a question... (e.g. 'How can I save water on laundry?')            ] [ Send ➤ ]|
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Contextual Insight Header
- Displays active meter ID, household occupancy, and relevant active alerts so the user understands that the AI is grounded in their real data.

### 2.2 Chat Bubble Layout
- Clear visual distinction between user messages and AI Advisor responses.
- Displays response timestamps and latency indicators.

### 2.3 Interactive Recommendation Cards
- Embedded cards within the conversation stream that translate conversational guidance directly into actionable goals stored in the database (`recommendations` table).

### 2.4 Suggested Quick Prompts
- Horizontally scrollable chips offering common high-intent questions, reducing typing friction.
