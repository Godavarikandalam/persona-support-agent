try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass  # not available locally on Windows - only needed on the cloud server

"""
app.py
------
Streamlit chat UI that wires together: classifier -> RAG retrieval ->
escalation check -> adaptive generator. Run with: streamlit run app.py
"""

import streamlit as st

from src import config
from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.generator import generate_adaptive_response
from src.escalator import check_escalation, generate_handoff_summary

st.set_page_config(page_title="Persona-Adaptive Support Agent", page_icon="🎧")
st.title("🎧 Persona-Adaptive Customer Support Agent")
st.caption(
    "Classifies your communication style, retrieves relevant help-desk docs, "
    "and adapts its tone accordingly — or escalates to a human when it can't help safely."
)


@st.cache_resource(show_spinner="Loading knowledge base...")
def get_pipeline():
    pipeline = LocalRAGPipeline()
    # Only (re)ingest if the collection is empty, so we don't re-embed
    # every file on every Streamlit rerun.
    if pipeline.collection.count() == 0:
        pipeline.ingest_directory("data")
    return pipeline


pipeline = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "consecutive_frustration" not in st.session_state:
    st.session_state.consecutive_frustration = 0

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a support question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Classify persona
            classification = classify_customer_persona(user_input)
            persona = classification["persona"]

            if persona == "Frustrated User":
                st.session_state.consecutive_frustration += 1
            else:
                st.session_state.consecutive_frustration = 0

            # 2. Retrieve relevant context
            context_chunks = pipeline.retrieve_context(user_input, top_k=config.TOP_K)

            # 3. Escalation check
            escalation = check_escalation(
                user_input,
                persona,
                context_chunks,
                st.session_state.consecutive_frustration,
            )

            if escalation["escalate"]:
                handoff_json = generate_handoff_summary(
                    user_input, persona, context_chunks, escalation["reason"]
                )
                answer = (
                    "I'm not able to fully resolve this on my own, so I'm connecting "
                    "you with a human support specialist who can help further."
                )
                st.markdown(answer)
                with st.expander("🔧 Human handoff details (internal)"):
                    st.code(handoff_json, language="json")
            else:
                # 4. Generate persona-adapted response
                result = generate_adaptive_response(user_input, persona, context_chunks)
                answer = result["response"]
                st.markdown(answer)
                with st.expander("ℹ️ Debug info (persona + sources)"):
                    st.write(f"**Persona:** {persona} (confidence: {classification.get('confidence', 'n/a')})")
                    st.write(f"**Reasoning:** {classification.get('reasoning', 'n/a')}")
                    st.write("**Sources used:**")
                    for c in context_chunks:
                        st.write(f"- {c['source']} (score: {c['score']:.2f})")

    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    st.subheader("How it works")
    st.markdown(
        "1. Your message is classified into a persona: **Technical Expert**, "
        "**Frustrated User**, or **Business Executive**.\n"
        "2. Relevant help-desk docs are retrieved via vector similarity search.\n"
        "3. If confidence is low or the topic is sensitive (billing/legal), "
        "the conversation is escalated to a human.\n"
        "4. Otherwise, a response is generated in a tone matched to your persona."
    )
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.session_state.consecutive_frustration = 0
        st.rerun()
