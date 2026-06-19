"""
classifier.py
-------------
Determines which of the three customer personas a message belongs to,
using Gemini structured JSON output so we get a reliable, parseable result
instead of free-form text we'd have to regex out.
"""

import json
from google import genai
from google.genai import types

from . import config
from .utils import call_with_backoff

SYSTEM_INSTRUCTION = (
    "You are an advanced classification engine. Your task is to analyze the "
    "sentiment, vocabulary, and tone of an incoming support message and classify "
    "it into exactly one of three customer personas:\n"
    "1. 'Technical Expert': Uses jargon, asks about APIs/code/configs.\n"
    "2. 'Frustrated User': Uses emotional language, exclamation marks, or mentions urgency.\n"
    "3. 'Business Executive': Focuses on business impact, ROI, timelines, and brevity.\n\n"
    "Provide your evaluation strictly in the requested JSON structure."
)

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "persona": {
            "type": "STRING",
            "enum": config.PERSONAS,
        },
        "confidence": {"type": "NUMBER"},
        "reasoning": {"type": "STRING"},
    },
    "required": ["persona", "confidence", "reasoning"],
}


def classify_customer_persona(user_message: str) -> dict:
    """
    Analyzes the user's message and classifies it into one of the three
    target personas. Returns a dict: {persona, confidence, reasoning}.
    Retries automatically on transient API errors before falling back.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    try:
        response = call_with_backoff(
            client.models.generate_content,
            model=config.GENERATION_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.1,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "persona": "Frustrated User",
            "confidence": 0.0,
            "reasoning": f"Classifier error, defaulted to safest persona: {e}",
        }


if __name__ == "__main__":
    test_msg = (
        "Our production API key stopped working with a 401 Unauthorized "
        "error. Check our logs immediately."
    )
    result = classify_customer_persona(test_msg)
    print(json.dumps(result, indent=2))