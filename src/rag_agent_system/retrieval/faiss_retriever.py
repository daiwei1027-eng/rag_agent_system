"""FAISS-backed retrieval contract for the Day 18 exercise."""

from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from rag_agent_system.ingestion import load_chunks
from rag_agent_system.models import DocumentChunk, RetrievedChunk
from rag_agent_system.paths import require_file

class FaissRetriever:
    def __init__(
        self,
        index_path: Path,
        chunks_path: Path,
        embedding_model: str,
        *,
        normalize_embeddings: bool,
    ) -> None:
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.embedding_model = embedding_model
        self.normalize_embeddings = normalize_embeddings
        self._faiss_id_to_chunk_id: dict[int, str] | None = None
        self._index: faiss.Index | None = None
        self._chunks: dict[str, DocumentChunk] | None = None
        self._encoder: SentenceTransformer | None = None

    @staticmethod
    def _build_id_mapping(
            chunks: dict[str, DocumentChunk],
    ) -> dict[int, str]:
        """Build the mapping from FAISS labels to chunk IDs."""

        mapping: dict[int, str] = {}

        for chunk_id, chunk in chunks.items():
            faiss_id = chunk.metadata.get("faiss_id")

            if type(faiss_id) is not int:
                raise ValueError(
                    f"Invalid faiss_id for chunk {chunk_id}"
                )

            if faiss_id in mapping:
                raise ValueError(
                    f"Duplicate faiss_id: {faiss_id}"
                )

            mapping[faiss_id] = chunk_id

        return mapping
    def _load_resources(self) -> None:
        """Load and validate the index, chunks, and encoder once."""
        if (
            self._index is not None
            and self._chunks is not None
            and self._encoder is not None
            and self._faiss_id_to_chunk_id is not None
        ):
            return

        index_path = require_file(
            self.index_path, label="FAISS index"
        )
        chunks_path = require_file(
            self.chunks_path, label="chunk store"
        )

        index = faiss.read_index(str(index_path))
        chunks = load_chunks(chunks_path)
        id_mapping = self._build_id_mapping(chunks)
        if index.ntotal == 0:
            raise ValueError("FAISS index is empty.")

        if index.ntotal != len(chunks):
            raise ValueError(
                f"Count mismatch: vectors={index.ntotal}, "
                f"chunks={len(chunks)}"
            )
        expected_ids = set(range(index.ntotal))

        if set(id_mapping) != expected_ids:
            raise ValueError(
                "FAISS ID mapping must cover every index position."
            )
        encoder = SentenceTransformer(self.embedding_model)

        if encoder.get_embedding_dimension() != index.d:
            raise ValueError(
                "Encoder dimension does not match FAISS index."
            )

        # 全部成功后才保存，避免对象留下半加载状态。
        self._index = index
        self._chunks = chunks
        self._encoder = encoder
        self._faiss_id_to_chunk_id = id_mapping
    def retrieve(
            self,
            query: str,
            top_k: int = 3,
    ) -> list[RetrievedChunk]:
        """Return chunks ranked by vector relevance."""
        if not isinstance(query, str):
            raise ValueError("The query must be a string.")
        query = query.strip()
        if not query:
            raise ValueError("The query cannot be empty.")
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")
        self._load_resources()
        ## Resources are loaded and cached for reuse.Then use encoder to process [query] with L2NORM,then turn it into float32,finally use faiss to search similarity
        index = self._index
        chunks = self._chunks
        encoder = self._encoder
        id_mapping = self._faiss_id_to_chunk_id
        embedded_query=encoder.encode([query],normalize_embeddings=self.normalize_embeddings,convert_to_numpy=True)
        embedded_query = np.ascontiguousarray(
            embedded_query,
            dtype=np.float32,
        )
        if embedded_query.shape != (1, index.d):
            raise ValueError("Unexpected query embedding shape.")

        search_k = min(top_k, index.ntotal)
        scores,faiss_id=index.search(embedded_query, search_k)
        results: list[RetrievedChunk] = []
        for score,faiss_id in zip(scores[0], faiss_id[0]):
            faiss_id=int(faiss_id)
            chunk_id=id_mapping[int(faiss_id)]
            chunk = chunks[chunk_id]
            each_RetrievedChunk = RetrievedChunk(chunk=chunk,score=float(score),rank=len(results)+1)
            results.append(each_RetrievedChunk)
        return results