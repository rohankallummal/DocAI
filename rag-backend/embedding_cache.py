import hashlib
import pickle
from pathlib import Path
from typing import List, Optional


class EmbeddingCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        path = self.cache_dir / f"{self._key(text)}.pkl"
        if path.exists():
            try:
                with open(path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Failed to load cached embedding: {e}")
                return None
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        path = self.cache_dir / f"{self._key(text)}.pkl"
        try:
            with open(path, "wb") as f:
                pickle.dump(embedding, f)
        except Exception as e:
            print(f"Failed to cache embedding: {e}")
    
    def clear(self) -> None:
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"Failed to delete cache file {cache_file}: {e}")