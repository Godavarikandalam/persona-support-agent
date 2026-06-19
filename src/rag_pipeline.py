"""
rag_pipeline.py
----------------
Everything related to turning raw support docs into searchable vectors,
and turning a user query into the top-k most relevant chunks.

Flow: ingest_directory() -> chunk -> embed -> store in ChromaDB
      retrieve_context()  -> embed query -> cosine similarity search -> top-k
"""

import os
import glob

import chromadb
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from . import config


class LocalRAGPipeline:
    def __init__(self, db_dir: str = config.CHROMA_DB_DIR):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.chroma_client.get_or_create_collection(
           name=config.COLLECTION_NAME,
           metadata={"hnsw:space": "cosine"}
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )

    # ---------- Embeddings ----------

    def get_embedding(self, text: str) -> list:
        """Call Gemini's embedding model and return the raw float vector."""
        response = self.client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values

    # ---------- Ingestion ----------

    def _read_file(self, path: str) -> str:
        """Read a single file (.txt, .md, or .pdf) and return its raw text."""
        if path.lower().endswith(".pdf"):
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        else:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    def ingest_document(self, doc_name: str, content: str) -> int:
        """Split a document into chunks, embed each, and store in Chroma.
        Returns the number of chunks ingested."""
        chunks = self.splitter.split_text(content)

        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            embedding = self.get_embedding(chunk)
            chunk_id = f"{doc_name}_chunk_{idx}"

            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{"source": doc_name, "chunk_index": idx}],
                documents=[chunk],
            )
        return len(chunks)

    def ingest_directory(self, data_dir: str = "data") -> dict:
        """Ingest every .txt, .md, and .pdf file found in data_dir.
        Returns a summary dict of {filename: chunk_count} for logging."""
        summary = {}
        patterns = ["*.txt", "*.md", "*.pdf"]
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(data_dir, pattern)))

        for path in sorted(files):
            doc_name = os.path.basename(path)
            content = self._read_file(path)
            count = self.ingest_document(doc_name, content)
            summary[doc_name] = count
            print(f"Ingested {doc_name}: {count} chunks")

        return summary

    # ---------- Retrieval ----------

    def retrieve_context(self, query: str, top_k: int = config.TOP_K) -> list:
        """Embed the query and run a cosine-similarity search against the
        indexed chunks. Returns a list of {text, source, score} dicts,
        ordered from most to least relevant."""
        query_vector = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        retrieved_items = []
        if results and results.get("documents"):
            for i in range(len(results["documents"][0])):
                distance = results["distances"][0][i] if results.get("distances") else 0.0
                retrieved_items.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    # Chroma's default space returns a distance; we convert
                    # it to a similarity-like score in [~0, 1] for thresholding.
                    "score": 1.0 - distance,
                })
        return retrieved_items


if __name__ == "__main__":
    # Quick standalone smoke test: run this file directly to (re)build the
    # index from /data and try a sample query before wiring up the rest
    # of the app. This is the "test bottom-up" step from the implementation plan.
    pipeline = LocalRAGPipeline()
    pipeline.ingest_directory("data")

    test_query = "How do I reset my password?"
    results = pipeline.retrieve_context(test_query)
    for r in results:
        print(f"[{r['score']:.3f}] ({r['source']}) {r['text'][:120]}...")
