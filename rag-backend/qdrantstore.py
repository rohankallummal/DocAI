from typing import List, Dict, Any
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class QdrantStorage:    
    def __init__(self, url: str, collection: str = None):
        self.client = QdrantClient(url)
        self.collection = collection
    
    def set_collection(self, collection_name: str) -> None:
        self.collection = collection_name
    
    def ensure_collection(self, dim: int) -> None:
        if not self.client.collection_exists(self.collection):
            print(f"Creating Qdrant collection '{self.collection}' ({dim} dims)...")
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            print(f"Collection '{self.collection}' created")
        else:
            print(f"Collection '{self.collection}' already exists")
    
    def upsert(
        self, 
        ids: List[str], 
        vectors: List[List[float]], 
        payloads: List[Dict[str, Any]], 
        batch_size: int = 100
    ) -> None:

        for i in tqdm(range(0, len(ids), batch_size), desc="Upserting to Qdrant"):
            batch_end = min(i + batch_size, len(ids))
            points = [
                PointStruct(
                    id=ids[j], 
                    vector=list(vectors[j]), 
                    payload=payloads[j]
                )
                for j in range(i, batch_end)
            ]
            self.client.upsert(collection_name=self.collection, points=points)
    
    def search(
        self, 
        query_vec: List[float], 
        top_k: int = 5
    ) -> Dict[str, Any]:
        
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vec,
            with_payload=True,
            limit=top_k,
        )
        
        contexts = []
        metadata = []
        
        for r in results.points:
            payload = getattr(r, "payload", {}) or {}
            if "text" in payload:
                contexts.append(payload["text"])
                metadata.append({
                    "source": payload.get("source", ""),
                    "page": payload.get("page", ""),
                    "score": getattr(r, "score", 0)
                })
        
        return {"contexts": contexts, "metadata": metadata}
    
    def delete_collection(self) -> None:
        if self.collection and self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
            print(f"Deleted collection '{self.collection}'")
    
    def list_collections(self) -> List[Dict[str, Any]]:
        collections = self.client.get_collections()
        collection_details = []
        
        for c in collections.collections:
            try:
                collection_info = self.client.get_collection(c.name)
                collection_details.append({
                    "name": c.name,
                    "vectors_count": collection_info.vectors_count,
                    "points_count": collection_info.points_count
                })
            except Exception as e:
                collection_details.append({
                    "name": c.name,
                    "error": str(e)
                })
        
        return collection_details