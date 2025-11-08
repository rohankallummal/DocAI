import uuid
from io import BytesIO
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from pypdf import PdfReader
from huggingface_hub import InferenceClient
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    HF_TOKEN,
    SMALL_EMBED_MODEL,
    LARGE_EMBED_MODEL,
    LLM_MODEL,
    SMALL_MODEL_CHUNK_THRESHOLD,
    SMALL_MODEL_DIM,
    LARGE_MODEL_DIM,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    MAX_TOKENS,
    CACHE_DIR,
    QDRANT_URL,
)
from embedding_cache import EmbeddingCache
from qdrantstore import QdrantStorage


class RAGPipeline:    
    def __init__(self):
        self.embed_cache = EmbeddingCache(CACHE_DIR)
        self.qdrant = QdrantStorage(QDRANT_URL)
        self.embed_client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
        self.llm_client = InferenceClient(api_key=HF_TOKEN)
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=CHUNK_SEPARATORS
        )
        
        self.current_collection = None
        self.current_embed_model = None
        self.current_embed_dim = None
    
    def select_model(self, num_chunks: int) -> Tuple[str, int]:
        if num_chunks < SMALL_MODEL_CHUNK_THRESHOLD:
            print(f"Using small embedding model - ({SMALL_MODEL_DIM} dims)")
            return SMALL_EMBED_MODEL, SMALL_MODEL_DIM
        
        print(f"Using large embedding model - ({LARGE_MODEL_DIM} dims)")
        return LARGE_EMBED_MODEL, LARGE_MODEL_DIM
    
    def load_pdf_from_bytes(
        self, 
        pdf_bytes: bytes, 
        filename: str
    ) -> List[Dict[str, Any]]:
        
        reader = PdfReader(BytesIO(pdf_bytes))
        chunks = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                page_chunks = self.splitter.split_text(text)
                for chunk in page_chunks:
                    chunks.append({
                        "text": chunk,
                        "metadata": {
                            "source": filename,
                            "page": i + 1
                        }
                    })
        
        print(f"Split {filename} into {len(chunks)} chunks")
        return chunks
    
    def _normalize_embedding(self, raw: Any) -> List[float]:
        if isinstance(raw, list) and len(raw) and isinstance(raw[0], list):
            raw = raw[0]
        
        return list(raw)
    
    def get_embedding(
        self, 
        text: str, 
        model_name: str = None
    ) -> List[float]:

        model = model_name or self.current_embed_model or LARGE_EMBED_MODEL
        cache_key = f"{model}_____{text}"
        
        cached = self.embed_cache.get(cache_key)
        if cached:
            return cached
        
        raw = self.embed_client.feature_extraction(text, model=model)
        embedding = self._normalize_embedding(raw)
        
        self.embed_cache.set(cache_key, embedding)
        
        return embedding
    
    def ingest_pdf(
        self, 
        pdf_bytes: bytes, 
        filename: str
    ) -> Tuple[int, str, str]:

        chunks = self.load_pdf_from_bytes(pdf_bytes, filename)
        
        if not chunks:
            raise RuntimeError("No text found in PDF")
        
        if self.current_collection:
            print(f"Deleting old collection: {self.current_collection}")
            self.qdrant.delete_collection()

        embed_model, embed_dim = self.select_model(len(chunks))

        collection_name = f"rag_docs_{embed_dim}_{uuid.uuid4().hex[:8]}"
        self.qdrant.set_collection(collection_name)
        self.qdrant.ensure_collection(embed_dim)
        
        self.current_collection = collection_name
        self.current_embed_model = embed_model
        self.current_embed_dim = embed_dim

        texts = [c["text"] for c in chunks]
        embeddings = [
            self.get_embedding(t, embed_model) 
            for t in tqdm(texts, desc="🔹 Generating embeddings")
        ]

        ids = [str(uuid.uuid4()) for _ in chunks]
        payloads = [{"text": c["text"], **c["metadata"]} for c in chunks]

        self.qdrant.upsert(ids, embeddings, payloads)
        
        print(f"Ingested {len(chunks)} chunks into '{collection_name}'")
        return len(chunks), embed_model, collection_name
    
    def query(
        self, 
        question: str, 
        top_k: int = 5
    ) -> Dict[str, Any]:

        if not self.current_collection:
            return {
                "answer": "No document indexed yet. Upload a PDF first.",
                "sources": []
            }
        
        query_vec = self.get_embedding(question, self.current_embed_model)
        
        results = self.qdrant.search(query_vec, top_k)
        
        if not results["contexts"]:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }
        
        context_text = "\n\n".join(results["contexts"])

        answer = self._generate_answer(question, context_text)

        sources = list({
            m.get("source", "") 
            for m in results["metadata"] 
            if m.get("source")
        })
        
        return {
            "answer": answer,
            "sources": sources,
            "num_contexts": len(results["contexts"])
        }
    
    def _generate_answer(self, question: str, context: str) -> str:

        system_message = """
You are an expert in your respective field who answer questions based of the uploaded document.

RULES:
- You must use the information present in the provided context.
- Answer only the specific question asked. Do not include related information that does not directly help answer the user's question.
- Do not just quote the text. Paraphrase while remaining 100 percent factual to the context.
- If the context does not contain the information needed to answer the question, you must state: "I cannot find sufficient information in the document to answer this question."
- All answers must be written in clear, coherent, and well-structured paragraphs.
- No using special characters for Demarcation (e.g - heading, horizontal rules, ..., etc)
- Your tone must be objective and neutral.
"""
        
        user_message = f"""
CONTEXT:
{context}

QUESTION:
{question}
"""
        
        try:
            completion = self.llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=MAX_TOKENS,
            )
            
            message = completion.choices[0].message
            answer = getattr(message, "content", str(message))
            return answer.strip()
            
        except Exception as e:
            print(f"Failed to generate answer: {e}")
            return "Error generating answer from LLM"
    
    def reset(self) -> None:
        if self.current_collection:
            self.qdrant.delete_collection()
        
        self.current_collection = None
        self.current_embed_model = None
        self.current_embed_dim = None