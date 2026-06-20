# Persona-Adaptive Customer Support Agent

An intelligent customer support agent that classifies the customer's
communication persona (Technical Expert / Frustrated User / Business
Executive), retrieves grounding context from a local knowledge base using
RAG, adapts its tone to the persona, and escalates to a human agent when
confidence is low or the topic is sensitive.

## Architecture

```
[User Message] ──> [Persona Classifier] ──> [Persona Tag: Tech/Frustrated/Exec]
                        │
                        ▼
                [Vector Database] ──> [Cosine Similarity Search] ──> [Top-K Chunks]
                        │
                        ▼
            [Adaptive Prompt Engine] ──> (Retrieval Quality Check)
                        │                                  │
                        │ (Sufficient Info Found)          │ (Confidence Low / Sensitive Issue)
                        ▼                                  ▼
             [Generate Adaptive Response]         [Escalate to Human Agent]
                                                           │
                                                           ▼
                                                [Generate Handoff JSON]
```

## Project Structure

```
persona-support-agent/
├── data/                    # Knowledge base (.txt, .md, .pdf)
├── src/
│   ├── config.py            # Settings & thresholds
│   ├── classifier.py        # Persona detection
│   ├── rag_pipeline.py      # Chunking, embeddings, vector search
│   ├── generator.py         # Persona-adaptive prompt + LLM call
│   └── escalator.py         # Escalation logic + handoff JSON
├── app.py                   # Streamlit chat UI
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key:**
   ```bash
   cp .env.example .env
   # then edit .env and paste in your real key
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   On first run, it will automatically ingest everything in `data/` into a
   local persistent ChromaDB store (`./chroma_db/`). Subsequent runs reuse
   the existing index instead of re-embedding everything.

   To force a full re-index (e.g. after editing the knowledge base), delete
   the `chroma_db/` folder before restarting the app.

4. **(Optional) Test the RAG pipeline standalone before touching the UI:**
   ```bash
   python -m src.rag_pipeline
   ```
   This re-ingests `data/` and prints retrieved chunks + scores for a sample
   query, so you can sanity-check retrieval quality in isolation.

5. **(Optional) Test the classifier standalone:**
   ```bash
   python -m src.classifier
   ```

## How Escalation Works

The agent hands off to a human whenever any of these is true:

| Trigger | Threshold |
|---|---|
| Low retrieval confidence | best chunk similarity score < 0.45 |
| Sensitive topic detected | keywords like refund, legal, dispute, unauthorized charge |
| Repeated frustration | 3+ consecutive "Frustrated User" turns |

When escalation fires, the app shows the customer a hand-off message and
generates a structured JSON summary (persona, issue, retrieved sources,
confidence score, recommended action) intended for the human agent picking
up the conversation.

## Notes on the Knowledge Base

The sample `data/` folder ships with 4 starter articles covering billing,
API troubleshooting, account access, and password resets. For a stronger
demo, expand this to 10-20 articles covering more edge cases — retrieval
quality is directly limited by how much (and how well-written) your
knowledge base is.

## Tech Stack

- **LLM & Embeddings:** Google Gemini (`gemini-2.5-flash` for generation,
  `text-embedding-004` for embeddings)
- **Vector Store:** ChromaDB (local, persistent)
- **Chunking:** LangChain `RecursiveCharacterTextSplitter`
- **UI:** Streamlit

  ## Deployment Link
  https://persona-support-agent-5jjhyascuga93zb6b9ybhy.streamlit.app/
