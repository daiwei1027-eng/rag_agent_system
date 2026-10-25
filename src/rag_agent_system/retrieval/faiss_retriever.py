"""Mode-based retrieval with the existing dense implementation and learning stubs."""

from pathlib import Path
from collections import Counter
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import normalize_embeddings
import math
from rag_agent_system.ingestion import load_chunks
from rag_agent_system.models import DocumentChunk, RetrievedChunk
from rag_agent_system.paths import require_file

class DocumentRetriever:
    def __init__(
        self,
        index_path: Path,
        chunks_path: Path,
        embedding_model: str,
        *,
        normalize_embeddings: bool,
        mode: str = "dense",
    ) -> None:
        if not isinstance(mode, str) or mode not in {"dense", "bm25", "hybrid"}:
            raise ValueError("mode must be dense, bm25 or hybrid")
        self.mode = mode
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.embedding_model = embedding_model
        self.normalize_embeddings = normalize_embeddings
        self._faiss_id_to_chunk_id: dict[int, str] | None = None
        self._index: faiss.Index | None = None
        self._chunks: dict[str, DocumentChunk] | None = None
        self._encoder: SentenceTransformer | None = None
        self._bm25_chunk_ids: list[str] = []
        self._bm25_term_frequencies: list[dict[str, int]] = []
        self._bm25_document_lengths: list[int] = []
        self._bm25_document_frequency: dict[str, int] = {}
        self._bm25_average_length: float = 0.0
        self._bm25_ready: bool = False

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
    def prepare(self) -> None:
        """Prepare the selected mode before timed evaluation queries."""
        self._load_resources()

    def _load_resources(self) -> None:
        """Compatibility entry point for existing dense evaluation scripts."""
        if self.mode == "dense":
            self._load_dense_resources()
            return
        if self.mode == "bm25":
            self._load_bm25_resources()
            return
        if self.mode == "hybrid":
            self._load_bm25_resources()
            self._load_dense_resources()
            return

    @staticmethod
    def _tokenize_bm25(text: str) -> list[str]:
        return text.lower().split()

    def _load_bm25_resources(self) -> None:
        if self._bm25_ready:
            return
        chunks_path = require_file(
            self.chunks_path, label="chunk store"
        )
        chunks = load_chunks(chunks_path)
        if not chunks:
            raise ValueError("Chunks are empty")
        chunk_ids = []
        term_frequencies = []
        document_lengths = []
        document_frequency = Counter()
        for chunk_id, chunk in chunks.items():
            tokens = self._tokenize_bm25(chunk.text)
            term_frequency = Counter(tokens)
            document_length=len(tokens)
            chunk_ids.append(chunk_id)
            term_frequencies.append(term_frequency)
            document_lengths.append(document_length)
            document_frequency.update(term_frequency.keys())
        average_length=sum(document_lengths)/len(document_lengths)
        if average_length ==0:
            raise ValueError("Tokenized chunks are empty")
        self._chunks = chunks
        self._bm25_chunk_ids = chunk_ids
        self._bm25_term_frequencies = term_frequencies
        self._bm25_document_lengths = document_lengths
        self._bm25_document_frequency = dict(document_frequency)
        self._bm25_average_length = average_length
        self._bm25_ready = True


    def _load_dense_resources(self) -> None:
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
        self._index = index
        self._chunks = chunks
        self._encoder = encoder
        self._faiss_id_to_chunk_id = id_mapping
    def retrieve(
            self,
            query: str,
            top_k: int = 3,
    ) -> list[RetrievedChunk]:
        """Validate common inputs and dispatch to the selected retrieval mode."""
        if not isinstance(query, str):
            raise ValueError("The query must be a string.")
        query = query.strip()
        if not query:
            raise ValueError("The query cannot be empty.")
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")
        if self.mode == "dense":
            return self._retrieve_dense(query, top_k)
        if self.mode == "bm25":
            return self._retrieve_bm25(query, top_k)
        return self._retrieve_hybrid(query, top_k)

    def _retrieve_dense(self, query: str, top_k: int) -> list[RetrievedChunk]:
        self._load_dense_resources()
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

    def _retrieve_bm25(self, query: str, top_k: int) -> list[RetrievedChunk]:
        self._load_bm25_resources()
        query_terms = sorted(set(self._tokenize_bm25(query)))
        if not query_terms:
            return []
        document_count = len(self._bm25_chunk_ids)
        scores = []
        k1=1.5
        b=0.75
        for position, chunk_id in enumerate(self._bm25_chunk_ids):
            term_frequency = self._bm25_term_frequencies[position]
            document_length = self._bm25_document_lengths[position]
            score = 0.0
            K_d = k1 * (
                    1 - b + b * document_length / self._bm25_average_length
            )

            for term in query_terms:
                tf = term_frequency.get(term, 0)
                if tf == 0:
                    continue

                df = self._bm25_document_frequency[term]
                idf = math.log(
                    1 + (document_count - df + 0.5) / (df + 0.5)
                )
                score+=idf*tf*(k1+1)/(tf+K_d)
            if score > 0:
                scores.append((chunk_id, score))
        scores.sort(key=lambda item: (-item[1], item[0]))
        results = []
        for rank, (chunk_id, score) in enumerate(scores[:top_k], start=1):
            results.append(
                RetrievedChunk(
                    chunk=self._chunks[chunk_id],
                    score=float(score),
                    rank=rank,
                )
            )

        return results

    def _retrieve_hybrid(
            self, query: str, top_k: int
    ) -> list[RetrievedChunk]:
        dense_results = self._retrieve_dense(query, top_k=top_k)
        bm25_results = self._retrieve_bm25(query, top_k=top_k)

        c = 60
        fused_scores: dict[str, float] = {}
        chunks_by_id: dict[str, DocumentChunk] = {}

        for candidates in (dense_results, bm25_results):
            for rank, result in enumerate(candidates, start=1):
                chunk_id = result.chunk.chunk_id
                chunks_by_id[chunk_id] = result.chunk
                fused_scores[chunk_id] = (
                        fused_scores.get(chunk_id, 0.0) + 1 / (rank + c)
                )
        ranked_scores = sorted(
            fused_scores.items(),
            key=lambda item: (-item[1], item[0]),
        )
        results = []
        for rank, (chunk_id, score) in enumerate(ranked_scores[:top_k], start=1):
            results.append(
                RetrievedChunk(
                    chunk=chunks_by_id[chunk_id],
                    score=float(score),
                    rank=rank,
                )
            )

        return results


FaissRetriever = DocumentRetriever
