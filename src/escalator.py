"""
escalator.py
------------
Decides whether the agent should answer directly or hand off to a human,
and builds the structured handoff payload when it does.

Three independent triggers (any one is enough to escalate):
  1. Retrieval confidence too low (the docs probably don't cover this).
  2. Sensitive topic keywords (billing, refunds, legal, account deletion).
  3. Repeated frustration across consecutive turns.
"""

import json
import re

from . import config


def is_sensitive_topic(user_query: str) -> bool:
    """Cheap keyword check for topics that should always go to a human,
    regardless of how confident the retrieval was. Uses word boundaries so
    short keywords (like "sue") don't accidentally match inside unrelated
    words (like "issue")."""
    lowered = user_query.lower()
    for keyword in config.SENSITIVE_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lowered):
            return True
    return False

def check_escalation(
    user_query: str,
    persona: str,
    context_chunks: list,
    consecutive_frustration_count: int = 0,
) -> dict:
    """
    Runs all three escalation checks and returns:
      {"escalate": bool, "reason": str | None}
    `consecutive_frustration_count` should be tracked by the caller (e.g. in
    Streamlit session_state) across turns of the same conversation.
    """
    best_score = max((c["score"] for c in context_chunks), default=0.0)

    if is_sensitive_topic(user_query):
        return {"escalate": True, "reason": "Sensitive topic detected (billing/legal/account)."}

    if best_score < config.RETRIEVAL_CONFIDENCE_THRESHOLD or not context_chunks:
        return {"escalate": True, "reason": f"Low retrieval confidence ({best_score:.2f})."}

    if (
        persona == "Frustrated User"
        and consecutive_frustration_count >= config.MAX_CONSECUTIVE_FRUSTRATION
    ):
        return {"escalate": True, "reason": "Repeated unresolved frustration across turns."}

    return {"escalate": False, "reason": None}


def generate_handoff_summary(
    user_query: str, persona: str, context_chunks: list, reason: str
) -> str:
    """Compile a structured JSON handoff report for the human agent."""
    handoff_data = {
        "persona": persona,
        "escalation_reason": reason,
        "detected_issue": user_query[:200] + ("..." if len(user_query) > 200 else ""),
        "retrieved_sources": [c["source"] for c in context_chunks],
        "confidence_score": max((c["score"] for c in context_chunks), default=0.0),
        "recommended_action": (
            "Review the retrieved sources (if any) for relevance, check whether "
            "the knowledge base needs a new article for this issue, and follow "
            "up with the customer directly."
        ),
    }
    return json.dumps(handoff_data, indent=2)
