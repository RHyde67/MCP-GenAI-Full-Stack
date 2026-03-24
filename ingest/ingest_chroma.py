import chromadb
from docx import Document
import glob
import os
import re

# -------- Sentence splitter --------
def sentence_split(text: str):
    # Basic, clean sentence-level splitting using regex
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Remove empties
    return [s.strip() for s in sentences if s.strip()]

# -------- Ingestion logic --------
def ingest_docx(root_dir="test_docs", vdb_path="vdb", collection_name="docs"):
    print("Looking in:", os.path.abspath(root_dir))
    client = chromadb.PersistentClient(path=vdb_path)
    collection = client.get_or_create_collection(collection_name)

    files = glob.glob(os.path.join(root_dir, "*.docx"))
    print(f"Found {len(files)} .docx files.")

    for file in files:
        filename = os.path.basename(file)
        print(f"Ingesting: {filename}")

        # Load doc and extract text
        doc = Document(file)
        full_text = "\n".join([p.text for p in doc.paragraphs])

        # Sentence-level chunks
        chunks = sentence_split(full_text)

        # Create unique IDs for each sentence-chunk
        ids = [f"{filename}-chunk-{i}" for i in range(len(chunks))]

        # Metadata (store filename for deletion/update)
        metadatas = [{"filename": filename} for _ in chunks]

        # Add to collection
        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        print(f"Added {len(chunks)} chunks for {filename}")

    print("Ingestion complete.")

if __name__ == "__main__":
        ingest_docx()