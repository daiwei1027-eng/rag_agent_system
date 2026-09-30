"""Project path discovery and validation helpers."""

from pathlib import Path


def project_root() -> Path:
    """Return the repository root for an editable checkout."""

    return Path(__file__).resolve().parents[2]


def resolve_project_path(value: str | Path, root: Path | None = None) -> Path:
    """Resolve a configuration path relative to the repository root."""

    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((root or project_root()) / path).resolve()


def require_file(path: Path, *, label: str) -> Path:
    """Return an existing file or raise a message that explains the missing artifact."""

    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path

