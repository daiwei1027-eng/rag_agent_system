"""Dataset identifiers shared by request routing, prompts and tool schemas."""

from pathlib import Path
from typing import Literal


DatasetName = Literal["tinystories", "sec"]

DATASET_CONFIG_PATHS: dict[DatasetName, Path] = {
    "tinystories": Path("configs/chunking_v2.yaml"),
    "sec": Path("configs/SEC_v1.yaml"),
}


def get_dataset_config_path(dataset: DatasetName) -> Path:

    if dataset in DATASET_CONFIG_PATHS:
        return DATASET_CONFIG_PATHS[dataset]
    else:
        raise ValueError("Unknown dataset")