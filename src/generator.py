"""
generator.py
------------
Takes the classified persona + retrieved context chunks and produces the
final, persona-flavored answer. This is where the "adaptive" part of the
system actually shows up to the customer.
"""

from google import genai
from google.genai import types

from . import config
from .utils import call_with_backoff

PERSONA_INSTRUCTIONS = {
    "Technical Expert": (
        "You are a Senior Systems Engineer. Provide clear root-cause analysis, "
        "configuration specifics, and precise API pathways or code blocks where "
        "relevant. Keep technical descriptions exact and structured. Do not "
        "oversimplify or add unnecessary reassurance."
    ),
    "Frustrated User": (
        "You are a deeply empathetic, reassuring Customer Care Specialist. "
        "Begin with a warm, genuine acknowledgment of their difficulty. Use "
        "straightforward, simple action-oriented bullet steps. Avoid jargon, "
        "avoid sounding scripted, and keep the tone calm and human."
    ),
    "Business Executive": (
        "You are a concise Client Relations Director. Lead with the direct "
        "answer, then the business impact and a resolution timeline. Keep the "
        "response short, professional, and skip implementation details unless "
        "explicitly asked."
    ),
}


def build_system_prompt(persona: str, context_chunks: list) -> str:
    """Assemble the full grounding + persona-styling system prompt."""
    persona_instructions = PERSONA_INSTRUCTIONS.get(
        persona, PERSONA_INSTRUCTIONS["Frustrated User"]
    )

    context_text = "\n\n".join(
        f"Source [{c['source']}]: {c['text']}" for c in context_chunks
    )

    return (
        f"{persona_instructions}\n\n"
        "CRITICAL RULES:\n"
        "- Base your response ONLY on the provided context documents below.\n"
        "- If the context does not fully answer the question, say so honestly "
        "instead of guessing.\n"
        "- Do not hallucinate facts, prices, or policies not found in the documents.\n\n"
        f"FACTUAL CONTEXT DOCUMENTS:\n{context_text}"
    )


def generate_adaptive_response(user_query: str, persona: str, context_chunks: list) -> dict:
    """
    Generate the persona-styled, context-grounded answer.
    Returns {response: str}. Retries automatically on transient API errors
    (like 503 overload) before giving up.
    """
    system_prompt = build_system_prompt(persona, context_chunks)
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    try:
        response = call_with_backoff(
            client.models.generate_content,
            model=config.GENERATION_MODEL,
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            ),
        )
        return {"response": response.text}
    except Exception as e:
        return {
            "response": (
                "I'm having trouble reaching the AI service right now (it may be "
                "temporarily overloaded). Please try asking again in a moment.\n\n"
                f"_Technical detail: {e}_"
            )
        }