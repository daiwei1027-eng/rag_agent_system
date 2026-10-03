import pytest
import yaml

from rag_agent_system.config import load_config


@pytest.fixture
def valid_config():
    return {
        "project": {
            "name": "rag-agent-system",
            "log_level": "INFO",
        },
        "paths": {
            "faiss_index": "data/tinystories.faiss",
            "chunks": "data/tinystories_chunks.json",
        },
        "retrieval": {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "normalize_embeddings": True,
            "top_k": 20,
        },
        "generation": {
            "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
            "max_new_tokens": 256,
            "temperature": 0.2,
        },
        "reranker": {
            "enabled": True,
            "model_name": "cross-encoder/ms-marco-MiniLM-L6-v2",
            "top_k": 5,
            "max_length":512,
            "batch_size":8
        },
        "context": {
            "top_k": 5,
        },
    }

@pytest.fixture
def write_config(tmp_path):
    def write(raw):
        # 将字典写入 tmp_path 下的 YAML 文件。
        # 返回文件路径。
        path=tmp_path / "config.yaml"
        with path.open("w",encoding="utf-8") as f:
            yaml.safe_dump(raw, f)
        return path


    return write


def test_load_valid_config(valid_config, write_config):
    # Arrange：写入配置
    # Act：调用 load_config
    # Assert：检查读取结果
    path = write_config(valid_config)
    config=load_config(path)
    assert config.reranker.enabled is True, "reranker.enabled not match"
    assert config.reranker.model_name == "cross-encoder/ms-marco-MiniLM-L6-v2", "reranker.model_name not match"
    assert config.reranker.max_length == 512, "reranker.max_length not match"
    assert config.reranker.batch_size == 8, "reranker.batch_size not match"
    assert config.retrieval.top_k==20, "retrieval.top_k not match"
    assert config.reranker.top_k == 5, "reranker.top_k not match"
    assert config.context.top_k == 5, "context.top_k not match"

@pytest.mark.parametrize("value", [0, -1, "5", True])
def test_reject_invalid_reranker_top_k(
    valid_config, write_config, value
):
    valid_config["reranker"]["top_k"] = value
    path = write_config(valid_config)
    # 用 pytest.raises 验证异常。
    with pytest.raises(ValueError,match=r"reranker\.top_k"):
        load_config(path)


@pytest.mark.parametrize("value1", [False])
@pytest.mark.parametrize("value2", [""])
@pytest.mark.parametrize("value3", [1])
@pytest.mark.parametrize("value4", [5])
def test_disabled_reranker_allows_smaller_top_k(
    valid_config, write_config, value1, value2, value3, value4
):
    valid_config["reranker"]["enabled"] = value1
    valid_config["reranker"]["model_name"] = value2
    valid_config["reranker"]["top_k"] = value3
    valid_config["context"]["top_k"] = value4
    path = write_config(valid_config)
    config=load_config(path)
    assert config.reranker.enabled is False, "reranker.enabled not match"
    assert config.reranker.top_k == 1, "reranker.top_k not match"
    assert config.reranker.model_name == ""
    assert config.context.top_k == 5

@pytest.mark.parametrize("value1", [True])
@pytest.mark.parametrize("value2", [3])
@pytest.mark.parametrize("value3", [5])
def test_enabled_reranker_rejects_insufficient_top_k(
    valid_config, write_config, value1, value2, value3
):
    valid_config["reranker"]["enabled"] = value1
    valid_config["reranker"]["top_k"] = value2
    valid_config["context"]["top_k"] = value3
    path = write_config(valid_config)
    with pytest.raises(ValueError, match=r"context\.top_k"):
        load_config(path)