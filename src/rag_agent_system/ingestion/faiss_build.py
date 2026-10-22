from typing import TYPE_CHECKING

import faiss
import numpy as np

from rag_agent_system.models import DocumentChunk

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

def build_flat_ip_index(
    chunks: list[DocumentChunk],
    encoder: "SentenceTransformer",
    *,
    batch_size: int = 64,
) -> "faiss.IndexFlatIP":
    if not chunks:
        raise ValueError("chunks must not be empty")
    if type(batch_size) is not int or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    max_input_tokens=encoder.max_seq_length
    texts=[]
    chunks_ids=[]
    for position,chunk in enumerate(chunks):
        chunk_id=chunk.chunk_id
        if chunk_id in chunks_ids:
            raise ValueError("Chunk id {} already exists".format(chunk_id))
        faiss_id = chunk.metadata.get("faiss_id")
        if type(faiss_id) is not int or faiss_id != position:
            raise ValueError("faiss_id must be an integer matching its position")
        chunks_ids.append(chunk_id)
        token_ids = encoder.tokenizer.encode(
            chunk.text,
            add_special_tokens=True,
            truncation=False,
        )
        if len(token_ids) > max_input_tokens:
            raise ValueError(
                f"{chunk_id}: embedding input has {len(token_ids)} tokens, "
                f"exceeding {max_input_tokens}"
            )

        texts.append(chunk.text)

    embeddings = encoder.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    expected_dimension = encoder.get_embedding_dimension()
    expected_shape = (len(chunks), expected_dimension)

    if embeddings.ndim != 2 or embeddings.shape != expected_shape:
        raise ValueError(
            f"Unexpected embedding shape: {embeddings.shape}, "
            f"expected {expected_shape}"
        )
    embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
    if not np.isfinite(embeddings).all():
        raise ValueError("NaN OR INFINITE!")
    norms=np.linalg.norm(embeddings,axis=1)
    if not np.allclose(norms, 1.0, atol=1e-5):
        raise ValueError("L2 Norm is not close to 1!")
    index = faiss.IndexFlatIP(expected_dimension)
    index.add(embeddings)
    return index
