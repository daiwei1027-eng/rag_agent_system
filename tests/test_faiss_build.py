"""Index contract checks with small fixed vectors, without model inference."""

import faiss
import numpy as np
import pytest

from rag_agent_system.ingestion.faiss_build import build_flat_ip_index
from rag_agent_system.models import DocumentChunk


class Tokenizer:
    def encode(self, text, *, add_special_tokens, truncation):
        assert add_special_tokens is True and truncation is False
        return list(range(len(text.split()) + 2))


class Encoder:
    max_seq_length = 6
    tokenizer = Tokenizer()

    def __init__(self, vectors=None):
        self.vectors = np.eye(3, dtype=np.float64) if vectors is None else vectors
        self.calls = []

    def get_embedding_dimension(self):
        return 3

    def encode(self, texts, **kwargs):
        self.calls.append((texts.copy(), kwargs))
        return self.vectors


def chunks():
    return [DocumentChunk(chunk_id=f"c{i}", text=text, source="sec", metadata={"faiss_id": i})
            for i, text in enumerate(["company year first", "second", "third"])]


def test_normalized_index_order_batch_flags_and_save_reload(tmp_path):
    # Noncontiguous float64 input exercises conversion before handing it to FAISS.
    encoder = Encoder(np.eye(3, dtype=np.float64)[:, ::-1])
    index = build_flat_ip_index(chunks(), encoder, batch_size=2)
    assert isinstance(index, faiss.IndexFlatIP)
    assert index.ntotal == 3 and index.d == 3
    assert encoder.calls == [(["company year first", "second", "third"],
                              {"batch_size": 2, "normalize_embeddings": True,
                               "convert_to_numpy": True})]
    restored_vectors = index.reconstruct_n(0, 3)
    assert restored_vectors.dtype == np.float32
    np.testing.assert_array_equal(restored_vectors, encoder.vectors)
    query = np.array([[0, 0, 1]], dtype=np.float32)
    scores, labels = index.search(query, 1)
    assert labels.tolist() == [[0]]
    np.testing.assert_allclose(scores, [[1]])
    path = tmp_path / "index.faiss"
    faiss.write_index(index, str(path))
    restored = faiss.read_index(str(path))
    np.testing.assert_array_equal(restored.reconstruct_n(0, 3), restored_vectors)
    disk_scores, disk_labels = restored.search(query, 3)
    memory_scores, memory_labels = index.search(query, 3)
    np.testing.assert_array_equal(disk_labels, memory_labels)
    np.testing.assert_array_equal(disk_scores, memory_scores)


@pytest.mark.parametrize("case", ["empty", "duplicate", "wrong-id", "boolean-id", "too-long"])
def test_invalid_chunks_fail_before_encoding(case):
    data = chunks()
    if case == "empty":
        data = []
    elif case == "duplicate":
        data[1] = DocumentChunk(chunk_id="c0", text="second", metadata={"faiss_id": 1})
    elif case == "wrong-id":
        data[1].metadata["faiss_id"] = 2
    elif case == "boolean-id":
        data[0].metadata["faiss_id"] = False
    else:
        data[2] = DocumentChunk(chunk_id="c2", text="one two three four five", metadata={"faiss_id": 2})
    encoder = Encoder()
    with pytest.raises(ValueError):
        build_flat_ip_index(data, encoder)
    assert not encoder.calls


@pytest.mark.parametrize("batch_size", [0, True, 1.5])
def test_invalid_batch_size(batch_size):
    encoder = Encoder()
    with pytest.raises(ValueError, match="batch_size"):
        build_flat_ip_index(chunks(), encoder, batch_size=batch_size)
    assert not encoder.calls


@pytest.mark.parametrize("vectors", [
    np.eye(2, 3),                 # wrong number of rows
    np.eye(3, 2),                 # wrong dimension
    np.ones((1, 3, 3)),           # wrong rank
    np.array([[np.nan, 0, 0], [0, 1, 0], [0, 0, 1]]),
    np.array([[np.inf, 0, 0], [0, 1, 0], [0, 0, 1]]),
    np.zeros((3, 3)),
    2 * np.eye(3),
], ids=["row-count", "dimension", "rank", "nan", "infinity", "zero", "not-normalized"])
def test_invalid_embedding_matrix(vectors):
    with pytest.raises(ValueError):
        build_flat_ip_index(chunks(), Encoder(vectors))


def test_input_exactly_at_embedding_limit_is_accepted():
    data = [DocumentChunk(chunk_id="c0", text="one two three four", metadata={"faiss_id": 0})]
    index = build_flat_ip_index(data, Encoder(np.array([[1, 0, 0]])))
    assert index.ntotal == 1
